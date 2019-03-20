# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import importlib
import logging

from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone
from django.db.models import signals
from django.utils.module_loading import autodiscover_modules

from django_datawatch.defaults import defaults

logger = logging.getLogger(__name__)


class DatawatchHandler(object):
    def __init__(self):
        self._registered_checks = {}
        self._related_models = dict()
        self._backend = None

    def autodiscover_checks(self, module_name='checks'):
        autodiscover_modules(module_name)

    def register(self, check_class):
        slug = self.get_slug(check_class.__module__, check_class.__name__)
        self._registered_checks[slug] = check_class
        check = check_class()

        # register delete
        if check.model_class is not None:
            signals.post_delete.connect(delete_results,
                                        sender=check.model_class,
                                        dispatch_uid='django_datawatch')

        # register update
        if check.trigger_update is not None:
            for keyword, model in check.trigger_update.items():
                method_name = 'get_%s_payload' % keyword
                if not hasattr(check, method_name):
                    logger.warning(
                        'Update trigger "%s" defined without .%s()',
                        keyword, method_name)
                    continue

                model_uid = make_model_uid(model)
                datawatch._related_models.setdefault(model_uid, list())
                if check_class not in datawatch._related_models[model_uid]:
                    signals.post_save.connect(run_checks, sender=model,
                                              dispatch_uid='django_datawatch')
                    datawatch._related_models[model_uid].append(check_class)

        return check_class

    def get_all_registered_checks(self):
        return self._registered_checks.values()

    def get_all_registered_check_slugs(self):
        return self._registered_checks.keys()

    def get_check_class(self, slug):
        if slug in self._registered_checks:
            return self._registered_checks[slug]
        return None

    def get_checks_for_related_model(self, model):
        model_uid = make_model_uid(model)
        if model_uid in self._related_models:
            return self._related_models[model_uid]
        return None

    def get_checks_for_model(self, model):
        check_classes = list()
        for check_class in datawatch.get_all_registered_checks():
            if check_class.model_class == model:
                check_classes.append(check_class)
        return check_classes

    def get_slug(self, module, class_name):
        return u'{}.{}'.format(module, class_name)

    def get_backend(self):
        if self._backend is None:
            backend_module = importlib.import_module(
                getattr(settings, 'DJANGO_DATAWATCH_BACKEND',
                        defaults['BACKEND']))
            self._backend = backend_module.Backend()
        return self._backend

    def delete_results(self, sender, instance):
        from django_datawatch.models import Result
        for check_class in datawatch.get_checks_for_model(model=sender):
            check = check_class()
            identifier = check.get_identifier(instance)
            Result.objects.filter(slug=check.slug, identifier=identifier).delete()

    def update_related(self, sender, instance):
        checks = datawatch.get_checks_for_related_model(sender) or []
        for check_class in checks:
            check = check_class()
            backend = datawatch.get_backend()
            model_uid = make_model_uid(instance.__class__)
            mapping = check.get_trigger_update_uid_map()

            if model_uid not in mapping:
                return

            if not hasattr(check, mapping[model_uid]):
                return

            payload = getattr(check, mapping[model_uid])(instance)
            if not payload:
                return

            backend.run(slug=check.slug, identifier=check.get_identifier(payload),
                        run_async=True)


datawatch = DatawatchHandler()


class Scheduler(object):
    def run_checks(self, force=False, slug=None):
        """
        :param force: <bool> force all registered checks to be executed
        :return:
        """
        checks = datawatch.get_all_registered_checks()
        last_executions = self.get_last_executions()

        for check_class in checks:
            check = check_class()

            # only update a single slug if requested
            if slug and check.slug != slug:
                continue

            # check is not meant to be run periodically
            if check_class.run_every is None:
                continue

            # schedule defined in an invalid format
            if not isinstance(check_class.run_every, crontab):
                logger.warning('run_every must be an instance of crontab')
                continue

            # shall the check be run again?
            if not force and check.slug in last_executions:
                last_execution = last_executions[check.slug]
                if timezone.is_aware(last_execution):
                    last_execution = last_execution.astimezone(timezone.get_current_timezone())
                if not check_class.run_every.is_due(last_run_at=last_execution).is_due:
                    continue

            # enqueue the check and save execution state
            check.run()

    def get_last_executions(self):
        from django_datawatch.models import CheckExecution
        return dict([(obj.slug, obj.last_run)
                     for obj in CheckExecution.objects.all()])


def make_model_uid(model):
    """
    Returns an uid that will identify the given model class.

    :param model: model class
    :return: uid (string)
    """
    return "%s.%s" % (model._meta.app_label, model.__name__)


def delete_results(sender, instance, using, **kwargs):
    if not getattr(settings, 'DJANGO_DATAWATCH_RUN_SIGNALS',
                   defaults['RUN_SIGNALS']):
        return
    datawatch.delete_results(sender, instance)


def run_checks(sender, instance, created, raw, using, **kwargs):
    """
    Re-execute checks related to the given sender model, only for the
    updated instance.

    :param sender: model
    :param kwargs:
    """
    if not getattr(settings, 'DJANGO_DATAWATCH_RUN_SIGNALS',
                   defaults['RUN_SIGNALS']):
        return
    try:
        datawatch.update_related(sender, instance)
    except Exception as e:
        logger.exception(e)
