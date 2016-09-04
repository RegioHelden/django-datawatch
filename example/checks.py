# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function


from django.utils.translation import ugettext as _
from django_datawatch.models import Check
from django_datawatch.monitoring import monitor
from django_datawatch.base import BaseCheck, BaseCheckForm
from django import forms

from example import models


class UserHasEnoughBalanceConfig(BaseCheckForm):
    danger = forms.IntegerField(initial=0, label=_('Balance critical'))
    warning = forms.IntegerField(initial=100, label=_('Balance warning'))


@monitor.register
class UserHasEnoughBalance(BaseCheck):
    config_form = UserHasEnoughBalanceConfig
    title = _('User balance')
    template_name = 'example/checks/user_has_enough_balance.html'
    trigger_update = dict(wallet=models.Wallet)

    def generate(self):
        for payload in models.Wallet.objects.all():
            yield payload

    def check(self, payload):
        config = self.get_config(payload)
        if payload.balance < config['danger']:
            return Check.STATUS.danger
        if payload.balance < config['warning']:
            return Check.STATUS.warning
        return Check.STATUS.ok

    def get_identifier(self, payload):
        return payload.pk

    def get_payload(self, identifier):
        return models.Wallet.objects.get(pk=identifier)

    def get_payload_description(self, payload):
        return payload.user.username

    def get_wallet_payload(self, instance):
        return instance
