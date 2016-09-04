# -*- coding: UTF-8 -*-
import logging

from django.core.management.base import BaseCommand

from django_datawatch.monitoring import Scheduler


class Command(BaseCommand):
    def handle(self, *args, **options):
        Scheduler().run_checks()
