# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import os

from django.apps import apps
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

app = Celery('example')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
