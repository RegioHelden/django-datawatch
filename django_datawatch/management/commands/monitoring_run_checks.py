# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand

from django_datawatch.monitoring import Scheduler


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Execute all checks.',
        )

    def handle(self, force, *args, **options):
        Scheduler().run_checks(force=force)
