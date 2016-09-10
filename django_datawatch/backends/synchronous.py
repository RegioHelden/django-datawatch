# -*- coding: UTF-8 -*-
from django_datawatch.backends.base import BaseBackend
from django_datawatch.monitoring import monitor


class Backend(BaseBackend):
    def enqueue(self, slug, async=True):
        check = monitor.get_check_class(slug)()
        for payload in check.generate():
            monitor.get_backend().run(
                check.slug, check.get_identifier(payload))

    def run(self, slug, identifier, async=True):
        check = monitor.get_check_class(slug)()
        payload = check.get_payload(identifier)
        check.handle(payload)
