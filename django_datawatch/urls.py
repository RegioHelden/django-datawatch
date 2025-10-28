from django.urls import path

from django_datawatch import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="django_datawatch_index"),
    path("result/<int:pk>/", views.ResultView.as_view(), name="django_datawatch_result"),
    path(
        "result/<int:pk>/acknowledge/",
        views.ResultAcknowledgeView.as_view(),
        name="django_datawatch_result_acknowledge",
    ),
    path("result/<int:pk>/config/", views.ResultConfigView.as_view(), name="django_datawatch_result_config"),
    path("result/<int:pk>/tags/", views.ResultTagManageView.as_view(), name="django_datawatch_result_tags"),
    path(
        "result/<int:result_pk>/tags/add/",
        views.ResultTagView.as_view(action="add"),
        name="django_datawatch_result_tag_add",
    ),
    path(
        "result/<int:result_pk>/tags/<int:tag_pk>/edit/",
        views.ResultTagView.as_view(action="edit"),
        name="django_datawatch_result_tag_edit",
    ),
    path(
        "result/<int:result_pk>/tags/<int:tag_pk>/delete/",
        views.ResultTagView.as_view(action="delete"),
        name="django_datawatch_result_tag_delete",
    ),
    path("result/<int:pk>/refresh/", views.ResultRefreshView.as_view(), name="django_datawatch_result_refresh"),
]
