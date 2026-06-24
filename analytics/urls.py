from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.panel_admin, name="panel_admin"),
    path("ping/", views.ping_visita, name="ping_visita"),
]
