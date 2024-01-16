from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test.testcases import TestCase

from django_datawatch.models import Result

User = get_user_model()

class ResultQuerySetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**{User.USERNAME_FIELD: 'test_user'})
        self.group = Group.objects.create(name='test_group')

    def test_for_user(self):
        result_without_users_and_groups = Result.objects.create(slug='test_slug', identifier='test_identifier')
        result_with = Result.objects.create(slug='test_slug2', identifier='test_identifier')
        result_with.assigned_users.add(self.user)
        result_with.assigned_groups.add(self.group)

        # User should have access to both results
        queryset = Result.objects.for_user(self.user)
        self.assertEqual(queryset.count(), 2)

        # User should have access to only one result
        other_user = User.objects.create_user(**{User.USERNAME_FIELD: 'test_user2'})
        queryset = Result.objects.for_user(other_user)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.get(), result_without_users_and_groups)
