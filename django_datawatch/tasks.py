# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery.task.base import PeriodicTask


from django_datawatch.monitoring import monitor

logger = get_task_logger(__name__)


@shared_task
def django_datawatch_enqueue(check_slug, *args, **kwargs):
    logger.debug('enqueuing checks for %s', check_slug)
    check = monitor.get_check_class(check_slug)()

    for payload in check.generate():
        identifier = check.get_identifier(payload)
        django_datawatch_run.apply_async(kwargs=dict(check_slug=check_slug, identifier=identifier),
                                         queue='django_datawatch')


@shared_task
def django_datawatch_run(check_slug, identifier, *args, **kwargs):
    logger.debug('running check %s for identifier %s', check_slug, identifier)
    check = monitor.get_check_class(check_slug)()
    payload = check.get_payload(identifier)
    return check.handle(payload)


class DatawatchScheduler(PeriodicTask):
    run_every = crontab(minute=0, hour=0)

    def run(self, *args, **kwargs):
        for check_slug in monitor.checks:
            django_datawatch_enqueue.apply_async(kwargs=dict(check_slug=check_slug), queue='django_datawatch')
