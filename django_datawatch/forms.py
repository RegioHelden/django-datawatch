# -*- coding: UTF-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from model_utils.choices import Choices

from django_datawatch.models import Result


class ResultFilterForm(forms.Form):
    STATUS_CHOICES = Choices((0, 'all', _('All')), (1, 'failed', _('Failed')))

    user = forms.ModelChoiceField(queryset=get_user_model().objects.all().order_by('first_name', 'last_name'),
                                  label=_('User'), required=False)
    status = forms.TypedChoiceField(coerce=int, choices=STATUS_CHOICES, label=_('Status'),
                                    initial=STATUS_CHOICES.failed)

    def __init__(self, user, group_filter=None, **kwargs):
        super(ResultFilterForm, self).__init__(**kwargs)

        if not group_filter:
            group_filter = dict()

        self.fields['user'].initial = user
        self.fields['user'].queryset = self.fields['user'].queryset.filter(**group_filter)

    def filter_queryset(self, request, queryset):
        # default values if form has not been submitted
        if not self.is_bound:
            return queryset.failed().unacknowledged().for_user(request.user)
        # form has been submitted with invalid values
        if not self.is_valid():
            return queryset.none()

        if self.cleaned_data['user']:
            queryset = queryset.for_user(self.cleaned_data['user'])
        if self.cleaned_data['status']:
            if self.cleaned_data['status'] == self.STATUS_CHOICES.failed:
                queryset = queryset.failed().unacknowledged()

        return queryset.distinct()


class AcknowledgeForm(forms.ModelForm):
    days = forms.IntegerField(label=_('Days to acknowledge'))

    class Meta:
        model = Result
        fields = ['days', 'acknowledged_reason']

    def __init__(self, user, **kwargs):
        self.user = user
        super(AcknowledgeForm, self).__init__(**kwargs)

    def save(self, commit=True):
        self.instance.acknowledge(user=self.user, days=self.cleaned_data.get('days'),
                                  reason=self.cleaned_data['acknowledged_reason'], commit=commit)
        return self.instance
