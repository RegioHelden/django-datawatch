from django.apps import AppConfig
from django.contrib import admin

from django_datawatch.datawatch import datawatch


class DjangoDatawatchConfig(AppConfig):
    name = "django_datawatch"
    verbose_name = "Django datawatch"

    def ready(self):
        super().ready()

        datawatch.autodiscover_checks()
        admin.autodiscover()
