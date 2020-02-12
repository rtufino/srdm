import datetime
from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user

from registro.models import Distributivo, Periodo, Estudiante, Alumno
from tutoria.models import Tarjeta, ReporteTutoria, Firma
from registro.decorators import estudiante_required
from SRDM.util import get_link_tutorias, get_link_documentos, get_periodo_activo
from tutoria.servicios_t import Servicios_t, PARCIAL


@login_required
@estudiante_required
def home(request):
    # Obtener estudiante
    user = get_user(request)
    estudiante = Estudiante.objects.filter(usuario=user).first()
    # Obtener materias
    materias = obtener_materias(estudiante)
    # Utilizar servicios para número de tutorias
    servicio = Servicios_t()
    num_tutorias = []
    for m in materias:
        n = servicio.get_num_tutorias(estudiante, PARCIAL, get_periodo_activo(), m.id)
        tutoria = {
            'materia': m.id,
            'numero': n
        }
        num_tutorias.append(tutoria)
    # Armar diccionario para enviar a la vista
    context = {
        'link_documentos': get_link_documentos(request.user),
        'link_tutorias': get_link_tutorias(request.user),
        'materias': materias,
        'tutorias': num_tutorias,
        'menu': 'tutorias'
    }
    # Renderizar la vista
    return render(request, 'tutoria/estudiante/home.html', context)


def obtener_materias(estudiante: Estudiante):
    # obtener el periodo activo
    periodo = get_periodo_activo()
    # obtener los registros donde el estudiante es alumno
    listado = Alumno.objects.filter(estudiante=estudiante)
    # obtener el id de los distributivos a los que el alumno pertenece
    ids = []
    for a in listado:
        ids.append(a.distributivo.id)
    # consultar las materias donde el estudiante es alumno del periodo activo
    distributivos = Distributivo.objects.filter(periodo=periodo).filter(pk__in=ids).order_by('materia__carrera',
                                                                                             'materia__nivel')
    return distributivos


@login_required
@estudiante_required
def detalle(request, distributivo_id):
    # Obtener estudiante
    user = get_user(request)
    estudiante = Estudiante.objects.filter(usuario=user).first()
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
        'tutorias': data,
        'asignatura': distributivo.materia.nombre + " - G" + distributivo.grupo,
        'distributivo_id': distributivo_id,
        'link_documentos': get_link_documentos(user),
        'link_tutorias': get_link_tutorias(user),
        'menu': 'tutorias'
    }
    return render(request, 'tutoria/estudiante/detalle.html', context)


@login_required
@estudiante_required
def registrar(request, codigo_hash):
    # Obtener la tarjeta a partir del codigo hash
    tarjeta = Tarjeta.objects.filter(hash=codigo_hash).first()
    # Validar si la tarjeta existe
    if tarjeta is None:
        dato = {
            'tipo': 'warning',
            'mensaje': 'Notifique a los desarrolladores que existe un error con el siguiente código:',
            'boton': False,
            'enfasis': codigo_hash
        }
        return render(request, 'tutoria/estudiante/error.html', dato)
    # Obtener estudiante
    user = get_user(request)
    estudiante = Estudiante.objects.filter(usuario=user).first()
    # Obtener el periodo activo
    periodo = Periodo.objects.filter(activo=True).first()
    # Obtener distributivos
    distributivos = Distributivo.objects.filter(periodo=periodo).filter(docente=tarjeta.docente)
    # Obtiene la hora actual
    fin = datetime.datetime.now().strftime("%H:%M")
    # Establece 15 minutos atrás de la hora actual
    inicio = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime("%H:%M")
    # Armar datos para la página
    datos = {
        'docente': tarjeta.docente.usuario.nombre(),
        'asignaturas': distributivos,
        'periodo': periodo,
        'inicio': inicio,
        'fin': fin,
        'estudiante': estudiante.usuario.nombre(),
        'page_title': 'Registrar Tutoria'
    }
    return render(request, 'tutoria/estudiante/registrar.html', datos)


@login_required
@estudiante_required
def firmar(request):
    if request.method == 'POST':
        # Obtener datos
        id_distributivo = request.POST.get('inputAsignatura')
        tema = request.POST.get('inputTema')
        inicio = request.POST.get('inputInicio')
        fin = request.POST.get('inputFin')
        # Obtener estudiante
        user = get_user(request)
        estudiante = Estudiante.objects.filter(usuario=user).first()
        # Obtener objetos
        distributivo = Distributivo.objects.filter(pk=id_distributivo).first()
        reporte = ReporteTutoria.objects.filter(distributivo=distributivo).first()
        # validar distributivo
        if distributivo is None:
            dato = {
                'tipo': 'warning',
                'mensaje': 'No se puede encontrar la asignatura:',
                'enfasis': 'id = ' + id_distributivo,
                'boton': True
            }
            return render(request, 'tutoria/estudiante/error.html', dato)
        # Validar reporte
        if reporte is None:
            dato = {
                'tipo': 'danger',
                'mensaje': 'No existe un reporte para la asignatura ' + distributivo.__str__(),
                'enfasis': 'Notifique a los desarrolladores',
                'boton': True
            }
            return render(request, 'tutoria/estudiante/error.html', dato)
        # Calculando duracion
        t_inicio = datetime.datetime.strptime(inicio, '%H:%M')
        t_fin = datetime.datetime.strptime(fin, '%H:%M')
        duracion = t_fin - t_inicio
        # Crear la firma
        firma = Firma(
            reporte=reporte,
            estudiante=estudiante,
            tema=tema,
            hash=estudiante.cedula,
            duracion=duracion
        )
        firma.save()
        # Redireccionar
        base_url = reverse('tutoria_estudiante:confirmar')
        query_string = urlencode({'id': firma.pk})
        url = '{}?{}'.format(base_url, query_string)
        return redirect(url)


@login_required
@estudiante_required
def confirmar(request):
    # Obtener datos de la peticion
    id = request.GET['id']
    # Obtener objeto
    firma = Firma.objects.filter(pk=id).first()
    # Obtener estudiante
    user = get_user(request)
    estudiante = Estudiante.objects.filter(usuario=user).first()
    # Validar firma
    if firma is None:
        dato = {
            'tipo': 'danger',
            'mensaje': 'No existe el registro de tutoría con id ' + id,
            'enfasis': 'Probablemente esto es un error generado por ti',
            'boton': False
        }
        return render(request, 'tutoria/estudiante/error.html', dato)
    # Validar estudiante es dueño de la firma
    if estudiante != firma.estudiante:
        dato = {
            'tipo': 'warning',
            'mensaje': 'Estás intentando ver un registro de tutoría que no te pertenece.',
            'enfasis': 'No seas sapo',
            'boton': False
        }
        return render(request, 'tutoria/estudiante/error.html', dato)
    # Generar datos para renderizar la página
    datos = {
        'estudiante': firma.estudiante.usuario.nombre(),
        'asignatura': firma.reporte.distributivo.materia.nombre,
        'docente': firma.reporte.distributivo.docente.usuario.nombre(),
        'duracion': firma.duracion,
        'tema': firma.tema
    }
    return render(request, 'tutoria/estudiante/confirmar.html', datos)
