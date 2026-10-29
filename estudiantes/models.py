from django.db import models
from django.conf import settings


class Estudiante(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ficha_estudiante'
    )

    identificacion = models.CharField(
        max_length=30,
        unique=True
    )

    nombre = models.CharField(max_length=100)

    apellidos = models.CharField(max_length=100)

    carrera = models.CharField(max_length=120)

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre + ' ' + self.apellidos
