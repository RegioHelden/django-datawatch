# -*- coding: UTF-8 -*-
from django.urls import path

from django_datawatch import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='django_datawatch_index'),
    path('result/<int:pk>/', views.ResultView.as_view(), name='django_datawatch_result'),
    path('result/<int:pk>/acknowledge/', views.ResultAcknowledgeView.as_view(),
        name='django_datawatch_result_acknowledge'),
    path('result/<int:pk>/config/', views.ResultConfigView.as_view(), name='django_datawatch_result_config'),
    path('result/<int:pk>/refresh/', views.ResultRefreshView.as_view(), name='django_datawatch_result_refresh'),
]
