import logging

from django.core.management.base import BaseCommand

from django_datawatch.tasks import datawatch_cleanup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Delete all results and executions for removed checks."

    def handle(self, *args, **options):
        datawatch_cleanup.apply()
