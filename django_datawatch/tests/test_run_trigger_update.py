# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

try:
    from unittest import mock
except ImportError:
    import mock

from django.test.testcases import TestCase, override_settings

from django_datawatch.monitoring import run_checks


class SettingsTestCase(TestCase):
    @override_settings(DJANGO_DATAWATCH_RUN_POST_SAVE_SIGNALS=True)
    @mock.patch('django_datawatch.monitoring.Scheduler.update_related')
    def test_setting_run_post_save_signals_true(self, mock_update):
        run_checks(sender=None, instance=None, created=None, raw=None,
                   using=None)
        self.assertTrue(mock_update.called)

    @override_settings(DJANGO_DATAWATCH_RUN_POST_SAVE_SIGNALS=False)
    @mock.patch('django_datawatch.monitoring.Scheduler.update_related')
    def test_setting_run_post_save_signals_false(self, mock_update):
        run_checks(sender=None, instance=None, created=None, raw=None,
                   using=None)
        self.assertFalse(mock_update.called)
