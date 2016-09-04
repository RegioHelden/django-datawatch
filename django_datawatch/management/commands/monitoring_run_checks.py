# -*- coding: UTF-8 -*-
import logging

from django.core.management.base import BaseCommand

from django_datawatch.monitoring import monitor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for check in monitor.get_all_registered_checks():
            check().run()
