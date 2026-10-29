from django.urls import path
from . import views


urlpatterns = [
    path(
        'api/solicitudes/',
        views.lista_solicitudes
    ),

    path(
        'api/solicitudes/<int:pk>/',
        views.detalle_solicitud
    ),
]