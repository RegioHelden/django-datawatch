# -*- coding: UTF-8 -*-
from django_datawatch.backends.base import BaseBackend
from django_datawatch.models import Result
from django_datawatch.monitoring import monitor


class Backend(BaseBackend):
    def enqueue(self, slug, async=True):
        check = self._get_check_instance(slug)
        if not check:
            return

        try:
            for payload in check.generate():
                monitor.get_backend().run(
                    check.slug, check.get_identifier(payload))
        except NotImplementedError:
            pass

    def refresh(self, slug, async=True):
        for result in Result.objects.filter(slug=slug):
            monitor.get_backend().run(result.slug, result.identifier)

    def run(self, slug, identifier, async=True):
        check = self._get_check_instance(slug)
        if not check:
            return

        payload = check.get_payload(identifier)
        check.handle(payload)

    def _get_check_instance(self, slug):
        check_class = monitor.get_check_class(slug)
        if not check_class:
            return None
        return check_class()
