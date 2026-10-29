from django.urls import path
from . import views


urlpatterns = [
    path(
        'api/estudiantes/',
        views.lista_estudiantes
    ),

    path(
        'api/estudiantes/<int:pk>/',
        views.detalle_estudiante
    ),
]