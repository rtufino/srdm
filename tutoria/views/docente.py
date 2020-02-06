from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from registro.decorators import docente_required
from registro.models import Distributivo, Periodo
from registro.servicios import Servicios
from tutoria.models import Firma
from tutoria.servicios_t import Servicios_t
from collections import defaultdict
PARCIAL = 1

servicios=Servicios()
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
    informacion=[]
    informacion_aux={}


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

    datos = []
    elemento_aux = []
    fechas_aux=[]
    duracion_aux=[]
    # ************** se obtiene los alumnos por el id de distributivo ************
    for q in (servicios.getalumnos(distributivo_id)):
        elemento = []

        print(q.estudiante_id)

        nombre = q.estudiante
        cedula = q.estudiante.cedula

        elemento.append(nombre)




        tutorias = servicios_t.get_num_tutorias(q.estudiante_id)

        temas=servicios_t.get_observacion(q.estudiante_id)
        timestamp=servicios_t.get_timestamp(q.estudiante_id)
        duracion=servicios_t.get_duracion(q.estudiante_id)
        for i in temas:
            elemento.append(i)
        for i in timestamp:
            fechas_aux.append(i)

        for i in duracion:
            duracion_aux.append(i)


        elemento.append(tutorias)
        datos.append(elemento)
        for i in temas:
            elemento_aux.append(i)
        print("elemento_aux",elemento_aux)

        informacion_aux={
            'nombre':q.estudiante,
            'cedula':q.estudiante.cedula,
            'num_tutorias':tutorias,
            'temas':elemento_aux,
            'fecha':fechas_aux,
            'duracion':duracion,
        }
        #print("informacion_aux",informacion_aux)

        informacion.append(informacion_aux)
        elemento_aux = []
        fechas_aux = []
        duracion_aux = []
    print("informacion",informacion)
    #print(datos)


    context2 = {"fecha": fecha_actual, "materia": distributivo_id, "docente": nombre_docente, "informacion": informacion, }
    print(context2)


    return render(request, 'tutoria/docente/estudiantes_list.html',context2)

def detalletutoria(request,distributivo_id,cedula):
    estudiante=cedula.pk

    print(estudiante)

    context = {"alumnos": estudiante}
    print(context)
    return render(request, 'tutoria/docente/detalle_tutoria.html', context)

