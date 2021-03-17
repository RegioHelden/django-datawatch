# -*- coding: UTF-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist

from django_datawatch.backends.base import BaseBackend
from django_datawatch.models import Result
from django_datawatch.datawatch import datawatch

logger = logging.getLogger(__name__)


class Backend(BaseBackend):
    def enqueue(self, slug, run_async=True):
        check = self._get_check_instance(slug)
        if not check:
            return

        try:
            for payload in check.generate():
                if payload is None:
                    continue
                datawatch.get_backend().run(check.slug, check.get_identifier(payload))
        except NotImplementedError as e:
            logger.error(e)

    def refresh(self, slug, run_async=True):
        for result in Result.objects.filter(slug=slug):
            datawatch.get_backend().run(result.slug, result.identifier)

    def run(self, slug, identifier, run_async=True, user_forced_refresh=False):
        check = self._get_check_instance(slug)
        if not check:
            return

        try:
            payload = check.get_payload(identifier)
        except NotImplementedError as e:
            logger.error(e)
            return
        except ObjectDoesNotExist:
            Result.objects.filter(slug=slug, identifier=identifier).delete()
            return

        # refresh has been forced by a user from the web view
        if user_forced_refresh:
            check.user_forced_refresh_hook(payload=payload)

        check.handle(payload)

    def _get_check_instance(self, slug):
        check_class = datawatch.get_check_class(slug)
        if not check_class:
            return None
        return check_class()
