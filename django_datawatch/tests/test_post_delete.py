# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

import mock
from django.test.testcases import TestCase, override_settings

from django_datawatch.base import BaseCheck
from django_datawatch.datawatch import datawatch, delete_results
from django_datawatch.models import Result
from django_datawatch.querysets import ResultQuerySet


@datawatch.register
class CheckPostDelete(BaseCheck):
    model = Result

    def get_identifier(self, payload):
        return payload.pk

    def check(self, payload):
        return payload


class PostDeleteTestCase(TestCase):
    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=True)
    @mock.patch('django_datawatch.datawatch.datawatch.delete_results')
    def test_setting_run_signals_true(self, mock_delete_results):
        delete_results(sender=None, instance=None, using=None)
        self.assertTrue(mock_delete_results.called)

    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=False)
    @mock.patch('django_datawatch.datawatch.datawatch.delete_results')
    def test_setting_run_signals_false(self, mock_delete_results):
        delete_results(sender=None, instance=None, using=None)
        self.assertFalse(mock_delete_results.called)

    @override_settings(DJANGO_DATAWATCH_RUN_SIGNALS=True)
    @mock.patch('django_datawatch.datawatch.DatawatchHandler.get_checks_for_model')
    def test_update_related_calls_backend(self, mock_get_checks_for_model):
        # mock the list of checks
        mock_get_checks_for_model.return_value = [CheckPostDelete]

        # mock the manager
        manager = mock.Mock(spec=ResultQuerySet)
        Result.objects = manager
        manager_filtered = mock.Mock(spec=ResultQuerySet)
        manager.filter.return_value = manager_filtered

        # test if delete has been called
        datawatch.delete_results(sender=Result, instance=Result(pk=1))
        manager.filter.assert_called_with(slug=CheckPostDelete().slug, identifier=1)
        manager_filtered.delete.assert_called_with()
