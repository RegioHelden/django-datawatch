# -*- coding: UTF-8 -*-
from django.conf.urls import url

from django_datawatch import views

urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='django_datawatch_index'),
    url(r'^result/(?P<pk>\d+)/$', views.ResultView.as_view(), name='django_datawatch_result'),
    url(r'^result/(?P<pk>\d+)/acknowledge/$', views.ResultAcknowledgeView.as_view(),
        name='django_datawatch_result_acknowledge'),
    url(r'^result/(?P<pk>\d+)/config/$', views.ResultConfigView.as_view(), name='django_datawatch_result_config'),
    url(r'^result/(?P<pk>\d+)/refresh/$', views.ResultRefreshView.as_view(), name='django_datawatch_result_refresh'),
]
