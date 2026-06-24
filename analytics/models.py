from django.contrib.auth.models import User
from django.db import models


class VisitaWeb(models.Model):
    ip = models.GenericIPAddressField(unpack_ipv4=True)
    usuario = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="visitas_web",
    )
    username_display = models.CharField(max_length=150, blank=True)
    pagina = models.CharField(max_length=500)
    metodo = models.CharField(max_length=10, default="GET")
    user_agent = models.TextField(blank=True)
    referrer = models.CharField(max_length=500, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    duracion_segundos = models.IntegerField(null=True, blank=True)
    es_movil = models.BooleanField(default=False)
    navegador = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Visita web"
        verbose_name_plural = "Visitas web"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["ip"]),
            models.Index(fields=["usuario"]),
        ]

    def __str__(self):
        return f"{self.timestamp:%d/%m/%Y %H:%M} — {self.ip} — {self.pagina}"
