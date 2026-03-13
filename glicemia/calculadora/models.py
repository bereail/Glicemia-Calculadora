from django.db import models
from django.contrib.auth.models import User


class MedicionGlucemia(models.Model):
    MODO_CHOICES = [
        ("inicio", "Inicio / Reinicio (Algoritmo 1)"),
        ("alg2", "Seguimiento - Algoritmo 2"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    glucemia = models.IntegerField()
    modo = models.CharField(max_length=20, choices=MODO_CHOICES)

    infusion_activa = models.BooleanField(default=False)
    glucemia_previa = models.IntegerField(null=True, blank=True)

    estado = models.CharField(max_length=100)
    clase = models.CharField(max_length=30)
    conducta = models.CharField(max_length=255)
    mensaje = models.TextField(blank=True)
    proximo_control = models.CharField(max_length=255, blank=True)
    observacion = models.CharField(max_length=255, blank=True)
    tendencia = models.CharField(max_length=50, blank=True)

    algoritmo_usado = models.CharField(max_length=100, blank=True)
    velocidad_sugerida = models.CharField(max_length=30, blank=True)
    bolo_ui = models.CharField(max_length=30, blank=True)
    tasa_inicial_ui_h = models.CharField(max_length=30, blank=True)

    alerta_hgr = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fecha_hora:%d/%m/%Y %H:%M} - {self.glucemia} mg/dL - {self.usuario.username}"