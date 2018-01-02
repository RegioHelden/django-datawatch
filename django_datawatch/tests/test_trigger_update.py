# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

from django_datawatch.backends.base import BaseBackend

try:
    from unittest import mock
except ImportError:
    import mock

from django.test.testcases import TestCase, override_settings

from django_datawatch.datawatch import datawatch, run_checks
from django_datawatch.base import BaseCheck
from django_datawatch.models import Result


@datawatch.register
class CheckTriggerUpdate(BaseCheck):
    model_class = Result
    trigger_update = dict(foobar=Result)

    def get_foobar_payload(self, instance):
        return instance

    def get_identifier(self, payload):
        return payload.pk

    def check(self, payload):
        return payload


class TriggerUpdateTestCase(TestCase):
    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=True)
    @mock.patch('django_datawatch.datawatch.DatawatchHandler.update_related')
    def test_setting_run_signals_true(self, mock_update):
        run_checks(sender=None, instance=None, created=None, raw=None,
                   using=None)
        self.assertTrue(mock_update.called)

    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=False)
    @mock.patch('django_datawatch.datawatch.DatawatchHandler.update_related')
    def test_setting_run_signals_false(self, mock_update):
        run_checks(sender=None, instance=None, created=None, raw=None,
                   using=None)
        self.assertFalse(mock_update.called)

    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=True)
    @mock.patch('django_datawatch.datawatch.DatawatchHandler.get_backend')
    def test_update_related_calls_backend(self, mock_get_backend):
        backend = mock.Mock(spec=BaseBackend)
        mock_get_backend.return_value = backend
        datawatch.update_related(sender=Result, instance=Result())
        self.assertTrue(backend.run.called)
