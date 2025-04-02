from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test.testcases import TestCase

from django_datawatch.base import BaseCheck
from django_datawatch.models import Result, ResultStatusHistory

User = get_user_model()


class BaseCheckTestCase(TestCase):
    def setUp(self) -> None:
        self.check = type("FakeCheck", (BaseCheck,), {"slug": "fake_check"})()
        self.fake_payload = type("FakePayload", (object,), {"pk": 1})()

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

        latest_history = history_qs.latest("created")
        self.assertEqual(latest_history.to_status, result2.status)
        self.assertEqual(latest_history.to_status, result2.status)

    def test_save_sets_groups_and_users(self):
        groups = [Group.objects.create(name=f"group_{i}") for i in range(3)]
        users = [User.objects.create_user(**{User.USERNAME_FIELD: f"user_{i}"}) for i in range(3)]

        self.check.get_assigned_groups = mock.Mock(return_value=groups)
        self.check.get_assigned_users = mock.Mock(return_value=users)

        result = self.check.save(self.fake_payload, Result.STATUS.ok)

        self.assertEqual(result.assigned_groups.count(), 3)
        for group in groups:
            self.assertTrue(group in result.assigned_groups.all())
        self.assertEqual(result.assigned_users.count(), 3)
        for user in users:
            self.assertTrue(user in result.assigned_users.all())

        # Update with no assigned users/groups
        self.check.get_assigned_groups = mock.Mock(return_value=None)
        self.check.get_assigned_users = mock.Mock(return_value=None)
        result = self.check.save(self.fake_payload, Result.STATUS.ok)

        self.assertEqual(result.assigned_groups.count(), 0)
        self.assertEqual(result.assigned_users.count(), 0)

    def test_unique_groups(self):
        group = Group.objects.create(name="group")
        self.check.get_assigned_groups = mock.Mock(return_value=[group, group])

        result = self.check.save(self.fake_payload, Result.STATUS.ok)

        # Result should be created with only one group
        self.assertEqual(Result.objects.count(), 1)
        self.assertEqual(result.assigned_groups.count(), 1)
        self.assertEqual(result.assigned_groups.first(), group)

    def test_unique_users(self):
        user = User.objects.create_user(**{User.USERNAME_FIELD: "test_user"})
        self.check.get_assigned_users = mock.Mock(return_value=[user, user])

        result = self.check.save(self.fake_payload, Result.STATUS.ok)

        # Result should be created with only one user
        self.assertEqual(Result.objects.count(), 1)
        self.assertEqual(result.assigned_users.count(), 1)
        self.assertEqual(result.assigned_users.first(), user)
