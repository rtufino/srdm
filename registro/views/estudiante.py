import datetime

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user

from ..decorators import estudiante_required
from ..models import Estudiante, Periodo, Distributivo, Alumno, Informe, Firma


@login_required
@estudiante_required
def home(request):
    # print ("-- home estudiante --")
    user = get_user(request)
    estudiante = Estudiante.objects.filter(usuario=user)[0]
    # print(estudiante)
    materias, documentos = obtener_datos(estudiante)
    # print(materias,documentos)
    datos = {'materias': materias, 'documentos': documentos}
    return render(request, 'registro/estudiante/home.html', datos)


def obtener_datos(estudiante: Estudiante):
    # obtener el periodo activo
    periodo = Periodo.objects.filter(activo=True).first()
    # obtener los registros donde el estudiante es alumno
    listado = Alumno.objects.filter(estudiante=estudiante)
    # obtener el id de los distributivos a los que el alumno pertenece
    ids = []
    for a in listado:
        ids.append(a.distributivo.id)
    # consultar las materias donde el estudiante es alumno del periodo activo
    distributivos = Distributivo.objects.filter(periodo=periodo).filter(pk__in=ids).order_by('materia__carrera',
                                                                                             'materia__nivel')
    # consultar los informes que se ha generado para esta asignatura
    informes = Informe.objects.filter(distributivo__in=ids).order_by('parcial', 'fecha_habilitacion')
    return distributivos, informes


@login_required
@estudiante_required
def documento(request, id_informe):
    informe = Informe.objects.filter(pk=id_informe).first()
    user = get_user(request)
    estudiante = Estudiante.objects.filter(usuario=user)[0]
    if not es_valido(informe, estudiante):
        return redirect('estudiante:home')
    if puede_firmar(estudiante, informe):
        datos = {
            'informe': informe,
            'carrera': informe.distributivo.materia.carrera,
            'periodo': informe.distributivo.periodo,
            'docente': informe.distributivo.docente,
            'materia': informe.distributivo.materia,
            'nivel': informe.distributivo.materia.nivel,
            'grupo': informe.distributivo.grupo,
            'cedula': estudiante.cedula
        }
        return render(request, 'registro/estudiante/documento.html', datos)
    else:
        mensaje = 'Tu ya has firmado este documento'
        alerta = 'danger'
        dato = {'mensaje': mensaje, 'alerta': alerta}
        return render(request, 'registro/estudiante/confirmacion.html', dato)


def es_valido(informe, estudiante):
    if informe is None:
        return False
    dato = Alumno.objects.filter(estudiante=estudiante).filter(distributivo=informe.distributivo)
    return len(dato) == 1


@login_required
@estudiante_required
def firmar(request):
    if request.method == 'POST':
        aceptar = request.POST['aceptar']
        mensaje = ''
        alerta = 'info'
        if aceptar == 'SI':
            id_informe = request.POST['informe']
            informe = Informe.objects.filter(pk=id_informe).first()
            user = get_user(request)
            estudiante = Estudiante.objects.filter(usuario=user)[0]
            alumno = Alumno.objects.filter(estudiante=estudiante, distributivo=informe.distributivo).first()
            if not ya_firmo(alumno, informe):
                firma = Firma(
                    alumno=alumno,
                    informe=informe,
                    hash=estudiante.cedula,
                    observacion='',
                    timestamp=datetime.datetime.now()
                )
                firma.save()
                mensaje = 'Documento firmado exitosamentre'
                alerta = 'success'
            else:
                mensaje = 'Tu ya has firmado este documento'
                alerta = 'danger'
        else:
            mensaje = "Has decidido NO firmar el documento"
            alerta = 'warning'
    else:
        mensaje = 'Invocación incorrrecta al método'
        alerta = 'danger'
    dato = {'mensaje': mensaje, 'alerta': alerta}
    return render(request, 'registro/estudiante/confirmacion.html', dato)


def ya_firmo(alumno, informe):
    f = Firma.objects.filter(alumno=alumno, informe=informe).first()
    if f is None:
        return False
    else:
        return True


def puede_firmar(estudiante, informe):
    alumno = Alumno.objects.filter(estudiante=estudiante, distributivo=informe.distributivo).first()
    return not ya_firmo(alumno, informe)
