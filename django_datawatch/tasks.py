# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery.task.base import PeriodicTask

from django_datawatch.backends import synchronous
from django_datawatch.monitoring import monitor
from django_datawatch.settings import ddw_settings

logger = get_task_logger(__name__)


@shared_task
def django_datawatch_enqueue(slug, *args, **kwargs):
    logger.debug('enqueuing checks for %s', slug)
    synchronous.Backend().enqueue(slug)


@shared_task
def django_datawatch_run(slug, identifier, *args, **kwargs):
    logger.debug('running check %s for identifier %s', slug, identifier)
    synchronous.Backend().run(slug, identifier)


class DatawatchScheduler(PeriodicTask):
    run_every = crontab(minute='*/1')
    queue = ddw_settings.QUEUE_NAME

    def run(self, *args, **kwargs):
        for check in monitor.get_all_registered_checks():
            check().run()
