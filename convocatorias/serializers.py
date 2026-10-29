from rest_framework import serializers
from .models import Convocatoria


class ConvocatoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Convocatoria
        fields = '__all__'

    def validate_cupos(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                'Los cupos deben ser mayores que cero.'
            )

        return value

    def validate(self, data):

        inicio = data.get(
            'fecha_inicio',
            self.instance.fecha_inicio if self.instance else None
        )

        fin = data.get(
            'fecha_fin',
            self.instance.fecha_fin if self.instance else None
        )

        if inicio and fin and fin < inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha final no puede ser anterior a la inicial.'
            })

        if self.instance:

            cupos = data.get(
                'cupos',
                self.instance.cupos
            )

            asignaciones = self.instance.solicitudes.filter(
                evaluacion__asignacion__estado__in=[
                    'ACTIVA',
                    'FINALIZADA'
                ]
            ).count()

            if asignaciones > cupos:
                raise serializers.ValidationError({
                    'cupos': 'No puedes colocar menos cupos que las becas asignadas.'
                })

        return data