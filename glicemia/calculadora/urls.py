from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.control_glicemia, name="control_glicemia"),
    path("historial/", views.historial, name="historial"),
    path(
        "historial/exportar/excel/",
        views.exportar_historial_excel,
        name="exportar_historial_excel",
    ),
    path(
        "historial/exportar/pdf/",
        views.exportar_historial_pdf,
        name="exportar_historial_pdf",
    ),
    path("logout/", LogoutView.as_view(next_page="/login/"), name="logout"),
]
