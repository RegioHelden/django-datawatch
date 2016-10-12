# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import logging

from django import forms

from django_datawatch.models import Result
from django_datawatch.monitoring import monitor, make_model_uid

logger = logging.getLogger(__name__)


class DatawatchCheckSkipException(Exception):
    pass


class BaseCheckForm(forms.Form):
    def save(self, instance):
        instance.config = self.cleaned_data
        instance.save(update_fields=['config'])
        return instance


class CheckResponse(object):
    def __init__(self):
        super(CheckResponse, self).__setattr__('_datastore', {})
        super(CheckResponse, self).__setattr__('_status', Result.STATUS.unknown)

    def __setattr__(self, name, value):
        self._datastore[name] = value

    def __getattr__(self, name):
        if name not in self._datastore:
            return None
        return self._datastore[name]

    def get_data(self):
        return self._datastore

    def set_status(self, status):
        super(CheckResponse, self).__setattr__('_status', status)

    def get_status(self):
        return self._status


class BaseCheck(object):
    """
    Any check should inherits from `BaseCheck` and should implements `.generate(self)`
    and `.check(self, payload)` methods.

    Optionally, you can implements `.get_assigned_user(self, payload)` (resp. `.get_assigned_group(self, payload)`)
    to define to which user (resp. group) the system had to assign the check result.
    """

    config_form = None
    title = ''
    max_acknowledge = None
    run_every = None
    trigger_update = dict()

    def __init__(self):
        self.slug = monitor.get_slug(self.__module__, self.__class__.__name__)

    def run(self):
        monitor.get_backend().enqueue(slug=self.slug)

    def handle(self, payload):
        # get old result
        old_status = None
        result = Result.objects.filter(slug=self.slug, identifier=self.get_identifier(payload)).first()
        if result:
            old_status = result.status

        # run check
        try:
            response = self.check(payload)
        except DatawatchCheckSkipException:
            if result:
                result.delete()
            return

        # save check result
        status = response.get_status()
        unacknowledge = old_status in [Result.STATUS.warning, Result.STATUS.critical] and status == Result.STATUS.ok
        self.save(payload=payload, status=status, data=response.get_data(), unacknowledge=unacknowledge)

    def get_config(self, payload):
        try:
            check_result = Result.objects.get(slug=self.slug, identifier=self.get_identifier(payload))

            # check has a configuration
            if check_result.config:
                return check_result.config
        except Result.DoesNotExist:
            pass

        # get default config from form initial values
        form = self.get_form_class()()
        return {name: field.initial for name, field in form.fields.items()}

    def get_form(self, payload):
        return self.get_form_class()(**self.get_config(payload))

    def get_form_class(self):
        return self.config_form

    def save(self, payload, status, data=None, unacknowledge=False):
        # build default data
        defaults = dict(status=status, data=data, assigned_to_user=self.get_assigned_user(payload, status),
                        assigned_to_group=self.get_assigned_group(payload, status),
                        payload_description=self.get_payload_description(payload))
        if unacknowledge:
            defaults.update(dict(acknowledge_by=None, acknowledge_at=None, acknowledge_until=None))

        # save the check
        dataset, created = Result.objects.update_or_create(
            slug=self.slug, identifier=self.get_identifier(payload),
            defaults=defaults)
        return dataset

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

    def format_result_data(self, result):
        return ''

    def get_assigned_user(self, payload, result):
        return None

    def get_assigned_group(self, payload, result):
        return None

    def get_context_data(self, result):
        return dict()

    def get_title(self):
        return self.title

    def get_template_name(self):
        if hasattr(self, 'template_name'):
            return self.template_name
        return None

    def get_max_acknowledge(self):
        return self.max_acknowledge

    def get_trigger_update_uid_map(self):
        mapping = {}
        for method_name, model in self.trigger_update.items():
            mapping[make_model_uid(model)] = 'get_%s_payload' % method_name
        return mapping
