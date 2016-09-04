# -*- coding: UTF-8 -*-
import logging

from django.core.management.base import BaseCommand

from django_datawatch.models import Result

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete all results for which check does not exist anymore.'

    def handle(self, *args, **options):
        results = Result.objects.ghost_results()
        check_names = list(results.distinct().values_list('slug', flat=True))
        results.delete()
        logger.info('%d results have been deleted:\n%s', len(check_names), '\n'.join(check_names))
