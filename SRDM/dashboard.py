from django.shortcuts import redirect, render
from django.contrib.auth import get_user

from registro.models import Docente


def home(request):
    if request.user.is_authenticated:
        if request.user.es_docente:
            # return redirect('dashboard_docente')
            user = get_user(request)
            docente = Docente.objects.filter(usuario=user).first()
            context = {
                'docente': docente.usuario.nombre()
            }
            return render(request, 'dashboard/docente.html', context)
        elif request.user.es_estudiante:
            return redirect('dashboard_estudiante')
    return render(request, 'index.html')
