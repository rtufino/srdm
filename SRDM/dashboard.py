from django.shortcuts import redirect, render
from django.contrib.auth import get_user

from registro.models import Docente, Estudiante
from SRDM.util import get_link_tutorias, get_link_documentos


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

