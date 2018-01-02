# -*- coding: UTF-8 -*-
from six import iteritems

from django.db.models.base import Model
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView


class FilteredListView(FormMixin, ListView):
    SESSION_KEY = 'datawatch_search_term'

    def get_form_kwargs(self):
        form_data = self.request.session.get(self.SESSION_KEY, None)
        return {
          'initial': self.get_initial(),
          'prefix': self.get_prefix(),
          'data': self.request.GET or form_data
        }

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        form = self.get_form(self.get_form_class())
        self.object_list = form.filter_queryset(request, self.object_list)
        if form.is_valid():
            form_data = dict()
            for k, v in iteritems(form.cleaned_data):
                if isinstance(v, Model):
                    v = v.pk
                form_data[k] = v
            self.request.session[self.SESSION_KEY] = dict(form_data)

        context = self.get_context_data(form=form, object_list=self.object_list)
        return self.render_to_response(context)
