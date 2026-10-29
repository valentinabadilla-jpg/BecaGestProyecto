from django.db import transaction

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Evaluacion
from .serializers import EvaluacionSerializer

from becagest.permisos import es_encargado


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lista_evaluaciones(request):

    if request.method == 'GET':

        evaluaciones = Evaluacion.objects.select_related(
            'solicitud__estudiante'
        ).order_by('id')

        if not es_encargado(request.user):

            evaluaciones = evaluaciones.filter(
                solicitud__estudiante__usuario=request.user
            )

        serializer = EvaluacionSerializer(
            evaluaciones,
            many=True
        )

        return Response(serializer.data)

    if request.method == 'POST':

        if not es_encargado(request.user):
            return Response(
                {'error': 'No tienes permiso para evaluar solicitudes.'},
                status=403
            )

        serializer = EvaluacionSerializer(
            data=request.data
        )

        if serializer.is_valid():

            with transaction.atomic():

                evaluacion = serializer.save()

                solicitud = evaluacion.solicitud

                solicitud.estado = evaluacion.resultado

                solicitud.save()

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_evaluacion(request, pk):

    try:
        evaluacion = Evaluacion.objects.select_related(
            'solicitud__estudiante'
        ).get(pk=pk)

    except Evaluacion.DoesNotExist:
        return Response(
            {'error': 'Evaluación no encontrada.'},
            status=404
        )

    if request.method == 'GET':

        if (
            not es_encargado(request.user)
            and evaluacion.solicitud.estudiante.usuario_id
            != request.user.id
        ):
            return Response(
                {'error': 'No tienes permiso.'},
                status=403
            )

        serializer = EvaluacionSerializer(
            evaluacion
        )

        return Response(serializer.data)

    if not es_encargado(request.user):
        return Response(
            {'error': 'Solo el personal autorizado puede modificar evaluaciones.'},
            status=403
        )

    if hasattr(evaluacion, 'asignacion'):
        return Response(
            {'error': 'No se puede modificar una evaluación con asignación.'},
            status=409
        )

    if request.method in ['PUT', 'PATCH']:

        serializer = EvaluacionSerializer(
            evaluacion,
            data=request.data,
            partial=(request.method == 'PATCH')
        )

        if serializer.is_valid():

            with transaction.atomic():

                actualizada = serializer.save()

                solicitud = actualizada.solicitud

                solicitud.estado = actualizada.resultado

                solicitud.save()

            return Response(
                serializer.data
            )

        return Response(
            serializer.errors,
            status=400
        )

    if request.method == 'DELETE':

        with transaction.atomic():

            solicitud = evaluacion.solicitud

            evaluacion.delete()

            solicitud.estado = 'PENDIENTE'

            solicitud.save()

        return Response(status=204)