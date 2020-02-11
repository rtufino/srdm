from django.shortcuts import redirect, render


def home(request):
    if request.user.is_authenticated:
        if request.user.es_docente:
            return redirect('docente:home_docente')
        elif request.user.es_estudiante:
            return redirect('estudiante:home')
    return render(request, 'index.html')
