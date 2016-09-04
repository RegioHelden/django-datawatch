# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from django_datawatch.models import Check


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('slug', 'identifier', 'status')
    search_fields = ('slug', 'identifier', 'payload_description')
    list_filter = ('status', )
