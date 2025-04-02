from django.contrib import admin

from example import models


@admin.register(models.Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance")
    search_fields = ("user__username",)
