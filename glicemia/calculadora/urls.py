from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("calculadora-guiada/", views.calculadora_guiada, name="guiada"),
    path("historial/", views.historial, name="historial"),
    path("historial/exportar/excel/", views.exportar_historial_excel, name="exportar_historial_excel"),
    path("historial/exportar/pdf/", views.exportar_historial_pdf, name="exportar_historial_pdf"),
]