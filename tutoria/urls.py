from django.urls import include, path

from .views import estudiante, tutoria,docente

urlpatterns = [
path('docente/', include((
        [
            path('', docente.home, name='home_docente'),
            path('<distributivo_id>/', docente.estudiantesList, name='estudiantes_list'),
          #  path('<distributivo_id>/<cedula>/', docente.detalletutoria, name='detalle_tutoria'),
        ], 'classrom3'),
        namespace='tutoria')),
]
