from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Estudiante
from .serializers import EstudianteSerializer


# Prueba del serializer
class EstudianteSerializerTest(TestCase):

    def test_identificacion_corta(self):

        grupo = Group.objects.create(name='Estudiante')

        usuario = get_user_model().objects.create_user(
            username='alumna1',
            password='Clave12345!'
        )
        usuario.groups.add(grupo)

        datos = {
            'usuario': usuario.id,
            'identificacion': '123',
            'nombre': 'Ana',
            'apellidos': 'Mora',
            'carrera': 'Informática'
        }

        serializer = EstudianteSerializer(data=datos)

        self.assertFalse(serializer.is_valid())
        self.assertIn('identificacion', serializer.errors)


# Pruebas de la API
class EstudianteAPITest(APITestCase):

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

        self.usuario2 = Usuario.objects.create_user(
            username='alumno2',
            password='Clave12345!'
        )
        self.usuario2.groups.add(grupo)

        Estudiante.objects.create(
            usuario=self.usuario,
            identificacion='123456789',
            nombre='Ana',
            apellidos='Mora',
            carrera='Informática'
        )

        Estudiante.objects.create(
            usuario=self.usuario2,
            identificacion='987654321',
            nombre='Luis',
            apellidos='Rojas',
            carrera='Administración'
        )

        self.url = '/api/estudiantes/'

    def test_rechaza_sin_autenticacion(self):

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_admin_crea_estudiante(self):

        self.client.force_authenticate(user=self.admin)

        usuario3 = get_user_model().objects.create_user(
            username='alumna3',
            password='Clave12345!'
        )

        usuario3.groups.add(
            Group.objects.get(name='Estudiante')
        )

        datos = {
            'usuario': usuario3.id,
            'identificacion': '555666777',
            'nombre': 'María',
            'apellidos': 'Rojas',
            'carrera': 'Contabilidad'
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

        self.assertEqual(Estudiante.objects.count(), 3)

    def test_paginacion_estudiantes(self):

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            '/api/estudiantes/?page=1&page_size=1'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(response.data['count'], 2)

        self.assertEqual(
            len(response.data['results']),
            1
        )