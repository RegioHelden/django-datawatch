# -*- coding: UTF-8 -*-

defaults = dict(
    ASYNC_BACKEND='django_datawatch.backends.synchronous',
    CELERY_QUEUE_NAME='django_datawatch',
    RUN_POST_SAVE_SIGNALS=True)
