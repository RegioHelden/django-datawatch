# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function

from celery.schedules import crontab
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django_datawatch.models import Result
from django_datawatch.datawatch import datawatch
from django_datawatch.base import BaseCheck, BaseCheckForm, CheckResponse
from django import forms

from example import models


class UserHasEnoughBalanceConfig(BaseCheckForm):
    critical = forms.IntegerField(initial=0, label=_('Balance critical'))
    warning = forms.IntegerField(initial=100, label=_('Balance warning'))


@datawatch.register
class UserHasEnoughBalance(BaseCheck):
    config_form = UserHasEnoughBalanceConfig
    run_every = crontab(hour='*/2')
    title = _('User balance')
    template_name = 'example/checks/user_has_enough_balance.html'
    max_acknowledge = 7
    trigger_update = dict(wallet=models.Wallet, user=get_user_model())
    model_class = models.Wallet

    def generate(self):
        for payload in models.Wallet.objects.all():
            yield payload

    def check(self, payload):
        config = self.get_config(payload)
        response = CheckResponse()
        response.balance = payload.balance

        # check balance for thresholds
        if payload.balance < config['critical']:
            response.set_status(Result.STATUS.critical)
        elif payload.balance < config['warning']:
            response.set_status(Result.STATUS.warning)
        else:
            response.set_status(Result.STATUS.ok)
        return response

    def get_identifier(self, payload):
        return payload.pk

    def get_payload(self, identifier):
        return models.Wallet.objects.get(pk=identifier)

    def get_payload_description(self, payload):
        return payload.user.username

    def format_result_data(self, result):
        if 'balance' in result.data:
            return ' ({balance:.2f})'.format(balance=float(result.data['balance']))
        return super(UserHasEnoughBalance, self).format_result_data(result)

    def get_wallet_payload(self, instance):
        return instance

    def get_user_payload(self, instance):
        return instance.wallet_set.first()
