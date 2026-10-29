from django.urls import path
from . import views


urlpatterns = [
    path(
        'api/asignaciones/',
        views.lista_asignaciones
    ),

    path(
        'api/asignaciones/<int:pk>/',
        views.detalle_asignacion
    ),
]