def es_admin(usuario):
    return (
        usuario.is_superuser
        or usuario.groups.filter(name='Administrador').exists()
    )


def es_encargado(usuario):
    return (
        es_admin(usuario)
        or usuario.groups.filter(name='Encargado').exists()
    )


def es_estudiante(usuario):
    return usuario.groups.filter(name='Estudiante').exists()