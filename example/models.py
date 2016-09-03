# -*- coding: UTF-8 -*-
from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    balance = models.DecimalField(max_digits=9, decimal_places=2)
