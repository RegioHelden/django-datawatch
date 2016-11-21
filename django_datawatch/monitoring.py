# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import logging
import importlib

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import autodiscover_modules

from django_datawatch.defaults import defaults

logger = logging.getLogger(__name__)


class MonitoringHandler(object):
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
        check.register(check_class)

        return check_class

    def get_all_registered_checks(self):
        return self._registered_checks.values()

    def get_all_registered_check_slugs(self):
        return self._registered_checks.keys()

    def get_check_class(self, slug):
        if slug in self._registered_checks:
            return self._registered_checks[slug]
        return None

    def related_model_exists(self, check_class, model_uid):
        monitor._related_models.setdefault(model_uid, list())
        return check_class not in monitor._related_models[model_uid]

    def related_model_add(self, check_class, model_uid):
        monitor._related_models[model_uid].append(check_class)

    def update_related(self, sender, instance):
        checks = monitor.get_checks_for_related_model(sender) or []
        for check_class in checks:
            check = check_class()
            check.update_related(instance)

    def get_checks_for_related_model(self, model):
        model_uid = make_model_uid(model)
        if model_uid in self._related_models:
            return self._related_models[model_uid]
        return None

    def get_checks_for_model(self, model):
        check_classes = list()
        for check_class in monitor.get_all_registered_checks():
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
        for check_class in monitor.get_checks_for_model(model=sender):
            check = check_class()
            identifier = check.get_identifier(instance)
            Result.objects.filter(slug=check.slug, identifier=identifier).delete()

monitor = MonitoringHandler()


class Scheduler(object):
    def run_checks(self, force=False, slug=None):
        """
        :param force: <bool> force all registered checks to be executed
        :return:
        """
        now = timezone.now()
        checks = monitor.get_all_registered_checks()
        last_executions = self.get_last_executions()

        for check_class in checks:
            check = check_class()

            # only update a single slug if requested
            if slug and check.slug != slug:
                continue

            # check is not meant to be run periodically
            if not isinstance(check_class.run_every, relativedelta):
                continue

            # shall the check be run again?
            if not force and check.slug in last_executions:
                if now < last_executions[check.slug] + check.run_every:
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
