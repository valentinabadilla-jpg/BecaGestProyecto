from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from estudiantes.models import Estudiante
from convocatorias.models import Convocatoria
from solicitudes.models import Solicitud

from .models import Evaluacion


class EvaluacionAPITest(APITestCase):

    def setUp(self):

        Usuario = get_user_model()

        grupo_estudiante = Group.objects.create(
            name='Estudiante'
        )

        grupo_encargado = Group.objects.create(
            name='Encargado'
        )

        self.usuario = Usuario.objects.create_user(
            username='alumna1',
            password='Clave12345!'
        )
        self.usuario.groups.add(grupo_estudiante)

        self.encargado = Usuario.objects.create_user(
            username='encargado1',
            password='Clave12345!'
        )
        self.encargado.groups.add(grupo_encargado)

        self.estudiante = Estudiante.objects.create(
            usuario=self.usuario,
            identificacion='123456789',
            nombre='Ana',
            apellidos='Mora',
            carrera='Informática'
        )

        hoy = timezone.localdate()

        self.convocatoria = Convocatoria.objects.create(
            nombre='Beca Transporte',
            descripcion='Apoyo económico',
            fecha_inicio=hoy - timedelta(days=1),
            fecha_fin=hoy + timedelta(days=30),
            cupos=5,
            activa=True
        )

        self.solicitud = Solicitud.objects.create(
            estudiante=self.estudiante,
            convocatoria=self.convocatoria,
            motivo='Necesito apoyo económico'
        )

        self.url = '/api/evaluaciones/'

    def datos_evaluacion(self):

        return {
            'solicitud': self.solicitud.id,
            'resultado': 'APROBADA',
            'puntaje': 90,
            'observaciones': 'Cumple los requisitos'
        }

    def test_encargado_aprueba_y_elimina_evaluacion(self):

        self.client.force_authenticate(user=self.encargado)

        response = self.client.post(
            self.url,
            self.datos_evaluacion(),
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, 'APROBADA')

        evaluacion_id = response.data['id']

        response = self.client.delete(
            f'/api/evaluaciones/{evaluacion_id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, 'PENDIENTE')

    def test_encargado_rechaza_solicitud(self):

        self.client.force_authenticate(user=self.encargado)

        datos = self.datos_evaluacion()
        datos['resultado'] = 'RECHAZADA'
        datos['puntaje'] = 30

        response = self.client.post(
            self.url,
            datos,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, 'RECHAZADA')

    def test_puntaje_invalido(self):

        self.client.force_authenticate(user=self.encargado)

        datos = self.datos_evaluacion()
        datos['puntaje'] = 150

        response = self.client.post(
            self.url,
            datos,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_estudiante_no_puede_evaluar(self):

        self.client.force_authenticate(user=self.usuario)

        response = self.client.post(
            self.url,
            self.datos_evaluacion(),
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )