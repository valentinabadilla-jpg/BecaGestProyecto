from django.db import models


class Asignacion(models.Model):

    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    evaluacion = models.OneToOneField(
        'evaluaciones.Evaluacion',
        on_delete=models.PROTECT,
        related_name='asignacion'
    )

    monto_mensual = models.DecimalField(
        max_digits=9,
        decimal_places=2
    )

    fecha_asignacion = models.DateField(
        auto_now_add=True
    )

    estado = models.CharField(
        max_length=12,
        choices=ESTADOS,
        default='ACTIVA'
    )

    def __str__(self):
        return f'Asignación {self.id}'