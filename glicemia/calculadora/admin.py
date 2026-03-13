from django.contrib import admin
from .models import MedicionGlucemia


@admin.register(MedicionGlucemia)
class MedicionGlucemiaAdmin(admin.ModelAdmin):
    list_display = (
        "fecha_hora",
        "usuario",
        "glucemia",
        "modo",
        "estado",
        "conducta",
        "tendencia",
    )
    list_filter = ("modo", "estado", "fecha_hora", "usuario")
    search_fields = ("usuario__username", "glucemia", "estado", "conducta")