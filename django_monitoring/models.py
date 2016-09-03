# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from dateutil import relativedelta
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields.json import JSONField
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel

from .monitoring import monitor
from .querysets import CheckQuerySet


class AlreadyAcknowledged(Exception):
    pass


@python_2_unicode_compatible
class Check(TimeStampedModel):
    STATUS = Choices((0, 'unknown', _('Unknown')),
                     (1, 'ok', _('OK')),
                     (2, 'warning', _('Warning')),
                     (3, 'danger', _('Critical')))

    slug = models.TextField(verbose_name=_('Module slug'))
    identifier = models.CharField(max_length=256, verbose_name=_('Identifier'))

    status = models.IntegerField(choices=STATUS,
                                 default=STATUS.unknown, verbose_name=_('Status'))
    config = JSONField(blank=True, verbose_name=_('Configuration'))

    payload_description = models.TextField(verbose_name=_('Payload description'))

    acknowledged_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True,
                                        verbose_name=_('Acknowledged by'),
                                        related_name='acknowledged_by')
    acknowledged_at = models.DateTimeField(null=True, verbose_name=_('Acknowledged at'))
    acknowledged_until = models.DateTimeField(null=True, verbose_name=_('Acknowledged until'))
    acknowledged_reason = models.TextField(blank=True, verbose_name=_('Acknowledge reason'))

    assigned_to_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True,
                                         related_name='assigned_to_user')
    assigned_to_group = models.ForeignKey(to='auth.Group', null=True)

    objects = CheckQuerySet.as_manager()

    class Meta:
        unique_together = ('slug', 'identifier')

    def acknowledge(self, user, days, reason=None, commit=True):
        if self.status in (self.STATUS.warning, self.STATUS.danger) and self.is_acknowledged():
            raise AlreadyAcknowledged()
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.acknowledged_until = timezone.now() + relativedelta.relativedelta(days=days)
        self.acknowledged_reason = reason or ''
        if commit:
            self.save(update_fields=['acknowledged_at', 'acknowledged_by', 'acknowledged_until', 'acknowledged_reason'])

    def is_acknowledged(self):
        return self.acknowledged_until and self.acknowledged_until >= timezone.now()

    def __str__(self):
        return self.slug

    def get_check_instance(self):
        return monitor.get_check_class(self.slug)()

    def get_payload(self):
        return self.get_check_instance().get_payload(self.identifier)
