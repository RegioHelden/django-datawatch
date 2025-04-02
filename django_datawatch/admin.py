from django.contrib import admin

from django_datawatch.models import (
    CheckExecution,
    Result,
    ResultAssignedGroup,
    ResultAssignedUser,
    ResultStatusHistory,
)


class ResultAssignedGroupInline(admin.TabularInline):
    model = ResultAssignedGroup
    extra = 0


class ResultAssignedUserInline(admin.TabularInline):
    model = ResultAssignedUser
    extra = 0


@admin.register(Result)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("slug", "identifier", "status")
    readonly_fields = ("created", "modified")
    search_fields = ("slug", "identifier", "payload_description")
    list_filter = ("status", "slug", "assigned_groups")
    inlines = (ResultAssignedGroupInline, ResultAssignedUserInline)


@admin.register(CheckExecution)
class CheckExecutionAdmin(admin.ModelAdmin):
    list_display = ("slug", "last_run")
    search_fields = ("slug",)


@admin.register(ResultStatusHistory)
class ResultStatusHistory(admin.ModelAdmin):
    list_display = (
        "result",
        "from_status",
        "to_status",
        "created",
    )
    autocomplete_fields = ("result",)
    ordering = ("result", "created")
    list_select_related = ("result",)
