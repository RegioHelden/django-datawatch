# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand

from django_datawatch.monitoring import Scheduler, monitor


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            dest='slug',
            default=None,
            help='Slug of check to refresh, all checks will be refreshed if slug is not provided',
        )

    def handle(self, slug, *args, **options):
        # refresh single check
        if slug:
            self.refresh(slug)
            return

        # refresh all
        checks = monitor.get_all_registered_checks()
        for check_class in checks:
            check = check_class()
            self.refresh(check.slug)

    def refresh(self, slug):
        backend = monitor.get_backend()
        backend.refresh(slug=slug, async=True)
