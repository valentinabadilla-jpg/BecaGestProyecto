from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from estudiantes.models import Estudiante
from convocatorias.models import Convocatoria
from solicitudes.models import Solicitud
from evaluaciones.models import Evaluacion

from .models import Asignacion


class AsignacionAPITest(APITestCase):

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

        self.usuario2 = Usuario.objects.create_user(
            username='alumno2',
            password='Clave12345!'
        )
        self.usuario2.groups.add(grupo_estudiante)

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
            cupos=1,
            activa=True
        )

        self.solicitud = Solicitud.objects.create(
            estudiante=self.estudiante,
            convocatoria=self.convocatoria,
            motivo='Necesito apoyo económico',
            estado='APROBADA'
        )

        self.solicitud2 = Solicitud.objects.create(
            estudiante=self.estudiante2,
            convocatoria=self.convocatoria,
            motivo='Necesito apoyo para estudiar',
            estado='APROBADA'
        )

        self.evaluacion = Evaluacion.objects.create(
            solicitud=self.solicitud,
            resultado='APROBADA',
            puntaje=90,
            observaciones='Cumple requisitos'
        )

        self.evaluacion2 = Evaluacion.objects.create(
            solicitud=self.solicitud2,
            resultado='APROBADA',
            puntaje=85,
            observaciones='Cumple requisitos'
        )

        self.url = '/api/asignaciones/'

    def datos_asignacion(self):

        return {
            'evaluacion': self.evaluacion.id,
            'monto_mensual': '50000.00',
            'estado': 'ACTIVA'
        }

    def test_encargado_crea_modifica_y_elimina(self):

        self.client.force_authenticate(user=self.encargado)

        response = self.client.post(
            self.url,
            self.datos_asignacion(),
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        asignacion_id = response.data['id']
        url = f'/api/asignaciones/{asignacion_id}/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        response = self.client.patch(
            url,
            {'monto_mensual': '60000.00'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        asignacion = Asignacion.objects.get(
            id=asignacion_id
        )

        self.assertEqual(
            asignacion.monto_mensual,
            Decimal('60000.00')
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_no_asigna_solicitud_rechazada(self):

        self.evaluacion.resultado = 'RECHAZADA'
        self.evaluacion.save()

        self.solicitud.estado = 'RECHAZADA'
        self.solicitud.save()

        self.client.force_authenticate(user=self.encargado)

        response = self.client.post(
            self.url,
            self.datos_asignacion(),
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_no_permite_superar_cupos(self):

        Asignacion.objects.create(
            evaluacion=self.evaluacion,
            monto_mensual=50000
        )

        self.client.force_authenticate(user=self.encargado)

        datos = {
            'evaluacion': self.evaluacion2.id,
            'monto_mensual': '30000.00',
            'estado': 'ACTIVA'
        }

        response = self.client.post(
            self.url,
            datos,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_estudiante_no_puede_asignar_beca(self):

        self.client.force_authenticate(user=self.usuario)

        response = self.client.post(
            self.url,
            self.datos_asignacion(),
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )