from rest_framework import serializers
from .models import Estudiante


class EstudianteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Estudiante
        fields = '__all__'
        read_only_fields = ['id']

    def validate_identificacion(self, value):

        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError(
                'La identificación debe tener al menos 5 caracteres.'
            )

        return value

    def validate_nombre(self, value):

        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )

        return value.strip()

    def validate(self, data):

        usuario = data.get(
            'usuario',
            self.instance.usuario if self.instance else None
        )

        if self.instance and usuario != self.instance.usuario:
            raise serializers.ValidationError({
                'usuario': 'No se puede cambiar el usuario del estudiante.'
            })

        if usuario and not usuario.groups.filter(
            name='Estudiante'
        ).exists():
            raise serializers.ValidationError({
                'usuario': 'El usuario debe pertenecer al grupo Estudiante.'
            })

        return data