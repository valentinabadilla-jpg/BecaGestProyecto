from django.db import models


class Solicitud(models.Model):

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    estudiante = models.ForeignKey(
        'estudiantes.Estudiante',
        on_delete=models.PROTECT,
        related_name='solicitudes'
    )

    convocatoria = models.ForeignKey(
        'convocatorias.Convocatoria',
        on_delete=models.PROTECT,
        related_name='solicitudes'
    )

    motivo = models.CharField(max_length=300)

    fecha_solicitud = models.DateField(
        auto_now_add=True
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='PENDIENTE'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['estudiante', 'convocatoria'],
                name='una_solicitud_por_convocatoria'
            )
        ]

    def __str__(self):
        return f'Solicitud {self.id} - {self.estudiante}'