# -*- coding: UTF-8 -*-
import logging

from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView, FormView
from django.contrib import messages

from django_datawatch import forms
from django_datawatch.common.views import FilteredListView
from django_datawatch.models import Check
from django_datawatch.settings import ddw_settings
from django_datawatch.tasks import django_datawatch_run

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, FilteredListView):
    form_class = forms.ResultFilterForm
    permission_required = 'django_datawatch.view'
    template_name = 'django_datawatch/dashboard.html'
    context_object_name = 'results'

    def get_form_kwargs(self):
        kwargs = super(DashboardView, self).get_form_kwargs()
        kwargs.update(dict(user=self.request.user))
        return kwargs

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = Check.objects.all().order_by('-status')
        return self.queryset

    def get_context_data(self, **kwargs):
        ctx = super(DashboardView, self).get_context_data(**kwargs)
        ctx.update(dict(check=Check))
        return ctx


class ResultView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'django_datawatch.view'
    model = Check
    template_name = 'django_datawatch/detail.html'

    def __init__(self, *args, **kwargs):
        super(ResultView, self).__init__(*args, **kwargs)
        self.check_instance = None

    def get_check_instance(self):
        if not self.check_instance:
            self.check_instance = self.object.get_check_instance()
        return self.check_instance

    def get_context_data(self, **kwargs):
        kwargs.update(result=self.object)
        ctx = super(ResultView, self).get_context_data(**kwargs)
        ctx.update(self.get_check_instance().get_context_data(self.object))
        return ctx

    def get_template_names(self):
        template_names = super(ResultView, self).get_template_names()
        check_template = self.get_check_instance().get_template_name()
        if check_template:
            return [check_template] + template_names
        return template_names


class ResultAcknowledgeView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'django_datawatch.acknowledge'
    form_class = forms.AcknowledgeForm
    model = Check
    template_name = 'django_datawatch/form.html'

    def get_form_kwargs(self):
        kwargs = super(ResultAcknowledgeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('django_datawatch_index')

    def get_context_data(self, **kwargs):
        ctx = super(ResultAcknowledgeView, self).get_context_data(**kwargs)
        ctx.update(dict(action=_('Acknowledge')))
        return ctx

    def form_valid(self, form):
        response = super(ResultAcknowledgeView, self).form_valid(form)
        messages.add_message(self.request, messages.INFO, _('Check has been successfully acknowledged'))
        return response


class ResultConfigView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, FormView):
    permission_required = 'django_datawatch.config'
    model = Check
    template_name = 'django_datawatch/form.html'

    def __init__(self, **kwargs):
        self.object = None
        super(ResultConfigView, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ResultConfigView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ResultConfigView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        return self.object.get_check_instance().get_form_class()

    def get_form_kwargs(self):
        kwargs = super(ResultConfigView, self).get_form_kwargs()
        if self.object.config:
            kwargs.update(dict(initial=self.object.config))
        return kwargs

    def get_success_url(self):
        return reverse_lazy('django_datawatch_result', kwargs=dict(pk=self.object.pk))

    def get_context_data(self, **kwargs):
        ctx = super(ResultConfigView, self).get_context_data(**kwargs)
        ctx.update(dict(action=_('Save')))
        return ctx

    def form_valid(self, form):
        form.save(instance=self.object)
        check = self.object.get_check_instance()

        django_datawatch_run.apply(kwargs=dict(check_slug=check.slug, identifier=check.get_identifier(self.object)),
                                   queue=ddw_settings.QUEUE_NAME)
        return super(ResultConfigView, self).form_valid(form)


class ResultRefreshView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    permission_required = 'django_datawatch.refresh'
    permanent = False
    model = Check

    def __init__(self, **kwargs):
        super(ResultRefreshView, self).__init__(**kwargs)
        self.kwargs = dict()
        self.object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super(ResultRefreshView, self).get(request, *args, **kwargs)
        check = self.object.get_check_instance()
        django_datawatch_run.apply(kwargs=dict(check_slug=check.slug, identifier=check.get_identifier(self.object)),
                                   queue=ddw_settings.QUEUE_NAME)
        messages.add_message(request, messages.INFO, _('Result has been refreshed'))
        return response

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('django_datawatch_result', kwargs=dict(pk=self.object.pk))
