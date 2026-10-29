from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Estudiante
from .serializers import EstudianteSerializer

from becagest.permisos import es_admin, es_encargado
from becagest.paginacion import PaginacionBasica


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lista_estudiantes(request):

    if request.method == 'GET':

        estudiantes = Estudiante.objects.select_related(
            'usuario'
        ).order_by('id')

        if not es_encargado(request.user):

            estudiantes = estudiantes.filter(
                usuario=request.user
            )

        else:

            carrera = request.query_params.get('carrera')
            activo = request.query_params.get('activo')
            buscar = request.query_params.get('buscar')

            if carrera:
                estudiantes = estudiantes.filter(
                    carrera__icontains=carrera
                )

            if activo in ['true', 'false']:
                estudiantes = estudiantes.filter(
                    activo=(activo == 'true')
                )

            if buscar:
                estudiantes = estudiantes.filter(
                    nombre__icontains=buscar
                )

        paginador = PaginacionBasica()

        pagina = paginador.paginate_queryset(
            estudiantes, request
        )

        serializer = EstudianteSerializer(
            pagina, many=True
        )

        return paginador.get_paginated_response(
            serializer.data
        )

    if request.method == 'POST':

        if not es_admin(request.user):
            return Response(
                {'error': 'Solo el administrador puede registrar estudiantes.'},
                status=403
            )

        serializer = EstudianteSerializer(
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
def detalle_estudiante(request, pk):

    try:
        estudiante = Estudiante.objects.get(pk=pk)

    except Estudiante.DoesNotExist:
        return Response(
            {'error': 'Estudiante no encontrado.'},
            status=404
        )

    if request.method == 'GET':

        if (
            not es_encargado(request.user)
            and estudiante.usuario_id != request.user.id
        ):
            return Response(
                {'error': 'No tienes permiso.'},
                status=403
            )

        serializer = EstudianteSerializer(estudiante)

        return Response(serializer.data)

    if not es_admin(request.user):
        return Response(
            {'error': 'Solo el administrador puede modificar estudiantes.'},
            status=403
        )

    if request.method in ['PUT', 'PATCH']:

        serializer = EstudianteSerializer(
            estudiante,
            data=request.data,
            partial=(request.method == 'PATCH')
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=400
        )

    if request.method == 'DELETE':

        if estudiante.solicitudes.exists():
            return Response(
                {'error': 'No se puede eliminar un estudiante con solicitudes.'},
                status=409
            )

        estudiante.delete()

        return Response(status=204)
