# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import logging

from django import forms

from django_datawatch.settings import ddw_settings
from django_datawatch.tasks import django_datawatch_enqueue
from django_datawatch.models import Check
from django_datawatch.monitoring import monitor

logger = logging.getLogger(__name__)


class BaseCheckForm(forms.Form):
    def save(self, instance):
        instance.config = self.cleaned_data
        instance.save(update_fields=['config'])
        return instance


class BaseCheck(object):

    """
    Any check should inherits from `BaseCheck` and should implements `.generate(self)`
    and `.check(self, payload)` methods.

    Optionally, you can implements `.get_assigned_user(self, payload)` (resp. `.get_assigned_group(self, payload)`)
    to define to which user (resp. group) the system had to assign the check result.
    """

    config_form = None
    title = ''

    def __init__(self):
        self.slug = monitor.get_slug(self.__module__, self.__class__.__name__)

    def run(self):
        django_datawatch_enqueue.apply_async(kwargs=dict(check_slug=self.slug), queue=ddw_settings.QUEUE_NAME)

    def handle(self, payload):
        # check result
        try:
            old_status = Check.objects.get(slug=self.slug, identifier=self.get_identifier(payload)).status
        except Check.DoesNotExist:
            old_status = None
        status = self.check(payload)
        unacknowledge = old_status in [Check.STATUS.warning, Check.STATUS.danger] and status == Check.STATUS.ok
        self.save(payload, status, unacknowledge=unacknowledge)

    def get_config(self, payload):
        try:
            check_result = Check.objects.get(slug=self.slug, identifier=self.get_identifier(payload))

            # check has a configuration
            if check_result.config:
                return check_result.config
        except Check.DoesNotExist:
            pass

        # get default config from form initial values
        form = self.get_form_class()()
        return {name: field.initial for name, field in form.fields.items()}

    def get_form(self, payload):
        return self.get_form_class()(**self.get_config(payload))

    def get_form_class(self):
        return self.config_form

    def save(self, payload, result, unacknowledge=False):
        defaults = {
            'status': result,
            'assigned_to_user': self.get_assigned_user(payload, result),
            'assigned_to_group': self.get_assigned_group(payload, result),
            'payload_description': self.get_payload_description(payload)
        }

        # save the check
        dataset, created = Check.objects.get_or_create(
            slug=self.slug, identifier=self.get_identifier(payload),
            defaults=defaults)

        # update existing dataset
        if not created:
            for (key, value) in defaults.items():
                setattr(dataset, key, value)
            if unacknowledge:
                dataset.acknowledge_by = None
                dataset.acknowledge_at = None
                dataset.acknowledge_until = None
            dataset.save()

    def generate(self):
        """
        yield items to run check for
        """
        raise NotImplementedError(".generate() should be overridden")

    def check(self, payload):
        """
        :param payload: the payload to run the check for
        :return:
        """
        raise NotImplementedError(".check() should be overridden")

    def get_identifier(self, payload):
        raise NotImplementedError(".get_identifier() should be overridden")

    def get_payload_description(self, payload):
        return str(payload)

    def get_assigned_user(self, payload, result):
        return None

    def get_assigned_group(self, payload, result):
        return None

    def get_context_data(self, payload):
        return dict()

    def get_title(self):
        return self.title

    def get_template_name(self):
        if hasattr(self, 'template_name'):
            return self.template_name
        return None
