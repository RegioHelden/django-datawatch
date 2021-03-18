# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from dateutil import relativedelta
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields.json import JSONField
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel

from django_datawatch.querysets import CheckExecutionQuerySet
from .datawatch import datawatch
from .querysets import ResultQuerySet


class AlreadyAcknowledged(Exception):
    pass


class Result(TimeStampedModel):
    STATUS = Choices((0, 'unknown', _('Unknown')),
                     (1, 'ok', _('OK')),
                     (2, 'warning', _('Warning')),
                     (3, 'critical', _('Critical')))

    slug = models.TextField(verbose_name=_('Module slug'))
    identifier = models.CharField(max_length=256, verbose_name=_('Identifier'))

    status = models.IntegerField(choices=STATUS,
                                 default=STATUS.unknown, verbose_name=_('Status'))
    data = JSONField(blank=True, default=dict, verbose_name=('Data'))
    config = JSONField(blank=True, default=dict, verbose_name=_('Configuration'))

    payload_description = models.TextField(verbose_name=_('Payload description'))

    acknowledged_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True,
                                        verbose_name=_('Acknowledged by'),
                                        related_name='acknowledged_by', on_delete=models.CASCADE)
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Acknowledged at'))
    acknowledged_until = models.DateTimeField(null=True, blank=True, verbose_name=_('Acknowledged until'))
    acknowledged_reason = models.TextField(blank=True, verbose_name=_('Acknowledge reason'))

    assigned_to_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True,
                                         related_name='assigned_to_user', on_delete=models.SET_NULL)
    assigned_to_group = models.ForeignKey(to='auth.Group', null=True, blank=True, on_delete=models.SET_NULL)

    objects = ResultQuerySet.as_manager()

    class Meta:
        unique_together = ('slug', 'identifier')
        permissions = (('view', 'Can view results dashboard and details'), ('acknowledge', 'Can acknowledge results'),
                       ('config', 'Can change the configuration for results'), ('refresh', 'Can refresh results'))

    def acknowledge(self, user, days, reason=None, commit=True):
        # calculate end of requested acknowledgement
        acknowledged_until = timezone.now() + relativedelta.relativedelta(days=days)

        # check that we're not accidentally overriding the current setup
        if self.status in (self.STATUS.warning, self.STATUS.critical):
            if self.is_acknowledged() and self.acknowledged_until > acknowledged_until:
                raise AlreadyAcknowledged()
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.acknowledged_until = acknowledged_until
        self.acknowledged_reason = reason or ''
        if commit:
            self.save(update_fields=['acknowledged_at', 'acknowledged_by', 'acknowledged_until', 'acknowledged_reason'])

    def is_acknowledged(self):
        return self.acknowledged_until and self.acknowledged_until >= timezone.now()

    def __str__(self):
        return self.slug

    def get_check_instance(self):
        return datawatch.get_check_class(self.slug)()

    def get_payload(self):
        return self.get_check_instance().get_payload(self.identifier)

    def get_formatted_data(self):
        return datawatch.get_check_class(self.slug)().format_result_data(self)


class CheckExecution(models.Model):
    slug = models.TextField(verbose_name=_('Check module slug'), unique=True)
    last_run = models.DateTimeField(verbose_name=_('Last run'))

    objects = CheckExecutionQuerySet.as_manager()

    def __str__(self):
        return '%s on %s' % (self.slug, self.last_run)
