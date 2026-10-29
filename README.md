# BecaGest

API REST para la gestión de becas, desarrollada con Django REST Framework y MySQL.

## Tecnologías

- Python 3.14.2
- Django 5.2.18
- Django REST Framework 3.18.3
- MySQL

## Módulos

- Estudiantes
- Convocatorias
- Solicitudes
- Evaluaciones
- Asignaciones

## Instalación

1. Crear y activar un entorno virtual.
2. Instalar las dependencias con `pip install -r requirements.txt`.
3. Configurar las variables de entorno en el archivo `.env`, tomando como referencia `.env.example`.
4. Aplicar las migraciones con `python manage.py migrate`.
5. Crear un superusuario con `python manage.py createsuperuser`, si es necesario.
6. Iniciar el servidor con `python manage.py runserver`.

## Autenticación

La API utiliza tokens de Django REST Framework.

- Obtener token: `POST /api/token/`
- Consultar perfil: `GET /api/perfil/`

## Endpoints principales

| Recurso | Endpoint |
|---|---|
| Estudiantes | `/api/estudiantes/` |
| Convocatorias | `/api/convocatorias/` |
| Solicitudes | `/api/solicitudes/` |
| Evaluaciones | `/api/evaluaciones/` |
| Asignaciones | `/api/asignaciones/` |
| Reportes | `/api/reportes/resumen/` |

## Pruebas

Ejecutar todas las pruebas automatizadas:

`python manage.py test`

Actualmente, las 20 pruebas automatizadas pasan correctamente.

## Seguridad

- Mantener las credenciales en `.env`.
- No subir `.env` a GitHub.
- Utilizar `.env.example` como referencia de configuración.
- `runserver` es para desarrollo, no para producción.
