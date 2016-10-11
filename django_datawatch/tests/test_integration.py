# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

from django.test.testcases import TestCase

from django_datawatch.base import BaseCheck
from django_datawatch.monitoring import monitor


class CheckImplementationTestCase(TestCase):
    pass


def test_generator(check_instance):
    def test(self):
        if not hasattr(check_instance, 'slug'):
            self.fail('{check} has no slug'.format(
                check=check_instance.__class__.__name__))
        self.assertIsInstance(
            check_instance, BaseCheck,
            '{slug} is not derived from BaseCheck'.format(
                slug=check_instance.slug))
        check_instance_dict = check_instance.__class__.__dict__

        # check general implementation
        if 'check' not in check_instance_dict:
            self.fail('{slug} must implement the check method'.format(
                slug=check_instance.slug))
        if 'get_identifier' not in check_instance_dict:
            self.fail('{slug} must implement the get_identifier method'.format(
                slug=check_instance.slug))

        # generate must be implemented if task should be running periodically
        if 'run_every' in check_instance_dict and check_instance_dict['run_every'] is not None:
            if 'generate' not in check_instance_dict:
                self.fail('{slug} must implement the generate method'.format(
                    slug=check_instance.slug))

        # a resolver method must be implemented for every update trigger
        if 'trigger_update' in check_instance_dict and check_instance_dict['trigger_update']:
            for key, value in check_instance_dict['trigger_update'].items():
                method_name = 'get_%s_payload' % key
                if method_name not in check_instance_dict:
                    self.fail(
                        '{slug} must implement a resolver method for every trigger_update, {method} is missing'.format(
                            slug=check_instance.slug, method=method_name))

    return test


monitor.autodiscover_checks()
for check in monitor.get_all_registered_checks():
    check_instance = check()
    test_name = 'test_{module}_{check}'.format(
        module=check_instance.__module__,
        check=check_instance.__class__.__name__)
    test = test_generator(check_instance)
    setattr(CheckImplementationTestCase, test_name, test)
