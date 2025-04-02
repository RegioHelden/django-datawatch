from celery import shared_task
from celery.utils.log import get_task_logger

from django_datawatch.backends import synchronous
from django_datawatch.datawatch import Scheduler
from django_datawatch.models import CheckExecution, Result

logger = get_task_logger(__name__)


@shared_task
def django_datawatch_enqueue(slug, *args, **kwargs):
    logger.debug("enqueuing checks for %s", slug)
    synchronous.Backend().enqueue(slug=slug)


@shared_task
def django_datawatch_refresh(slug, *args, **kwargs):
    logger.debug("refreshing check results for %s", slug)
    synchronous.Backend().refresh(slug=slug)


@shared_task
def django_datawatch_run(slug, identifier, user_forced_refresh=False, *args, **kwargs):
    logger.debug(
        "running check %s for identifier %s (forced refresh %s)",
        slug,
        identifier,
        user_forced_refresh,
    )
    synchronous.Backend().run(
        slug=slug,
        identifier=identifier,
        user_forced_refresh=user_forced_refresh,
    )


@shared_task
def django_datawatch_scheduler(*args, **kwargs):
    Scheduler().run_checks(force=False)


@shared_task
def datawatch_cleanup(*args, **kwargs):
    results = Result.objects.ghost_results()
    check_names = list(results.distinct().values_list("slug", flat=True))
    results.delete()
    check_names_str = "\n".join(check_names)
    logger.info("%s results have been deleted:\n%s", len(check_names), check_names_str)

    check_executions = CheckExecution.objects.ghost_executions()
    check_names = list(check_executions.distinct().values_list("slug", flat=True))
    check_executions.delete()
    check_names_str = "\n".join(check_names)
    logger.info("%s check executions have been deleted:\n%s", len(check_names), check_names_str)
