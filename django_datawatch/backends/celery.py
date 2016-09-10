# -*- coding: UTF-8 -*-
from django_datawatch.backends.base import BaseBackend
from django_datawatch.tasks import django_datawatch_enqueue, \
    django_datawatch_run
from django_datawatch.settings import ddw_settings


class Backend(BaseBackend):
    """
    A wrapper backend to execute tasks asynchronously in celery
    """
    def enqueue(self, slug, async=True):
        kwargs = dict(kwargs=dict(slug=slug), queue=ddw_settings.QUEUE_NAME)
        if async:
            django_datawatch_enqueue.apply_async(**kwargs)
        else:
            django_datawatch_enqueue.apply(**kwargs)

    def run(self, slug, identifier, async=True):
        kwargs = dict(kwargs=dict(slug=slug, identifier=identifier),
                      queue=ddw_settings.QUEUE_NAME)
        if async:
            django_datawatch_run.apply_async(**kwargs)
        else:
            django_datawatch_run.apply(**kwargs)
