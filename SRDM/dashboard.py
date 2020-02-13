from django.shortcuts import redirect, render
from django.contrib.auth import get_user

from registro.models import Docente, Estudiante
from SRDM.util import get_link_tutorias, get_link_documentos
from registro.forms import ValidarFirmaForm
from registro.models import Docente
from registro.views.docente import servicios


def home(request):
    if request.user.is_authenticated:
        if request.user.es_docente:
            # return redirect('dashboard_docente')
            user = get_user(request)
            docente = Docente.objects.filter(usuario=user).first()
            context = {
                'docente': docente.usuario.nombre(),
                'link_documentos': get_link_documentos(request.user),
                'link_tutorias': get_link_tutorias(request.user),
                'menu': 'dashboard'
            }
            return render(request, 'dashboard/docente.html', context)
        elif request.user.es_estudiante:
            user = get_user(request)
            estudiante = Estudiante.objects.filter(usuario=user).first()
            context = {
                'estudiante': estudiante.usuario.first_name,
                'link_documentos': get_link_documentos(request.user),
                'link_tutorias': get_link_tutorias(request.user),
                'menu': 'dashboard'
            }
            return render(request, 'dashboard/estudiante.html', context)
    return render(request, 'index.html')


def validarfirma(request):
    dato = {}
    if request.method == 'POST':
        print('ingresa al if del POST')
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
                return render(request, 'dashboard/confirmacion.html', dato)
            else:
                mensaje = "No existe Documento"
                alerta = 'danger'
                dato = {'mensaje': mensaje, 'alerta': alerta}
                return render(request, 'dashboard/confirmacion.html', dato)
    else:
        form = ValidarFirmaForm()

    return render(request, 'dashboard/validarfirma.html', {'form': form})
