# -*- coding: UTF-8 -*-
from django.conf.urls import url

from django_monitoring import views

urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='django_monitoring_index'),
    url(r'^result/(?P<pk>\d+)/$', views.ResultView.as_view(), name='django_monitoring_result'),
    url(r'^result/(?P<pk>\d+)/acknowledge/$', views.ResultAcknowledgeView.as_view(),
        name='django_monitoring_result_acknowledge'),
    url(r'^result/(?P<pk>\d+)/config/$', views.ResultConfigView.as_view(), name='django_monitoring_result_config'),
    url(r'^result/(?P<pk>\d+)/refresh/$', views.ResultRefreshView.as_view(), name='django_monitoring_result_refresh'),
]
