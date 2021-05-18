# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

from django_datawatch.backends import synchronous
from django_datawatch.datawatch import Scheduler

logger = get_task_logger(__name__)


@shared_task
def django_datawatch_enqueue(slug, *args, **kwargs):
    logger.debug('enqueuing checks for %s', slug)
    synchronous.Backend().enqueue(slug=slug)


@shared_task
def django_datawatch_refresh(slug, *args, **kwargs):
    logger.debug('refreshing check results for %s', slug)
    synchronous.Backend().refresh(slug=slug)


@shared_task
def django_datawatch_run(slug, identifier, user_forced_refresh=False, *args, **kwargs):
    logger.debug('running check %s for identifier %s (forced refresh %s)', slug, identifier, user_forced_refresh)
    synchronous.Backend().run(slug=slug, identifier=identifier, user_forced_refresh=user_forced_refresh)


@shared_task
def django_datawatch_scheduler(*args, **kwargs):
    Scheduler().run_checks(force=False)
