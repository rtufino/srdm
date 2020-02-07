from django.urls import include, path

from .views import estudiante, tutoria, docente

urlpatterns = [
    path('docente/', include((
        [
            path('', docente.home, name='home_docente'),
            path('<distributivo_id>/', docente.estudiantesList, name='estudiantes_list'),
            path('detalle/<int:distributivo_id>/<int:estudiante_id>/', docente.detalle_tutoria, name='detalle_tutoria'),
        ], 'classrom3'),
        namespace='tutoria')),
    path('estudiante/', include((
        [
            path('registrar/<str:codigo_hash>', estudiante.registrar, name='registrar'),
            path('firmar/', estudiante.firmar, name='firmar'),
            path('confirmar/', estudiante.confirmar, name='confirmar'),
        ], 'classroom1'),
        namespace='tutoria_estudiante')),
]
