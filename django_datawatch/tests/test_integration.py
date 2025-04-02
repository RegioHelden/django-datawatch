from django.test.testcases import TestCase

from django_datawatch.base import BaseCheck
from django_datawatch.datawatch import datawatch


class CheckImplementationTestCase(TestCase):
    pass


def test_generator(check_instance):
    def test(self):
        if not hasattr(check_instance, "slug"):
            self.fail(f"{check_instance.__class__.__name__} has no slug")
        self.assertIsInstance(check_instance, BaseCheck, f"{check_instance.slug} is not derived from BaseCheck")
        check_dict = check_instance.__class__.__dict__

        # check general implementation
        if "check" not in check_dict:
            self.fail(f"{check_instance.slug} must implement the check method")
        if "get_identifier" not in check_dict:
            self.fail(f"{check_instance.slug} must implement the get_identifier method")

        # generate must be implemented if task should be running periodically
        if check_dict.get("run_every", None) is not None and "generate" not in check_dict:
            self.fail(f"{check_instance.slug} must implement the generate method")

        # a resolver method must be implemented for every update trigger
        if check_dict.get("trigger_update", None) is not None:
            for key, _value in check_dict["trigger_update"].items():
                method_name = f"get_{key}_payload"
                if method_name not in check_dict:
                    self.fail(
                        f"{check_instance.slug} must implement a resolver method for every"
                        f" trigger_update, {method_name} is missing",
                    )

    return test


datawatch.autodiscover_checks()
for check in datawatch.get_all_registered_checks():
    check_instance = check()
    test_name = f"test_{check_instance.__module__}_{check_instance.__class__.__name__}"
    test = test_generator(check_instance)
    setattr(CheckImplementationTestCase, test_name, test)
