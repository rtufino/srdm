from registro.models import Periodo
from tutoria.models import Parametro


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


def get_parcial():
    parcial = Parametro.objects.filter(clave='PARCIAL').first()
    if parcial is not None:
        return int(parcial.valor)
    else:
        return 1


def get_IP():
    param = Parametro.objects.filter(clave='IP').first()
    if param is not None:
        return param.valor
    else:
        return 'http://127.0.0.1:8000'
