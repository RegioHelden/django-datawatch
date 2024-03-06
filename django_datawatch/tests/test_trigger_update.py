from unittest import mock

from django.db import transaction
from django.test.testcases import TestCase, override_settings

from django_datawatch.backends.base import BaseBackend
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


@datawatch.register
class CheckTriggerUpdateList(BaseCheck):
    model_class = Result
    trigger_update = dict(foobar=Result)

    def get_foobar_payload(self, instance):
        return [instance, Result(pk=51945, slug="51945")]

    def get_identifier(self, payload):
        return payload.pk

    def check(self, payload):
        return payload


class TriggerUpdateTestCase(TestCase):
    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=True)
    @mock.patch('django_datawatch.datawatch.DatawatchHandler.update_related')
    def test_setting_run_signals_true(self, mock_update):
        run_checks(sender='sender', instance='instance', created=None, raw=None,
                   using=None)
        mock_update.assert_called_once_with('sender', 'instance', None)

    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=False)
    @mock.patch('django_datawatch.datawatch.DatawatchHandler.update_related')
    def test_setting_run_signals_false(self, mock_update):
        run_checks(sender=None, instance=None, created=None, raw=None,
                   using=None)
        mock_update.assert_not_called()

    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=True)
    @mock.patch('django_datawatch.datawatch.DatawatchHandler.get_backend')
    def test_update_related_calls_backend(self, mock_get_backend):
        backend = mock.Mock(spec=BaseBackend)
        mock_get_backend.return_value = backend

        with self.captureOnCommitCallbacks() as callbacks:
            datawatch.update_related(sender=Result, instance=Result(pk=143243, slug="143243"))

        self.assertEqual(3, len(callbacks))

        parameters = [
            dict(slug='django_datawatch.tests.test_trigger_update.CheckTriggerUpdate', identifier=143243, run_async=True),
            dict(slug='django_datawatch.tests.test_trigger_update.CheckTriggerUpdateList', identifier=143243, run_async=True),
            dict(slug='django_datawatch.tests.test_trigger_update.CheckTriggerUpdateList', identifier=51945, run_async=True),
        ]

        for callback in callbacks:
            callback()
            parameter_list = parameters.pop(0)
            backend.run.assert_called_once_with(**parameter_list)
            backend.reset_mock()
