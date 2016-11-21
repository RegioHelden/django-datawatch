# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand

from django_datawatch.datawatch import datawatch


class Command(BaseCommand):
    def handle(self, *args, **options):
        for slug in datawatch.get_all_registered_check_slugs():
            print(slug)
