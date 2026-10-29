
from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from . import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', obtain_auth_token),
    path('api/perfil/', views.perfil),
    path('api/sesion/', views.contador_sesion),
    path('api/reportes/resumen/', views.resumen),

    path('', include('estudiantes.urls')),
    path('', include('convocatorias.urls')),
    path('', include('solicitudes.urls')),
    path('', include('evaluaciones.urls')),
    path('', include('asignaciones.urls')),
]
