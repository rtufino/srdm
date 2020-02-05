from django.urls import include, path

from .views import estudiante, tutoria

urlpatterns = [

    path('estudiante/', include((
        [
            path('registrar/<str:codigo_hash>', estudiante.registrar, name='registrar'),
            path('firmar/', estudiante.firmar, name='firmar'),
            path('confirmar/', estudiante.confirmar, name='confirmar'),
        ], 'classroom1'),
        namespace='tutoria_estudiante')),
]
