import logging
from typing import Any, cast

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView, UpdateView

from django_datawatch import forms
from django_datawatch.common.views import FilteredListView
from django_datawatch.datawatch import datawatch
from django_datawatch.defaults import defaults
from django_datawatch.models import AlreadyAcknowledgedError, Result, ResultTag

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, FilteredListView):
    form_class = forms.ResultFilterForm
    permission_required = "django_datawatch.view"
    template_name = "django_datawatch/dashboard.html"
    context_object_name = "results"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = Result.objects.all().prefetch_related("resulttag_set").order_by("-status")
        return self.queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"check": Result})
        return ctx


class ResultView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "django_datawatch.view"
    model = Result
    template_name = "django_datawatch/detail.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_instance = None

    def get_check_instance(self):
        if not self.check_instance:
            self.check_instance = self.object.get_check_instance()
        return self.check_instance

    def get_context_data(self, **kwargs):
        kwargs.update(result=self.object)
        ctx = super().get_context_data(**kwargs)
        ctx["datawatch_show_debug_info"] = self.request.user.is_superuser and getattr(
            settings,
            "DJANGO_DATAWATCH_SHOW_ADMIN_DEBUG",
            defaults["SHOW_ADMIN_DEBUG"],
        )
        ctx.update(self.get_check_instance().get_context_data(self.object))
        return ctx

    def get_template_names(self):
        template_names = super().get_template_names()
        check_template = self.get_check_instance().get_template_name()
        if check_template:
            return [check_template, *template_names]
        return template_names

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.add_message(self.request, messages.WARNING, _("Check result does not exist (anymore)"))
            return HttpResponseRedirect(redirect_to=reverse_lazy("django_datawatch_index"))


class ResultAcknowledgeView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "django_datawatch.acknowledge"
    form_class = forms.AcknowledgeForm
    model = Result
    template_name = "django_datawatch/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("django_datawatch_index")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"action": _("Acknowledge")})
        return ctx

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.add_message(self.request, messages.INFO, _("Successfully acknowledged"))
        except AlreadyAcknowledgedError:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("This check is already acknowledged for a longer period"),
            )
            response = HttpResponseRedirect(self.get_success_url())

        return response


class ResultConfigView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, FormView):
    permission_required = "django_datawatch.config"
    model = Result
    template_name = "django_datawatch/form.html"

    def __init__(self, **kwargs):
        self.object = None
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_class(self):
        return self.object.get_check_instance().get_form_class()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object.config:
            kwargs.update({"initial": self.object.config})
        return kwargs

    def get_success_url(self):
        return reverse_lazy("django_datawatch_result", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"action": _("Save")})
        return ctx

    def form_valid(self, form):
        cast(Any, form).save(instance=self.object)
        check = self.object.get_check_instance()

        datawatch.get_backend().run(
            slug=check.slug,
            identifier=check.get_identifier(self.object),
            run_async=False,
            queue=check.queue,
        )
        return super().form_valid(form)


class ResultRefreshView(LoginRequiredMixin, PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    permission_required = "django_datawatch.refresh"
    permanent = False
    model = Result

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = {}
        self.object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super().get(request, *args, **kwargs)
        check = self.object.get_check_instance()
        datawatch.get_backend().run(
            slug=check.slug,
            identifier=self.object.identifier,
            run_async=False,
            user_forced_refresh=True,
            queue=check.queue,
        )
        messages.add_message(request, messages.INFO, _("Result has been refreshed"))
        return response

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("django_datawatch_result", kwargs={"pk": self.object.pk})


class ResultTagManageView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Result
    form_class = forms.ResultTagForm
    template_name = "django_datawatch/tags_manage.html"
    permission_required = "django_datawatch.tag"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user, "result": self.object})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "result": self.object,
                "tags": self.object.resulttag_set.select_related("user").all(),
            },
        )
        return context


class ResultTagView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = ResultTag
    form_class = forms.ResultTagForm
    pk_url_kwarg = "tag_pk"
    action = None
    permission_required = "django_datawatch.tag"
    template_name = "django_datawatch/form.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def get_result(self):
        result_pk = self.kwargs.get("result_pk")
        return get_object_or_404(Result, pk=result_pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user, "result": self.get_result()})
        if self.action == "edit":
            kwargs["instance"] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = _("Save")
        return context

    def form_valid(self, form):
        form.save()
        messages.info(self.request, _("Tag saved"))
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        # handle delete as a POST without a form
        if self.action == "delete":
            tag = self.get_object()
            result_pk = tag.result.pk
            tag.delete()
            messages.info(request, _("Tag deleted"))
            return HttpResponseRedirect(reverse_lazy("django_datawatch_result_tags", kwargs={"pk": result_pk}))
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("django_datawatch_result_tags", kwargs={"pk": self.get_result().pk})
