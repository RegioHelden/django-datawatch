import datetime
from unittest import mock

from celery.schedules import crontab
from django.test.testcases import TestCase
from django.utils import timezone
from time_machine import travel

from django_datawatch.base import BaseCheck
from django_datawatch.datawatch import Scheduler, datawatch


class CheckRunEvery(BaseCheck):
    run_every = crontab(hour=0, minute=0)


class CheckNoRunEvery(BaseCheck):
    run_every = None


class SchedulerTestCase(TestCase):
    @mock.patch("django_datawatch.tests.test_scheduler.CheckNoRunEvery.run")
    def test_skip_no_run_every(self, mock_run):
        datawatch.get_all_registered_checks = mock.MagicMock(return_value=[CheckNoRunEvery])
        scheduler = Scheduler()
        scheduler.get_last_executions = mock.MagicMock(return_value={})
        scheduler.run_checks()
        self.assertFalse(mock_run.called)

    @mock.patch("django_datawatch.tests.test_scheduler.CheckRunEvery.run")
    def test_no_previous_execution(self, mock_run):
        datawatch.get_all_registered_checks = mock.MagicMock(return_value=[CheckRunEvery])
        scheduler = Scheduler()
        scheduler.get_last_executions = mock.MagicMock(return_value={})
        scheduler.run_checks()
        self.assertTrue(mock_run.called)

    @travel(datetime.datetime(2016, 12, 1, 0, 0, tzinfo=timezone.get_current_timezone()))
    @mock.patch("django_datawatch.tests.test_scheduler.CheckRunEvery.run")
    def test_execution_in_past(self, mock_run):
        datawatch.get_all_registered_checks = mock.MagicMock(return_value=[CheckRunEvery])
        scheduler = Scheduler()

        scheduler.get_last_executions = mock.MagicMock(
            return_value={
                "django_datawatch.tests.test_scheduler.CheckRunEvery": datetime.datetime(
                    2016,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=timezone.get_current_timezone(),
                ),
            },
        )
        scheduler.run_checks()
        self.assertTrue(mock_run.called)

    @travel(datetime.datetime(2016, 1, 1, 0, 0, tzinfo=timezone.get_current_timezone()))
    @mock.patch("django_datawatch.tests.test_scheduler.CheckRunEvery.run")
    def test_execution_in_future(self, mock_run):
        datawatch.get_all_registered_checks = mock.MagicMock(return_value=[CheckRunEvery])
        scheduler = Scheduler()

        scheduler.get_last_executions = mock.MagicMock(
            return_value={
                "django_datawatch.tests.test_scheduler.CheckRunEvery": datetime.datetime(
                    2016,
                    12,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=timezone.get_current_timezone(),
                ),
            },
        )
        scheduler.run_checks()
        self.assertFalse(mock_run.called)

    @travel(datetime.datetime(2016, 12, 1, 0, 0, tzinfo=timezone.get_current_timezone()))
    @mock.patch("django_datawatch.tests.test_scheduler.CheckRunEvery.run")
    def test_execution_in_future_and_force(self, mock_run):
        datawatch.get_all_registered_checks = mock.MagicMock(return_value=[CheckRunEvery])
        scheduler = Scheduler()

        scheduler.get_last_executions = mock.MagicMock(
            return_value={
                "django_datawatch.tests.test_scheduler.CheckRunEvery": datetime.datetime(
                    2016,
                    12,
                    1,
                    0,
                    0,
                    0,
                    0,
                    tzinfo=timezone.get_current_timezone(),
                ),
            },
        )
        scheduler.run_checks(force=True)
        self.assertTrue(mock_run.called)
