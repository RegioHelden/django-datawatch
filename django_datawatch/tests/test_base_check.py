from django.test.testcases import TestCase

from django_datawatch.base import BaseCheck
from django_datawatch.models import Result, ResultStatusHistory


class BaseCheckTestCase(TestCase):
    def setUp(self) -> None:
        self.check = type('FakeCheck', (BaseCheck,), dict(slug='fake_check'))()
        self.fake_payload = type('FakePayload', (object,), dict(pk=1))()

    def test_save_tracks_status_change_on_initial_creation(self):
        result = self.check.save(self.fake_payload, Result.STATUS.ok)

        history_qs = ResultStatusHistory.objects.all()
        self.assertEqual(history_qs.count(), 1)

        history = history_qs.get()
        self.assertEqual(history.result, result)
        self.assertEqual(history.from_status, None)
        self.assertEqual(history.to_status, result.status)

    def test_save_does_not_track_same_status_change(self):
        result1 = self.check.save(self.fake_payload, Result.STATUS.ok)

        history_qs = ResultStatusHistory.objects.all()
        self.assertEqual(history_qs.count(), 1)

        history = history_qs.get()
        self.assertEqual(history.result, result1)
        self.assertEqual(history.to_status, result1.status)

        result2 = self.check.save(self.fake_payload, Result.STATUS.ok)
        self.assertEqual(result1, result2)
        self.assertEqual(history_qs.count(), 1)

        history = history_qs.get()
        self.assertEqual(history.result, result2)
        self.assertEqual(history.to_status, result2.status)

    def test_save_tracks_different_status_changes(self):
        result1 = self.check.save(self.fake_payload, Result.STATUS.ok)

        history_qs = ResultStatusHistory.objects.all()
        self.assertEqual(history_qs.count(), 1)

        history = history_qs.get()
        self.assertEqual(history.to_status, result1.status)
        self.assertEqual(history.to_status, result1.status)

        result2 = self.check.save(self.fake_payload, Result.STATUS.critical)
        self.assertEqual(history_qs.count(), 2)

        latest_history = history_qs.latest('created')
        self.assertEqual(latest_history.to_status, result2.status)
        self.assertEqual(latest_history.to_status, result2.status)
