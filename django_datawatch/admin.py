# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from django_datawatch.models import Result, CheckExecution, ResultStatusHistory


@admin.register(Result)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('slug', 'identifier', 'status')
    readonly_fields = ('created', 'modified')
    search_fields = ('slug', 'identifier', 'payload_description')
    list_filter = ('status', 'slug', 'assigned_to_group')


@admin.register(CheckExecution)
class CheckExecutionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'last_run')
    search_fields = ('slug',)


@admin.register(ResultStatusHistory)
class ResultStatusHistory(admin.ModelAdmin):
    list_display = (
        'result',
        'from_status',
        'to_status',
        'created',
    )
    autocomplete_fields = ('result',)
    ordering = ('result', 'created')
    list_select_related = ['result']
