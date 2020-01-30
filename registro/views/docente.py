from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user

from django.shortcuts import render, redirect

from ..decorators import docente_required
from registro.servicios import Servicios

from django.http import HttpResponseRedirect
from django.urls import reverse
from registro.models import ValidarFirma
from registro.forms import ValidarFirmaForm

from ..models import Documento, Distributivo, Periodo

PARCIAL = 2

servicios = Servicios()


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
        return render(request, 'registro/docente/confirmacion.html', dato)

    context = {"fecha": fecha_actual, "materias": materias, "docente": nombre_docente, "grupo": p.grupo,
               "periodo": p.periodo}

    return render(request, 'registro/docente/listado_list.html', context)


@login_required
@docente_required
def estudiantesList(request, distributivo_id):
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
        return render(request, 'registro/docente/error.html', dato)
    # obtener el periodo activo
    # periodo = Periodo.objects.filter(activo=True).first()
    materias = servicios.getmaterias(nombre_docente, periodo)
    documento = []
    datos2 = []
    datos = []
    # ************** se obtiene los alumnos por el id de distributivo ************
    for q in (servicios.getalumnos(distributivo_id)):
        elemento = []
        # doc = servicios.getinforme(q.estudiante.cedula)
        # doc = Documento.objects.filter(informe__firma__alumno_id=q.pk)
        doc = Documento.objects.filter(informe__parcial=PARCIAL, informe__firma__alumno_id=q.pk)
        print("**** DOC ***")
        print(q.pk)
        print(doc)
        nombre = q.estudiante
        cedula = q.estudiante.cedula

        elemento.append(nombre)
        elemento.append(cedula)

        if len(doc) == 0:
            elemento.append('none')
        datos2 = []
        for r in doc:
            elemento.append(r)
        if len(datos2) != 0:
            elemento.append(datos2)
        datos.append(elemento)
    print(datos)

    # context = {"fecha":fecha_actual,"materia": materiaid,"docente": nombre_docente,"alumnos": nombre,"document":documento,"cedula":cedula}

    # context2 = {"fecha": fecha_actual, "materia": materiaid, "docente": nombre_docente,
    #             "alumnos": servicios.getalumnos(materiaid), "document": datos[2], "cedula": q.estudiante.cedula}
    context2 = {"fecha": fecha_actual, "materia": distributivo_id, "docente": nombre_docente, "alumnos": datos, }
    print(context2)
    return render(request, 'registro/docente/estudiantes_list.html', context2)


@login_required
@docente_required
def documentos_pdf(request, materia, tipo):
    usuario = get_user(request)
    print("recibo", materia)
    nombre_docente = servicios.getuser(usuario)
    s = servicios.verificar_estado_informe(materia, tipo)
    print("estado", s)
    if s != None:
        if s['estado'] != "C":
            respuesta = servicios.get_pdf(nombre_docente, materia, tipo)
        else:
            mensaje = "El documento ya se ha generado"
            alerta = 'danger'
            dato = {'mensaje': mensaje, 'alerta': alerta}
            return render(request, 'registro/docente/error.html', dato)
    else:
        mensaje = "El documento no es necesario para este período"
        alerta = 'danger'
        dato = {'mensaje': mensaje, 'alerta': alerta}
        return render(request, 'registro/docente/error.html', dato)

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
