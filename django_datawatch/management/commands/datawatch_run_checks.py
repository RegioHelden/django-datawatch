# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand

from django_datawatch.datawatch import Scheduler


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Execute all checks.',
        )
        parser.add_argument(
            '--slug',
            dest='slug',
            default=None,
            help='Slug of check to refresh, all checks will be refreshed if slug is not provided',
        )

    def handle(self, force, slug, *args, **options):
        Scheduler().run_checks(force=force, slug=slug)
