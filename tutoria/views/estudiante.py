import datetime
from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.utils import text
from django.urls import reverse

from registro.models import Distributivo, Periodo, Estudiante
from tutoria.models import Tarjeta, ReporteTutoria, Firma


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
        'fin': fin
    }
    return render(request, 'tutoria/registrar.html', datos)


def firmar(request):
    if request.method == 'POST':
        # Obtener datos
        cedula = request.POST.get('inputCedula')
        id_distributivo = request.POST.get('inputAsignatura')
        tema = request.POST.get('inputTema')
        inicio = request.POST.get('inputInicio')
        fin = request.POST.get('inputFin')
        # Obtener objetos
        distributivo = Distributivo.objects.filter(pk=id_distributivo).first()
        estudiante = Estudiante.objects.filter(cedula=cedula).first()
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
        # validar estudiante
        if estudiante is None:
            dato = {
                'tipo': 'danger',
                'mensaje': 'No existe un estudiante con la cédula proporcionada.',
                'enfasis': cedula,
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
        query_string = urlencode(
            {
                'e': estudiante.pk,
                'd': id_distributivo,
                't': tema
            }
        )
        url = '{}?{}'.format(base_url, query_string)
        print(base_url, query_string, url)
        return redirect(url)


def confirmar(request):
    # Obtener datos de la peticion
    id_e = request.GET['e']
    id_d = request.GET['d']
    tema = request.GET['t']
    # Obtener objetos
    estudiante = Estudiante.objects.filter(pk=id_e).first()
    distributivo = Distributivo.objects.filter(pk=id_d).first()
    datos = {
        'estudiante': estudiante.usuario.nombre(),
        'asignatura': distributivo.materia.nombre,
        'tema': tema
    }
    return render(request, 'tutoria/confirmar.html', datos)
