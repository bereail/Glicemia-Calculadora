from django.contrib.auth.models import User
from django.db import models


class MedicionGlucemia(models.Model):
    """
    Guarda una evaluación de glicemia realizada por el usuario.
    """

    MODO_CHOICES = [
        ("inicio", "Inicio / Reinicio"),
        ("seguimiento", "Seguimiento"),
    ]

    CLASE_CHOICES = [
        ("hipoglucemia", "Hipoglucemia"),
        ("post_hipoglucemia", "Post-hipoglucemia"),
        ("en_rango", "En rango"),
        ("hiperglucemia", "Hiperglucemia"),
        ("sin_clasificacion", "Sin clasificación"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mediciones_glucemia",
    )

    fecha_hora = models.DateTimeField(auto_now_add=True)

    # -----------------------------
    # DATOS DE ENTRADA
    # -----------------------------
    glicemia_actual = models.PositiveIntegerField()
    glicemia_previa = models.PositiveIntegerField(null=True, blank=True)

    infusion_activa = models.BooleanField(default=False)
    hubo_ajuste_insulina = models.BooleanField(default=False)

    tercera_medicion = models.PositiveIntegerField(null=True, blank=True)

    modo = models.CharField(
        max_length=20,
        choices=MODO_CHOICES,
        default="seguimiento",
    )

    # -----------------------------
    # RESULTADO CLÍNICO
    # -----------------------------
    estado = models.CharField(max_length=100, blank=True)
    subestado = models.CharField(max_length=150, blank=True)

    clase = models.CharField(
        max_length=30,
        choices=CLASE_CHOICES,
        default="sin_clasificacion",
    )

    mensaje = models.TextField(blank=True)
    conducta = models.TextField(blank=True)
    proximo_control = models.CharField(max_length=255, blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    # -----------------------------
    # TENDENCIA
    # -----------------------------
    tendencia = models.CharField(max_length=50, blank=True)
    flecha_tendencia = models.CharField(max_length=5, blank=True)
    delta = models.CharField(max_length=20, blank=True)

    # -----------------------------
    # DATOS TERAPÉUTICOS / ALGORITMO
    # -----------------------------
    algoritmo_usado = models.CharField(max_length=100, blank=True)
    velocidad_sugerida = models.CharField(max_length=30, blank=True)
    bolo_ui = models.CharField(max_length=30, blank=True)
    tasa_inicial_ui_h = models.CharField(max_length=30, blank=True)
    tasa_algoritmo = models.CharField(max_length=30, blank=True)

    # -----------------------------
    # FLAGS CLÍNICOS
    # -----------------------------
    requiere_recontrol = models.BooleanField(default=False)
    suspender_insulina = models.BooleanField(default=False)
    administrar_dextrosa = models.BooleanField(default=False)
    reiniciar_insulina = models.BooleanField(default=False)

    alerta_hgr = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_hora"]
        verbose_name = "Medición de glicemia"
        verbose_name_plural = "Mediciones de glicemia"

    def __str__(self):
        return (
            f"{self.fecha_hora:%d/%m/%Y %H:%M} - "
            f"{self.glicemia_actual} mg/dL - "
            f"{self.usuario.username}"
        )
