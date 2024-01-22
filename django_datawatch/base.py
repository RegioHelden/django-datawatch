import logging
from contextlib import contextmanager
from typing import Optional, List

from django import forms
from django.contrib.auth.models import AbstractUser, Group
from django.db import transaction
from django.utils import timezone

from django_datawatch.models import Result, CheckExecution, ResultStatusHistory
from django_datawatch.datawatch import datawatch, make_model_uid

logger = logging.getLogger(__name__)


@contextmanager
def track_status_history(slug, identifier, new_status):
    result = Result.objects.filter(slug=slug, identifier=identifier).only('id', 'status').first()
    current_status = getattr(result, 'status', None)
    yield
    if current_status != new_status:
        if result is None:
            result = Result.objects.only('id').get(slug=slug, identifier=identifier)
        ResultStatusHistory.objects.create(from_status=current_status, to_status=new_status, result_id=result.id)


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

    Optionally, you can implements `.get_assigned_users(self, payload)` (resp. `.get_assigned_groups(self, payload)`)
    to define to which user(s) (resp. group(s)) the system had to assign the check result.
    """

    config_form = None
    title = ''
    max_acknowledge = None
    run_every = None
    trigger_update = dict()
    model_class = None

    def __init__(self):
        self.slug = datawatch.get_slug(self.__module__, self.__class__.__name__)

    def user_forced_refresh_hook(self, payload):
        """
        gets only executed when the refresh has been forced by a user
        from the web view
        """
        pass

    def run(self):
        datawatch.get_backend().enqueue(slug=self.slug)
        CheckExecution.objects.update_or_create(slug=self.slug, defaults=dict(
            last_run=timezone.now()))

    def refresh(self):
        datawatch.get_backend().refresh(slug=self.slug)

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
        defaults = dict(status=status, data=data, payload_description=self.get_payload_description(payload))

        if unacknowledge:
            defaults.update(dict(acknowledged_by=None, acknowledged_at=None, acknowledged_until=None))

        with transaction.atomic():
            with track_status_history(self.slug, self.get_identifier(payload), status):
                # save the check
                dataset, created = Result.objects.update_or_create(
                    slug=self.slug, identifier=self.get_identifier(payload),
                    defaults=defaults)

                # set assigned users and groups
                if groups := self.get_assigned_groups(payload, status):
                    dataset.assigned_groups.set(groups)
                else:
                    dataset.assigned_groups.clear()

                if users := self.get_assigned_users(payload, status):
                    dataset.assigned_users.set(users)
                else:
                    dataset.assigned_users.clear()

        return dataset

    def get_trigger_update_uid_map(self):
        mapping = {}
        for method_name, model in self.trigger_update.items():
            mapping[make_model_uid(model)] = 'get_%s_payload' % method_name
        return mapping

    def generate(self):
        """
        yield items to run check for
        """
        raise NotImplementedError(".generate() must be overridden")

    def check(self, payload):
        """
        :param payload: the payload to run the check for
        :return:
        """
        raise NotImplementedError(".check() must be overridden")

    def get_identifier(self, payload):
        return payload.pk

    def get_payload(self, identifier):
        return self.model_class.objects.get(pk=identifier)

    def register(self, check_class):
        pass

    def get_payload_description(self, payload):
        return str(payload)

    def format_result_data(self, result):
        return ''

    def get_assigned_users(self, payload, result) -> Optional[List[AbstractUser]]:
        return None

    def get_assigned_groups(self, payload, result) -> Optional[List[Group]]:
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
