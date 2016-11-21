# -*- coding: UTF-8 -*-

defaults = dict(
    BACKEND='django_datawatch.backends.synchronous',
    CELERY_QUEUE_NAME='django_datawatch',
    RUN_SIGNALS=True)
