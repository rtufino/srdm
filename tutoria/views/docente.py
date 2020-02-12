from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from registro.decorators import docente_required
from registro.forms import ValidarFirmaForm
from registro.models import Distributivo, Periodo, Estudiante
from registro.servicios import Servicios
from tutoria.models import Firma, ReporteTutoria
from tutoria.servicios_t import Servicios_t
from SRDM.util import get_link_tutorias, get_link_documentos
from collections import defaultdict

PARCIAL = 1

servicios = Servicios()
servicios_t = Servicios_t()


@login_required
@docente_required
def home(request):
    usuario = get_user(request)
    nombre_docente = servicios.getuser(usuario)
    print("Docente:", nombre_docente)
    # obtener el periodo activo
    periodo = Periodo.objects.filter(activo=True).first()
    materias = servicios.getmaterias(nombre_docente, periodo)
    # materias = servicios.getmaterias(nombre_docente)
    fecha_actual = servicios.getFechaActual()
    print("Fecha:", fecha_actual)
    if len(materias) != 0:
        for p in materias:
            print("Materia:", p.materia)
            print("Grupo", p.grupo)
            print("Periodo:", p.periodo)
            # print(p.activo)
            print("Nivel:", p.materia.nivel)
            print("Carrera:", p.materia.carrera)
    else:
        mensaje = 'No existen materias registradas para el docente'
        alerta = 'danger'
        dato = {'mensaje': mensaje, 'alerta': alerta,
                'link_documentos': get_link_documentos(usuario),
                'link_tutorias': get_link_tutorias(usuario),
                'menu': 'tutorias'}
        print(dato)
        return render(request, 'tutoria/docente/confirmacion.html', dato)

    context = {"fecha": fecha_actual, "materias": materias, "docente": nombre_docente, "grupo": p.grupo,
               "periodo": p.periodo,
               'link_documentos': get_link_documentos(usuario),
               'link_tutorias': get_link_tutorias(usuario),
               'menu': 'tutorias'}

    return render(request, 'tutoria/docente/listado_list.html', context)


@login_required
@docente_required
def estudiantesList(request, distributivo_id):
    informacion_aux = {}

    # obtener el periodo activo
    periodo = Periodo.objects.filter(activo=True).first()

    # ************* MODIFICACIÓN POR RODIGO ******************
    # Se recibe el id del distributivo en lugar de la materia

    # ***************** Se consulta del Distributivo el nombre de la materia ************
    la_materia = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo).first()
    asignatura = la_materia.materia.nombre + " - G" + la_materia.grupo

    usuario = get_user(request)

    nombre_docente = servicios.getuser(usuario)

    fecha_actual = servicios.getFechaActual()
    val = servicios.validar_materia_docente(distributivo_id, nombre_docente)
    print("docente", val)
    if val == False:
        mensaje = 'No tiene permiso para ver esta página'
        alerta = 'danger'
        dato = {'mensaje': mensaje, 'alerta': alerta,
                'link_documentos': get_link_documentos(usuario),
                'link_tutorias': get_link_tutorias(usuario),
                'menu': 'tutorias'}
        print(dato)
        return render(request, 'tutoria/docente/error.html', dato)

    informacion = servicios_t.get_info(distributivo_id)
    #######################################################################################

    # print(datos)
    #######################################################################################
    context2 = {
        "fecha": fecha_actual,
        "materia": distributivo_id,
        "docente": nombre_docente,
        "informacion": informacion,
        "asignatura": asignatura,
        'link_documentos': get_link_documentos(usuario),
        'link_tutorias': get_link_tutorias(usuario),
        'menu': 'tutorias'
    }
    print(context2)
    nombre_docente = nombre_docente.usuario.nombre()

    ########pruebas unicamenes###########################################
    # servicios_t.get_data(distributivo_id)
    # servicios_t.gen_reporte(informacion, 'tutoria', distributivo_id)
    #####################################################################

    return render(request, 'tutoria/docente/estudiantes_list.html', context2)


def detalle_tutoria(request, distributivo_id, estudiante_id):
    # Obtener estudiante
    estudiante = Estudiante.objects.filter(pk=estudiante_id).first()
    # Obtner tutorias
    distributivo = Distributivo.objects.filter(pk=distributivo_id).first()
    reporte = ReporteTutoria.objects.filter(distributivo=distributivo).first()
    firmas = Firma.objects.filter(reporte=reporte).filter(estudiante=estudiante)
    # retornar las firmas
    data = []
    n = 1
    for f in firmas:
        d = {
            'numero': n,
            'fecha': f.timestamp,
            'duracion': f.duracion,
            'tema': f.tema
        }
        data.append(d)
        n += 1
    context = {
        'alumno': estudiante.usuario.nombre(),
        'tutorias': data,
        'asignatura': distributivo.materia.nombre + " - G" + distributivo.grupo,
        'distributivo_id': distributivo_id,
        'link_documentos': get_link_documentos(get_user(request)),
        'link_tutorias': get_link_tutorias(get_user(request)),
        'menu': 'tutorias'
    }
    return render(request, 'tutoria/docente/detalle_tutoria.html', context)


@login_required
@docente_required
def documentos_pdf(request, distributivo_id, tipo):
    usuario = get_user(request)
    print("recibo", distributivo_id)
    print("recibo_tipo", tipo)
    nombre_docente = servicios.getuser(usuario)
    s = servicios_t.verificar_estado_informe(distributivo_id, tipo)
    print("estado", s)
    if s is not None:
        if s['estado'] != "C":
            informacion = servicios_t.get_info(distributivo_id)
            # servicios_t.get_data(distributivo_id)
            respuesta = servicios_t.gen_reporte(informacion, tipo, distributivo_id)
            # respuesta = servicios.get_pdf(nombre_docente, distributivo_id, tipo)
        else:
            mensaje = "El documento ya se ha generado"
            alerta = 'danger'
            dato = {'mensaje': mensaje, 'alerta': alerta,
                    'link_documentos': get_link_documentos(usuario),
                    'link_tutorias': get_link_tutorias(usuario),
                    'menu': 'tutorias'}
            return render(request, 'tutoria/docente/error.html', dato)
    else:
        # respuesta = servicios.get_pdf(nombre_docente, materia, tipo)
        mensaje = "El documento no se puede generar, no hay tutorias registradas"
        alerta = 'danger'
        dato = {'mensaje': mensaje, 'alerta': alerta,
                'link_documentos': get_link_documentos(usuario),
                'link_tutorias': get_link_tutorias(usuario),
                'menu': 'tutorias'}
        return render(request, 'tutoria/docente/error.html', dato)

    return respuesta

