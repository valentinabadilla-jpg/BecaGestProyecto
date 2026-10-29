from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from estudiantes.models import Estudiante
from convocatorias.models import Convocatoria

from .models import Solicitud


class SolicitudAPITest(APITestCase):

    def setUp(self):

        Usuario = get_user_model()

        grupo = Group.objects.create(name='Estudiante')

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

        self.estudiante = Estudiante.objects.create(
            usuario=self.usuario,
            identificacion='123456789',
            nombre='Ana',
            apellidos='Mora',
            carrera='Informática'
        )

        self.estudiante2 = Estudiante.objects.create(
            usuario=self.usuario2,
            identificacion='987654321',
            nombre='Luis',
            apellidos='Rojas',
            carrera='Administración'
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

        self.url = '/api/solicitudes/'

    def datos_solicitud(self):

        return {
            'estudiante': self.estudiante.id,
            'convocatoria': self.convocatoria.id,
            'motivo': 'Necesito apoyo económico para estudiar.'
        }

    def test_estudiante_crea_solicitud(self):

        self.client.force_authenticate(user=self.usuario)

        response = self.client.post(
            self.url,
            self.datos_solicitud(),
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(Solicitud.objects.count(), 1)

    def test_no_permite_solicitud_duplicada(self):

        Solicitud.objects.create(
            estudiante=self.estudiante,
            convocatoria=self.convocatoria,
            motivo='Primera solicitud de apoyo'
        )

        self.client.force_authenticate(user=self.usuario)

        response = self.client.post(
            self.url,
            self.datos_solicitud(),
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_no_permite_cambiar_estado_por_patch(self):

        solicitud = Solicitud.objects.create(
            estudiante=self.estudiante,
            convocatoria=self.convocatoria,
            motivo='Necesito apoyo económico'
        )

        self.client.force_authenticate(user=self.usuario)

        url = f'/api/solicitudes/{solicitud.id}/'

        response = self.client.patch(
            url,
            {'estado': 'APROBADA'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'PENDIENTE')

        solicitud.estado = 'APROBADA'
        solicitud.save()

        response = self.client.patch(
            url,
            {'motivo': 'Cambio en el motivo de la solicitud'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT
        )

    def test_estudiante_no_ve_solicitud_ajena(self):

        solicitud = Solicitud.objects.create(
            estudiante=self.estudiante2,
            convocatoria=self.convocatoria,
            motivo='Necesito apoyo para estudiar'
        )

        self.client.force_authenticate(user=self.usuario)

        response = self.client.get(
            f'/api/solicitudes/{solicitud.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )