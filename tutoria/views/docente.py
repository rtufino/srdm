from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from registro.decorators import docente_required
from registro.forms import ValidarFirmaForm
from registro.models import Distributivo, Periodo, Estudiante
from registro.servicios import Servicios
from tutoria.models import Firma, ReporteTutoria
from tutoria.servicios_t import Servicios_t
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
        dato = {'mensaje': mensaje, 'alerta': alerta}
        print(dato)
        return render(request, 'tutoria/docente/confirmacion.html', dato)

    context = {"fecha": fecha_actual, "materias": materias, "docente": nombre_docente, "grupo": p.grupo,
               "periodo": p.periodo}

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
    materiaid = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.nombre

    usuario = get_user(request)

    nombre_docente = servicios.getuser(usuario)

    fecha_actual = servicios.getFechaActual()
    val = servicios.validar_materia_docente(distributivo_id, nombre_docente)
    print("docente", val)
    if val == False:
        mensaje = 'No tiene permiso para ver esta página'
        alerta = 'danger'
        dato = {'mensaje': mensaje, 'alerta': alerta}
        print(dato)
        return render(request, 'tutoria/docente/error.html', dato)

    informacion=servicios_t.get_info(distributivo_id)
#######################################################################################

    # print(datos)
#######################################################################################
    context2 = {"fecha": fecha_actual, "materia": distributivo_id, "docente": nombre_docente,
                "informacion": informacion, }
    print(context2)
    nombre_docente = nombre_docente.usuario.nombre()

    ########pruebas unicamenes###########################################
    #servicios_t.get_data(distributivo_id)
    #servicios_t.gen_reporte(informacion, 'tutoria', distributivo_id)
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
        'tutorias': data
    }
    return render(request, 'tutoria/docente/detalle_tutoria.html', context)
@login_required
@docente_required
def documentos_pdf(request, distributivo_id, tipo):
    usuario = get_user(request)
    print("recibo", distributivo_id)
    print("recibo_tipo",tipo)
    nombre_docente = servicios.getuser(usuario)
    s = servicios_t.verificar_estado_informe(distributivo_id, tipo)
    print("estado", s)

    if s != None:
        if s['estado'] != "C":
            informacion=servicios_t.get_info(distributivo_id)
            #servicios_t.get_data(distributivo_id)
            respuesta=servicios_t.gen_reporte(informacion, tipo, distributivo_id)
            #respuesta = servicios.get_pdf(nombre_docente, distributivo_id, tipo)
        else:
            mensaje = "El documento ya se ha generado"
            alerta = 'danger'
            dato = {'mensaje': mensaje, 'alerta': alerta}
            return render(request, 'tutoria/docente/error.html', dato)
    else:
        #respuesta = servicios.get_pdf(nombre_docente, materia, tipo)
        mensaje = "El documento no se puede generar, no hay tutorias registradas"
        alerta = 'danger'
        dato = {'mensaje': mensaje, 'alerta': alerta}
        return render(request, 'tutoria/docente/error.html', dato)

    return respuesta

def validarfirma(request):
    dato = {}
    if request.method == 'POST':
        form = ValidarFirmaForm(request.POST)
        if form.is_valid():

            firma_hash = form.save()

            firma_hash.save()
            print(form.cleaned_data['documento_id'])
            valid = servicios.validarfirma(form.cleaned_data['documento_id'])
            print(valid)
            if valid == True:

                mensaje = 'Documento Válido'
                alerta = 'success'
                dato = {'mensaje': mensaje, 'alerta': alerta}
                print(dato)
                return render(request, 'registro/docente/confirmacion.html', dato)
            else:
                mensaje = "No existe Documento"
                alerta = 'danger'
                dato = {'mensaje': mensaje, 'alerta': alerta}
                return render(request, 'registro/docente/confirmacion.html', dato)


    else:
        form = ValidarFirmaForm()

    return render(request, 'registro/docente/validarfirma.html', {'form': form})