from registro.models import Periodo


def get_link_tutorias(user):
    if user.es_docente:
        return 'tutoria_docente:home'
    elif user.es_estudiante:
        return 'tutoria_estudiante:home'


def get_link_documentos(user):
    if user.es_docente:
        return 'registro_docente:home'
    elif user.es_estudiante:
        return 'registro_estudiante:home'


def get_periodo_activo():
    # Obtener el periodo activo
    periodo = Periodo.objects.filter(activo=True).first()
    return periodo
