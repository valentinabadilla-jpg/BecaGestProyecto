from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Asignacion
from .serializers import AsignacionSerializer

from becagest.permisos import es_encargado


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lista_asignaciones(request):

    if request.method == 'GET':

        asignaciones = Asignacion.objects.select_related(
            'evaluacion__solicitud__estudiante'
        ).order_by('id')

        if not es_encargado(request.user):

            asignaciones = asignaciones.filter(
                evaluacion__solicitud__estudiante__usuario=request.user
            )

        else:

            estado = request.query_params.get('estado')

            if estado:
                asignaciones = asignaciones.filter(
                    estado=estado
                )

        serializer = AsignacionSerializer(
            asignaciones,
            many=True
        )

        return Response(serializer.data)

    if request.method == 'POST':

        if not es_encargado(request.user):
            return Response(
                {'error': 'Solo el encargado o administrador puede asignar becas.'},
                status=403
            )

        serializer = AsignacionSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

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
def detalle_asignacion(request, pk):

    try:
        asignacion = Asignacion.objects.select_related(
            'evaluacion__solicitud__estudiante'
        ).get(pk=pk)

    except Asignacion.DoesNotExist:
        return Response(
            {'error': 'Asignación no encontrada.'},
            status=404
        )

    if request.method == 'GET':

        if (
            not es_encargado(request.user)
            and asignacion.evaluacion.solicitud.estudiante.usuario_id
            != request.user.id
        ):
            return Response(
                {'error': 'No tienes permiso para consultar esta asignación.'},
                status=403
            )

        serializer = AsignacionSerializer(
            asignacion
        )

        return Response(serializer.data)

    if not es_encargado(request.user):
        return Response(
            {'error': 'No tienes permiso para modificar asignaciones.'},
            status=403
        )

    if request.method in ['PUT', 'PATCH']:

        serializer = AsignacionSerializer(
            asignacion,
            data=request.data,
            partial=(request.method == 'PATCH')
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data
            )

        return Response(
            serializer.errors,
            status=400
        )

    if request.method == 'DELETE':

        asignacion.delete()

        return Response(status=204)