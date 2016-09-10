# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When, Value
from django.db.models.query_utils import Q
from django.utils import timezone

from django_datawatch.monitoring import monitor


class CheckQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(Q(assigned_to_group__isnull=True) | Q(assigned_to_group__in=user.groups.all()),
                           Q(assigned_to_user__isnull=True) | Q(assigned_to_user=user))

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
        return self.exclude(slug__in=monitor.get_all_registered_check_slugs())
