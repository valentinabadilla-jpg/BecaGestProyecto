from django.urls import path
from . import views


urlpatterns = [
    path(
        'api/convocatorias/',
        views.lista_convocatorias
    ),

    path(
        'api/convocatorias/<int:pk>/',
        views.detalle_convocatoria
    ),
]