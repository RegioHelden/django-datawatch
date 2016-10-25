# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

import datetime
try:
    from unittest import mock
except ImportError:
    import mock
import pytz

from dateutil import relativedelta
from freezegun import freeze_time
from django.test.testcases import TestCase
from django.conf import settings

from django_datawatch.base import BaseCheck
from django_datawatch.monitoring import monitor, Scheduler


class CheckRunEvery(BaseCheck):
    run_every = relativedelta.relativedelta(days=1)

    def generate(self):
        pass

    def check(self, payload):
        pass


class CheckNoRunEvery(BaseCheck):
    def generate(self):
        pass

    def check(self, payload):
        pass


class SchedulerTestCase(TestCase):
    @mock.patch('django_datawatch.tests.test_scheduler.CheckNoRunEvery.run')
    def test_skip_no_run_every(self, mock_run):
        monitor.get_all_registered_checks = mock.MagicMock(return_value=[
            CheckNoRunEvery])
        scheduler = Scheduler()
        scheduler.get_last_executions = mock.MagicMock(return_value={})
        scheduler.run_checks()
        self.assertFalse(mock_run.called)

    @mock.patch('django_datawatch.tests.test_scheduler.CheckRunEvery.run')
    def test_no_previous_execution(self, mock_run):
        monitor.get_all_registered_checks = mock.MagicMock(return_value=[
            CheckRunEvery])
        scheduler = Scheduler()
        scheduler.get_last_executions = mock.MagicMock(return_value={})
        scheduler.run_checks()
        self.assertTrue(mock_run.called)

    @freeze_time('2016-12-01 00:00:00')
    @mock.patch('django_datawatch.tests.test_scheduler.CheckRunEvery.run')
    def test_execution_in_past(self, mock_run):
        monitor.get_all_registered_checks = mock.MagicMock(return_value=[
            CheckRunEvery])
        scheduler = Scheduler()

        scheduler.get_last_executions = mock.MagicMock(return_value={
            'django_datawatch.tests.test_scheduler.CheckRunEvery':
                datetime.datetime(2016, 1, 1, 0, 0, 0, 0, pytz.timezone(
                    settings.TIME_ZONE)),
        })
        scheduler.run_checks()
        self.assertTrue(mock_run.called)

    @freeze_time('2016-01-01 00:00:00')
    @mock.patch('django_datawatch.tests.test_scheduler.CheckRunEvery.run')
    def test_execution_in_future(self, mock_run):
        monitor.get_all_registered_checks = mock.MagicMock(return_value=[
            CheckRunEvery])
        scheduler = Scheduler()

        scheduler.get_last_executions = mock.MagicMock(return_value={
            'django_datawatch.tests.test_scheduler.CheckRunEvery':
                datetime.datetime(2016, 12, 1, 0, 0, 0, 0, pytz.timezone(
                    settings.TIME_ZONE)),
        })
        scheduler.run_checks()
        self.assertFalse(mock_run.called)

    @freeze_time('2016-12-01 00:00:00')
    @mock.patch('django_datawatch.tests.test_scheduler.CheckRunEvery.run')
    def test_execution_in_future_and_force(self, mock_run):
        monitor.get_all_registered_checks = mock.MagicMock(return_value=[
            CheckRunEvery])
        scheduler = Scheduler()

        scheduler.get_last_executions = mock.MagicMock(return_value={
            'django_datawatch.tests.test_scheduler.CheckRunEvery':
                datetime.datetime(2016, 12, 1, 0, 0, 0, 0, pytz.timezone(
                    settings.TIME_ZONE)),
        })
        scheduler.run_checks(force=True)
        self.assertTrue(mock_run.called)
