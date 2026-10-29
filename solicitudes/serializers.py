from django.utils import timezone
from rest_framework import serializers

from .models import Solicitud


class SolicitudSerializer(serializers.ModelSerializer):

    class Meta:
        model = Solicitud
        fields = '__all__'
        read_only_fields = [
            'id',
            'fecha_solicitud',
            'estado'
        ]

    def validate_motivo(self, value):

        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                'El motivo debe tener al menos 10 caracteres.'
            )

        return value.strip()

    def validate(self, data):

        if 'estado' in self.initial_data:
            raise serializers.ValidationError({
                'estado': 'El estado solo cambia al evaluar la solicitud.'
            })

        estudiante = data.get(
            'estudiante',
            self.instance.estudiante if self.instance else None
        )

        convocatoria = data.get(
            'convocatoria',
            self.instance.convocatoria if self.instance else None
        )

        if self.instance:

            if self.instance.estado != 'PENDIENTE':
                raise serializers.ValidationError(
                    'Solo se pueden editar solicitudes pendientes.'
                )

            if (
                estudiante != self.instance.estudiante
                or convocatoria != self.instance.convocatoria
            ):
                raise serializers.ValidationError(
                    'No se puede cambiar el estudiante ni la convocatoria.'
                )

        else:

            if not estudiante.activo:
                raise serializers.ValidationError({
                    'estudiante': 'El estudiante está inactivo.'
                })

            hoy = timezone.localdate()

            if (
                not convocatoria.activa
                or not (
                    convocatoria.fecha_inicio
                    <= hoy
                    <= convocatoria.fecha_fin
                )
            ):
                raise serializers.ValidationError({
                    'convocatoria': 'La convocatoria no está abierta.'
                })

            if Solicitud.objects.filter(
                estudiante=estudiante,
                convocatoria=convocatoria
            ).exists():
                raise serializers.ValidationError(
                    'Ya existe una solicitud para esta convocatoria.'
                )

        return data