from django.contrib import admin

from .models import MedicionGlucemia


@admin.register(MedicionGlucemia)
class MedicionGlucemiaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha_hora",
        "glicemia_actual",
        "glicemia_previa",
        "usuario",
        "estado",
        "subestado",
        "clase",
        "infusion_activa",
        "requiere_recontrol",
    )

    list_filter = (
        "estado",
        "clase",
        "infusion_activa",
        "requiere_recontrol",
        "fecha_hora",
    )

    search_fields = (
        "usuario__username",
        "estado",
        "subestado",
        "mensaje",
        "conducta",
    )

    ordering = ("-fecha_hora",)
    readonly_fields = ("fecha_hora",)
