# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

from django.apps import AppConfig
from django.contrib import admin
from django_datawatch.monitoring import monitor


class DjangoDatawatchConfig(AppConfig):
    name = 'django_datawatch'
    verbose_name = "Django datawatch"

    def ready(self):
        super(DjangoDatawatchConfig, self).ready()

        monitor.autodiscover_checks()
        admin.autodiscover()
