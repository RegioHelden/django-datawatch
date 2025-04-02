from django_datawatch.backends.base import BaseBackend
from django_datawatch.tasks import django_datawatch_enqueue, django_datawatch_refresh, django_datawatch_run


class Backend(BaseBackend):
    """
    A wrapper backend to execute tasks asynchronously in celery
    """

    def enqueue(self, slug, run_async=True):
        kwargs = {"kwargs": {"slug": slug}}
        if run_async:
            django_datawatch_enqueue.apply_async(**kwargs)
        else:
            django_datawatch_enqueue.apply(**kwargs)

    def refresh(self, slug, run_async=True):
        kwargs = {"kwargs": {"slug": slug}}
        if run_async:
            django_datawatch_refresh.apply_async(**kwargs)
        else:
            django_datawatch_refresh.apply(**kwargs)

    def run(self, slug, identifier, run_async=True, user_forced_refresh=False, queue=None):
        kwargs = {"kwargs": {"slug": slug, "identifier": identifier, "user_forced_refresh": user_forced_refresh}}

        if run_async:
            django_datawatch_run.apply_async(**kwargs, queue=queue)
        else:
            django_datawatch_run.apply(**kwargs, queue=queue)
