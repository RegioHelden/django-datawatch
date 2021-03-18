# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django_datawatch.backends.base import BaseBackend
from django_datawatch.tasks import django_datawatch_enqueue, \
    django_datawatch_run, django_datawatch_refresh


class Backend(BaseBackend):
    """
    A wrapper backend to execute tasks asynchronously in celery
    """
    def enqueue(self, slug, run_async=True):
        kwargs = dict(kwargs=dict(slug=slug))
        if run_async:
            django_datawatch_enqueue.apply_async(**kwargs)
        else:
            django_datawatch_enqueue.apply(**kwargs)

    def refresh(self, slug, run_async=True):
        kwargs = dict(kwargs=dict(slug=slug))
        if run_async:
            django_datawatch_refresh.apply_async(**kwargs)
        else:
            django_datawatch_refresh.apply(**kwargs)

    def run(self, slug, identifier, run_async=True, user_forced_refresh=False):
        kwargs = dict(kwargs=dict(slug=slug, identifier=identifier, user_forced_refresh=user_forced_refresh))
        if run_async:
            django_datawatch_run.apply_async(**kwargs)
        else:
            django_datawatch_run.apply(**kwargs)
