import json
from typing import ClassVar

from dateutil import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields.json import JSONField
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel

from django_datawatch.querysets import CheckExecutionQuerySet

from .datawatch import datawatch
from .querysets import ResultQuerySet


class AlreadyAcknowledgedError(Exception):
    pass


class Result(TimeStampedModel):
    STATUS = Choices(
        (0, "unknown", _("Unknown")),
        (1, "ok", _("OK")),
        (2, "warning", _("Warning")),
        (3, "critical", _("Critical")),
    )

    slug = models.TextField(verbose_name=_("Module slug"))
    identifier = models.CharField(max_length=256, verbose_name=_("Identifier"))

    status = models.IntegerField(choices=STATUS, default=STATUS.unknown, verbose_name=_("Status"))
    data = JSONField(blank=True, default=dict, verbose_name=("Data"))
    config = JSONField(blank=True, default=dict, verbose_name=_("Configuration"))

    payload_description = models.TextField(verbose_name=_("Payload description"))

    acknowledged_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        verbose_name=_("Acknowledged by"),
        related_name="acknowledged_by",
        on_delete=models.CASCADE,
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Acknowledged at"))
    acknowledged_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Acknowledged until"))
    acknowledged_reason = models.TextField(blank=True, verbose_name=_("Acknowledge reason"))

    assigned_users = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        through="ResultAssignedUser",
        related_name="assigned_results",
        blank=True,
        verbose_name=_("Assigned users"),
    )
    assigned_groups = models.ManyToManyField(
        to="auth.Group",
        through="ResultAssignedGroup",
        related_name="assigned_groups",
        blank=True,
        verbose_name=_("Assigned groups"),
    )

    objects = ResultQuerySet.as_manager()

    class Meta:
        unique_together = ("slug", "identifier")
        permissions = (
            ("view", "Can view results dashboard and details"),
            ("acknowledge", "Can acknowledge results"),
            ("config", "Can change the configuration for results"),
            ("refresh", "Can refresh results"),
            ("tag", "Can add and remove tags on results"),
        )

    def __str__(self):
        return self.slug

    def acknowledge(self, user, days, reason=None, commit=True):
        # calculate end of requested acknowledgement
        acknowledged_until = timezone.now() + relativedelta.relativedelta(days=days)

        # check that we're not accidentally overriding the current setup
        if (
            self.status in (self.STATUS.warning, self.STATUS.critical)
            and self.is_acknowledged()
            and self.acknowledged_until > acknowledged_until
        ):
            raise AlreadyAcknowledgedError
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.acknowledged_until = acknowledged_until
        self.acknowledged_reason = reason or ""
        if commit:
            self.save(update_fields=["acknowledged_at", "acknowledged_by", "acknowledged_until", "acknowledged_reason"])

    def is_acknowledged(self):
        return self.acknowledged_until and self.acknowledged_until >= timezone.now()

    def get_check_instance(self):
        return datawatch.get_check_class(self.slug)()

    def get_payload(self):
        return self.get_check_instance().get_payload(self.identifier)

    def get_formatted_data(self):
        return datawatch.get_check_class(self.slug)().format_result_data(self)

    def latest_status(self, status):
        return self.status_history.filter(to_status=status).order_by("-created").first()

    @cached_property
    def latest_unknown(self):
        return self.latest_status(self.STATUS.unknown)

    @cached_property
    def latest_ok(self):
        return self.latest_status(self.STATUS.ok)

    @cached_property
    def latest_warning(self):
        return self.latest_status(self.STATUS.warning)

    @cached_property
    def latest_critical(self):
        return self.latest_status(self.STATUS.critical)

    def config_formatted(self):
        return json.dumps(self.get_check_instance().get_config(payload=self.get_payload()), indent=4)


class ResultStatusHistory(TimeStampedModel):
    result = models.ForeignKey(Result, models.CASCADE, "status_history", "status_history", verbose_name=_("Result"))
    from_status = models.IntegerField(choices=Result.STATUS, verbose_name=_("From status"), null=True)
    to_status = models.IntegerField(choices=Result.STATUS, verbose_name=_("To status"))

    class Meta:
        verbose_name = _("Result status history")
        verbose_name_plural = _("Result status history")


class ResultAssignedGroup(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, verbose_name=_("Result"))
    group = models.ForeignKey(to="auth.Group", verbose_name=_("Group"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Result assigned group")
        verbose_name_plural = _("Result assigned groups")
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["result", "group"], name="unique_result_assigned_group"),
        ]

    def __str__(self):
        return f"Group {self.group} assigned to {self.result}"

    def validate_unique(self, exclude=None):
        if (
            ResultAssignedGroup.objects.filter(result_id=self.result_id, group_id=self.group_id)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError({"group": _("Group must be unique across the result")})
        super().validate_unique(exclude)


class ResultAssignedUser(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, verbose_name=_("Result"))
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Result assigned user")
        verbose_name_plural = _("Result assigned users")
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["result", "user"], name="unique_result_assigned_user"),
        ]

    def __str__(self):
        return f"User {self.user} assigned to {self.result}"

    def validate_unique(self, exclude=None):
        if (
            ResultAssignedUser.objects.filter(result_id=self.result_id, user_id=self.user_id)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError({"user": _("User must be unique across the result")})
        super().validate_unique(exclude)


class ResultTag(TimeStampedModel):
    class StatusChoices(models.IntegerChoices):
        DEFAULT = 1, _("Grey")
        SUCCESS = 2, _("Green")
        INFO = 3, _("Blue")
        WARNING = 4, _("Yellow")
        IMPORTANT = 5, _("Red")

    result = models.ForeignKey(Result, on_delete=models.CASCADE, verbose_name=_("Result"))
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    tag = models.CharField(max_length=50, verbose_name=_("Tag"))
    type = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.DEFAULT, verbose_name=_("Type"))

    class Meta:
        verbose_name = _("Result tag")
        verbose_name_plural = _("Result tags")
        unique_together = ("result", "tag")

    def __str__(self):
        return f"Tag '{self.tag}' on {self.result}"

    @property
    def badge_class(self) -> str:
        """Return a Bootstrap badge class string based on the tag `type`.
        Templates should use it like: <span class="badge {{ tag.badge_class }}">{{ tag.tag }}</span>
        """
        mapping = {
            self.StatusChoices.SUCCESS: "bg-success",
            self.StatusChoices.INFO: "bg-info",
            self.StatusChoices.WARNING: "bg-warning text-dark",
            self.StatusChoices.IMPORTANT: "bg-danger",
            self.StatusChoices.DEFAULT: "bg-secondary",
        }
        return mapping.get(self.type, "bg-secondary")


class CheckExecution(models.Model):
    slug = models.TextField(verbose_name=_("Check module slug"), unique=True)
    last_run = models.DateTimeField(verbose_name=_("Last run"))

    objects = CheckExecutionQuerySet.as_manager()

    def __str__(self):
        return f"{self.slug} on {self.last_run}"
