from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f"Balance of user {self.user} is {self.balance}"
