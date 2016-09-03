# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

from django.apps import AppConfig
from django.contrib import admin
from django_monitoring.monitoring import monitor


class DjangoMonitoringConfig(AppConfig):
    name = 'django_monitoring'
    verbose_name = "DjangoMonitoring"

    def ready(self):
        super(DjangoMonitoringConfig, self).ready()

        monitor.autodiscover_checks()
        admin.autodiscover()
