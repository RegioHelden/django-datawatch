from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test.testcases import TestCase

from django_datawatch.models import Result

User = get_user_model()


class ResultQuerySetTestCase(TestCase):
    def _make_users(self, usernames: list):
        users = []
        for username in usernames:
            users.append(User(**{User.USERNAME_FIELD: username}))
        return User.objects.bulk_create(users)

    def _make_groups(self, names: list):
        groups = []
        for name in names:
            groups.append(Group(name=name))
        return Group.objects.bulk_create(groups)

    def _make_result(
        self,
        slug,
        users: list | None = None,
        groups: list | None = None,
    ):
        result = Result.objects.create(slug=slug, identifier="test_identifier")
        if users:
            result.assigned_users.set(users)
        if groups:
            result.assigned_groups.set(groups)
        return result

    def _assert_for_user_results(self, user, expected_results):
        queryset = Result.objects.for_user(user).order_by("pk")
        self.assertEqual(queryset.count(), len(expected_results))
        self.assertEqual(list(queryset), sorted(expected_results, key=lambda x: x.pk))

    def test_for_user(self):
        groups = self._make_groups(["g1", "g2", "g3"])
        users = self._make_users(["u1", "u2", "u3"])

        group_with_user = groups[1]
        group_without_users = groups[2]
        group_with_users = groups[0]

        user_with_group = users[0]
        user_without_group = users[1]
        user_with_groups = users[2]

        user_with_group.groups.set([group_with_users])
        user_with_groups.groups.set([group_with_users, group_with_user])

        # No group and no user (u1, u2, u3)
        res_no_user_no_group = self._make_result("test1")
        # One group but no user (u3)
        res_with_group_no_user = self._make_result("test2", groups=[group_with_user])
        # One user but no group (u1)
        res_with_user_no_group = self._make_result("test3", users=[user_with_group])
        # Multiple groups but no user (u3)
        res_with_groups_no_user = self._make_result(
            "test4",
            groups=[group_with_user, group_without_users],
        )
        # Multiple users but no groups (u1, u3)
        res_with_users_no_group = self._make_result(
            "test5",
            users=[user_with_group, user_with_groups],
        )
        # One group and one user (u2)
        res_with_group_and_user = self._make_result(
            "test6",
            users=[user_without_group],
            groups=[group_with_user],
        )
        # Multiple groups and one user (u2)
        res_with_groups_and_user = self._make_result(
            "test7",
            users=[user_without_group],
            groups=[group_with_user, group_without_users],
        )
        # One group and multiple users (u1, u3)
        res_with_group_and_users = self._make_result(
            "test8",
            users=[user_with_group, user_with_groups],
            groups=[group_with_user],
        )
        self._assert_for_user_results(
            user_with_group,
            [
                res_no_user_no_group,
                res_with_user_no_group,
                res_with_users_no_group,
                res_with_group_and_users,
            ],
        )
        self._assert_for_user_results(
            user_without_group,
            [res_no_user_no_group, res_with_group_and_user, res_with_groups_and_user],
        )
        self._assert_for_user_results(
            user_with_groups,
            [
                res_no_user_no_group,
                res_with_group_no_user,
                res_with_groups_no_user,
                res_with_users_no_group,
                res_with_group_and_users,
            ],
        )

    def test_get_stats_overcounts_due_to_join_multiplication(self) -> None:
        users = self._make_users(["u1", "u2"])
        groups = self._make_groups(["g1", "g2"])
        user = users[0]
        user.groups.set(groups)
        self._make_result(
            "test",
            users=users,
            groups=groups,
        )

        stats = Result.objects.for_user(user).get_stats()

        self.assertEqual(stats.count(), 1)
        self.assertEqual(stats[0]["amount"], 1)
