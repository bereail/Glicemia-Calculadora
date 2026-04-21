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

    ESCALAMIENTO_CHOICES = [
        ("normal", "Normal"),
        ("persistente", "Hiperglucemia persistente"),
        ("refractaria", "Hiperglucemia refractaria"),
    ]

    ALGORITMO_CHOICES = [
        ("", "Sin algoritmo"),
        ("Algoritmo 1", "Algoritmo 1"),
        ("Algoritmo 2", "Algoritmo 2"),
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
    tercera_medicion = models.PositiveIntegerField(null=True, blank=True)

    infusion_activa = models.BooleanField(default=False)
    hubo_ajuste_insulina = models.BooleanField(default=False)

    modo = models.CharField(
        max_length=20,
        choices=MODO_CHOICES,
        default="seguimiento",
    )

    horas_desde_inicio = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Horas desde el inicio o reinicio de la insulinización EV.",
    )
    estable = models.BooleanField(
        default=False,
        help_text="Indica si el paciente permanece estable para espaciar controles.",
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
    algoritmo_usado = models.CharField(
        max_length=20,
        choices=ALGORITMO_CHOICES,
        blank=True,
        default="",
    )
    velocidad_sugerida = models.CharField(max_length=30, blank=True)
    bolo_ui = models.CharField(max_length=30, blank=True)
    tasa_inicial_ui_h = models.CharField(max_length=30, blank=True)
    tasa_algoritmo = models.CharField(max_length=30, blank=True)

    escalon_algoritmo = models.CharField(
        max_length=30,
        blank=True,
        help_text="Ej.: 120-149, 150-179, 180-209, >360, etc.",
    )

    escalamiento_clinico = models.CharField(
        max_length=20,
        choices=ESCALAMIENTO_CHOICES,
        default="normal",
    )

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