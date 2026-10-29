from django.db.models import Count, Sum

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .permisos import es_encargado

from estudiantes.models import Estudiante
from convocatorias.models import Convocatoria
from solicitudes.models import Solicitud
from evaluaciones.models import Evaluacion
from asignaciones.models import Asignacion


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil(request):

    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'grupos': list(
            request.user.groups.values_list(
                'name',
                flat=True
            )
        )
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def resumen(request):

    if not es_encargado(request.user):
        return Response(
            {'error': 'No tienes permiso para ver el resumen.'},
            status=403
        )

    por_convocatoria = list(
        Convocatoria.objects.annotate(
            total_solicitudes=Count('solicitudes')
        ).values(
            'id',
            'nombre',
            'total_solicitudes'
        ).order_by('id')
    )

    por_estado = list(
        Solicitud.objects.values('estado')
        .annotate(total=Count('id'))
        .order_by('estado')
    )

    por_carrera = list(
        Estudiante.objects.values('carrera')
        .annotate(total=Count('id'))
        .order_by('carrera')
    )

    monto_total = Asignacion.objects.exclude(
        estado='CANCELADA'
    ).aggregate(
        monto=Sum('monto_mensual')
    )['monto'] or 0

    return Response({
        'total_estudiantes': Estudiante.objects.count(),

        'convocatorias_activas': Convocatoria.objects.filter(
            activa=True
        ).count(),

        'solicitudes_pendientes': Solicitud.objects.filter(
            estado='PENDIENTE'
        ).count(),

        'solicitudes_aprobadas': Solicitud.objects.filter(
            estado='APROBADA'
        ).count(),

        'evaluaciones_realizadas': Evaluacion.objects.count(),

        'asignaciones_no_canceladas': Asignacion.objects.exclude(
            estado='CANCELADA'
        ).count(),

        'monto_mensual_total': monto_total,

        'solicitudes_por_convocatoria': por_convocatoria,

        'solicitudes_por_estado': por_estado,

        'estudiantes_por_carrera': por_carrera
    })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def contador_sesion(request):

    visitas = request.session.get(
        'visitas',
        0
    ) + 1

    request.session['visitas'] = visitas

    return Response({
        'visitas_en_esta_sesion': visitas
    })