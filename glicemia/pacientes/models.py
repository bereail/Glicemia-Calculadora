from django.db import models
from django.contrib.auth.models import User


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    historia_clinica = models.CharField(max_length=50, unique=True)
    servicio = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.historia_clinica})"


class RegistroGlucemia(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="registros"
    )
    valor = models.IntegerField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    algoritmo = models.IntegerField(default=1)  # 1 o 2

    escalon = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.paciente} - {self.valor} mg/dL"