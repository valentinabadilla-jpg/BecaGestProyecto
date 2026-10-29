from django.utils import timezone
from django.db.models import Q

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Convocatoria
from .serializers import ConvocatoriaSerializer

from becagest.permisos import es_admin
from becagest.paginacion import PaginacionBasica


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lista_convocatorias(request):

    if request.method == 'GET':

        convocatorias = Convocatoria.objects.all()

        activa = request.query_params.get('activa')
        buscar = request.query_params.get('buscar')
        abierta = request.query_params.get('abierta')
        orden = request.query_params.get('orden', 'id')

        if activa in ['true', 'false']:
            convocatorias = convocatorias.filter(
                activa=(activa == 'true')
            )

        if buscar:
            convocatorias = convocatorias.filter(
                Q(nombre__icontains=buscar)
                | Q(descripcion__icontains=buscar)
            )

        if abierta == 'si':

            hoy = timezone.localdate()

            convocatorias = convocatorias.filter(
                activa=True,
                fecha_inicio__lte=hoy,
                fecha_fin__gte=hoy
            )

        if orden not in [
            'id', '-id',
            'nombre', '-nombre',
            'fecha_fin', '-fecha_fin'
        ]:
            orden = 'id'

        convocatorias = convocatorias.order_by(orden)

        paginador = PaginacionBasica()

        pagina = paginador.paginate_queryset(
            convocatorias,
            request
        )

        serializer = ConvocatoriaSerializer(
            pagina,
            many=True
        )

        return paginador.get_paginated_response(
            serializer.data
        )

    if request.method == 'POST':

        if not es_admin(request.user):
            return Response(
                {'error': 'Solo el administrador puede crear convocatorias.'},
                status=403
            )

        serializer = ConvocatoriaSerializer(
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
def detalle_convocatoria(request, pk):

    try:
        convocatoria = Convocatoria.objects.get(
            pk=pk
        )

    except Convocatoria.DoesNotExist:
        return Response(
            {'error': 'Convocatoria no encontrada.'},
            status=404
        )

    if request.method == 'GET':

        serializer = ConvocatoriaSerializer(
            convocatoria
        )

        return Response(serializer.data)

    if not es_admin(request.user):
        return Response(
            {'error': 'Solo el administrador puede modificar convocatorias.'},
            status=403
        )

    if request.method in ['PUT', 'PATCH']:

        serializer = ConvocatoriaSerializer(
            convocatoria,
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

        if convocatoria.solicitudes.exists():
            return Response(
                {'error': 'No se puede eliminar una convocatoria con solicitudes.'},
                status=409
            )

        convocatoria.delete()

        return Response(status=204)
