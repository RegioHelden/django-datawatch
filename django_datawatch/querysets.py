from django.db import models
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When, Value
from django.db.models.query_utils import Q
from django.utils import timezone

from django_datawatch.datawatch import datawatch


class ResultQuerySet(models.QuerySet):
    def for_user(self, user):
        user_groups = user.groups.all()
        return self.filter(
            Q(assigned_users=user)
            | Q(assigned_groups__in=user_groups)
            | Q(assigned_users__isnull=True, assigned_groups__isnull=True)
        ).distinct()

    def failed(self):
        return self.exclude(status__in=(self.model.STATUS.unknown, self.model.STATUS.ok))

    def ok(self):
        return self.filter(status=self.model.STATUS.ok)

    def unknown(self):
        return self.filter(status=self.model.STATUS.unknown)

    def unacknowledged(self):
        return self.exclude(acknowledged_until__gt=timezone.now())

    def with_status_name(self):
        case = Case(output_field=models.CharField())
        for status_value in self.model.STATUS._db_values:
            case.cases.append(
                When(status=status_value, then=Value(str(self.model.STATUS[status_value]))),
            )
        return self.annotate(status_name=case)

    def get_stats(self):
        return self.values('status').annotate(amount=Count('id')).with_status_name()

    def ghost_results(self):
        """
        :return: results that do not have checks anymore (check has been deleted)
        """
        return self.exclude(slug__in=datawatch.get_all_registered_check_slugs())


class CheckExecutionQuerySet(models.QuerySet):
    def ghost_executions(self):
        """
        :return: check executions that do not have checks anymore (check has been deleted)
        """
        return self.exclude(slug__in=datawatch.get_all_registered_check_slugs())
