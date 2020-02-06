import datetime
from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user

from registro.models import Distributivo, Periodo, Estudiante
from tutoria.models import Tarjeta, ReporteTutoria, Firma
from registro.decorators import estudiante_required


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
        return render(request, 'tutoria/error.html', dato)
    # Obtener estudiante
    user = get_user(request)
    estudiante = Estudiante.objects.filter(usuario=user).first()
    # Obtener el periodo activo
    periodo = Periodo.objects.filter(activo=True).first()
    # Obtener distributivos
    distributivos = Distributivo.objects.filter(periodo=periodo).filter(docente=tarjeta.docente)
    # Obtiene la hora actual
    fin = datetime.datetime.now().strftime("%H:%M")
    inicio = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime("%H:%M")
    datos = {
        'docente': tarjeta.docente.usuario.nombre(),
        'asignaturas': distributivos,
        'periodo': periodo,
        'inicio': inicio,
        'fin': fin,
        'estudiante': estudiante.usuario.nombre()
    }
    return render(request, 'tutoria/registrar.html', datos)


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
            return render(request, 'tutoria/error.html', dato)
        # Validar reporte
        if reporte is None:
            dato = {
                'tipo': 'danger',
                'mensaje': 'No existe un reporte para la asignatura ' + distributivo.__str__(),
                'enfasis': 'Notifique a los desarrolladores',
                'boton': True
            }
            return render(request, 'tutoria/error.html', dato)
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
        return render(request, 'tutoria/error.html', dato)
    # Validar estudiante es dueño de la firma
    if estudiante != firma.estudiante:
        dato = {
            'tipo': 'warning',
            'mensaje': 'Estás intentando ver un registro de tutoría que no te pertenece.',
            'enfasis': 'No seas sapo',
            'boton': False
        }
        return render(request, 'tutoria/error.html', dato)
    # Generar datos para renderizar la página
    datos = {
        'estudiante': firma.estudiante.usuario.nombre(),
        'asignatura': firma.reporte.distributivo.materia.nombre,
        'docente': firma.reporte.distributivo.docente.usuario.nombre(),
        'duracion': firma.duracion,
        'tema': firma.tema
    }
    return render(request, 'tutoria/confirmar.html', datos)
