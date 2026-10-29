from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Solicitud
from .serializers import SolicitudSerializer

from becagest.permisos import es_encargado, es_estudiante


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lista_solicitudes(request):

    if request.method == 'GET':

        solicitudes = Solicitud.objects.select_related(
            'estudiante',
            'convocatoria'
        ).order_by('id')

        if not es_encargado(request.user):

            solicitudes = solicitudes.filter(
                estudiante__usuario=request.user
            )

        else:

            estado = request.query_params.get('estado')
            estudiante = request.query_params.get('estudiante')
            convocatoria = request.query_params.get('convocatoria')

            if estado:
                solicitudes = solicitudes.filter(
                    estado=estado
                )

            if estudiante and not estudiante.isdigit():
                return Response(
                    {'estudiante': ['Debe indicar un ID numérico.']},
                    status=400
                )

            if convocatoria and not convocatoria.isdigit():
                return Response(
                    {'convocatoria': ['Debe indicar un ID numérico.']},
                    status=400
                )

            if estudiante:
                solicitudes = solicitudes.filter(
                    estudiante_id=int(estudiante)
                )

            if convocatoria:
                solicitudes = solicitudes.filter(
                    convocatoria_id=int(convocatoria)
                )

        serializer = SolicitudSerializer(
            solicitudes,
            many=True
        )

        return Response(serializer.data)

    if request.method == 'POST':

        if (
            not es_encargado(request.user)
            and not es_estudiante(request.user)
        ):
            return Response(
                {'error': 'Necesitas el rol Estudiante para solicitar becas.'},
                status=403
            )

        if not es_encargado(request.user):

            estudiante_id = request.data.get(
                'estudiante'
            )

            ficha = getattr(
                request.user,
                'ficha_estudiante',
                None
            )

            if str(estudiante_id) != str(
                getattr(ficha, 'id', None)
            ):
                return Response(
                    {'error': 'Solo puedes solicitar becas para ti.'},
                    status=403
                )

        serializer = SolicitudSerializer(
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
def detalle_solicitud(request, pk):

    try:
        solicitud = Solicitud.objects.select_related(
            'estudiante',
            'convocatoria'
        ).get(pk=pk)

    except Solicitud.DoesNotExist:
        return Response(
            {'error': 'Solicitud no encontrada.'},
            status=404
        )

    if (
        not es_encargado(request.user)
        and solicitud.estudiante.usuario_id != request.user.id
    ):
        return Response(
            {'error': 'No tienes permiso para esta solicitud.'},
            status=403
        )

    if request.method == 'GET':

        serializer = SolicitudSerializer(
            solicitud
        )

        return Response(serializer.data)

    if solicitud.estado != 'PENDIENTE':
        return Response(
            {'error': 'La solicitud ya fue evaluada.'},
            status=409
        )

    if request.method in ['PUT', 'PATCH']:

        serializer = SolicitudSerializer(
            solicitud,
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

        if hasattr(solicitud, 'evaluacion'):
            return Response(
                {'error': 'No se puede eliminar una solicitud que tiene evaluación.'},
                status=409
            )

        solicitud.delete()

        return Response(status=204)