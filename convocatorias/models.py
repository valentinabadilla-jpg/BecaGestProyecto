from django.db import models


class Convocatoria(models.Model):

    nombre = models.CharField(max_length=120)

    descripcion = models.CharField(max_length=250)

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    cupos = models.PositiveIntegerField()

    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre