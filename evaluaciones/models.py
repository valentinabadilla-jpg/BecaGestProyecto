from django.db import models


class Evaluacion(models.Model):

    RESULTADOS = [
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    solicitud = models.OneToOneField(
        'solicitudes.Solicitud',
        on_delete=models.PROTECT,
        related_name='evaluacion'
    )

    resultado = models.CharField(
        max_length=15,
        choices=RESULTADOS
    )

    puntaje = models.PositiveIntegerField()

    observaciones = models.CharField(
        max_length=300
    )

    fecha_evaluacion = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f'Evaluación {self.id} - {self.resultado}'