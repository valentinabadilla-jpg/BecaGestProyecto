from rest_framework import serializers
from .models import Evaluacion


class EvaluacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Evaluacion
        fields = '__all__'

        read_only_fields = [
            'id',
            'fecha_evaluacion'
        ]

    def validate_puntaje(self, value):

        if value > 100:
            raise serializers.ValidationError(
                'El puntaje debe estar entre 0 y 100.'
            )

        return value

    def validate(self, data):

        solicitud = data.get(
            'solicitud',
            self.instance.solicitud if self.instance else None
        )

        if self.instance:

            if solicitud != self.instance.solicitud:
                raise serializers.ValidationError(
                    'No se puede cambiar la solicitud evaluada.'
                )

            if hasattr(self.instance, 'asignacion'):
                raise serializers.ValidationError(
                    'No se puede modificar una evaluación con beca asignada.'
                )

        else:

            if solicitud.estado != 'PENDIENTE':
                raise serializers.ValidationError(
                    'Solo se pueden evaluar solicitudes pendientes.'
                )

        return data