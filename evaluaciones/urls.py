from django.urls import path
from . import views


urlpatterns = [
    path(
        'api/evaluaciones/',
        views.lista_evaluaciones
    ),

    path(
        'api/evaluaciones/<int:pk>/',
        views.detalle_evaluacion
    ),
]