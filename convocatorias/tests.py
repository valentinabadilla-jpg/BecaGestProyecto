from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Convocatoria
from .serializers import ConvocatoriaSerializer


# Prueba del serializer
class ConvocatoriaSerializerTest(TestCase):

    def test_fechas_invalidas(self):

        hoy = timezone.localdate()

        datos = {
            'nombre': 'Beca Transporte',
            'descripcion': 'Apoyo económico',
            'fecha_inicio': str(hoy + timedelta(days=10)),
            'fecha_fin': str(hoy),
            'cupos': 5,
            'activa': True
        }

        serializer = ConvocatoriaSerializer(data=datos)

        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_fin', serializer.errors)


# Pruebas de la API
class ConvocatoriaAPITest(APITestCase):

    def setUp(self):

        Usuario = get_user_model()

        grupo = Group.objects.create(name='Estudiante')

        self.admin = Usuario.objects.create_superuser(
            username='admin_test',
            password='Clave12345!'
        )

        self.usuario = Usuario.objects.create_user(
            username='alumna1',
            password='Clave12345!'
        )
        self.usuario.groups.add(grupo)

        hoy = timezone.localdate()

        self.convocatoria = Convocatoria.objects.create(
            nombre='Beca Transporte',
            descripcion='Apoyo para transporte',
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            cupos=5,
            activa=True
        )

        self.url = '/api/convocatorias/'

    def test_admin_crea_convocatoria(self):

        self.client.force_authenticate(user=self.admin)

        hoy = timezone.localdate()

        datos = {
            'nombre': 'Beca Alimentación',
            'descripcion': 'Apoyo alimentario',
            'fecha_inicio': str(hoy),
            'fecha_fin': str(hoy + timedelta(days=20)),
            'cupos': 10,
            'activa': True
        }

        response = self.client.post(
            self.url,
            datos,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_admin_modifica_y_elimina_convocatoria(self):

        self.client.force_authenticate(user=self.admin)

        url = f'/api/convocatorias/{self.convocatoria.id}/'

        response = self.client.patch(
            url,
            {'cupos': 15},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.convocatoria.refresh_from_db()
        self.assertEqual(self.convocatoria.cupos, 15)

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_estudiante_no_crea_convocatoria(self):

        self.client.force_authenticate(user=self.usuario)

        hoy = timezone.localdate()

        datos = {
            'nombre': 'Beca Nueva',
            'descripcion': 'Apoyo económico',
            'fecha_inicio': str(hoy),
            'fecha_fin': str(hoy + timedelta(days=30)),
            'cupos': 5
        }

        response = self.client.post(
            self.url,
            datos,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
