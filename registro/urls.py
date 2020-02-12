from django.urls import include, path

from .views import registro, docente, estudiante


urlpatterns = [
    path('docente/', include((
        [
            path('', docente.home, name='home'),
            path('<distributivo_id>/', docente.estudiantesList, name='estudiantes_list'),
            path('revex/<materia> <tipo>/', docente.documentos_pdf, name='documentos_pdf'),
            #path('validar/', docente.validarfirma, name='validarfirma'),

        ], 'classroom'),
        namespace='registro_docente')),

    path('estudiante/', include((
        [
            path('', estudiante.home, name='home'),
            path('<int:id_informe>', estudiante.documento, name='documento'),
            path('firmar', estudiante.firmar, name='firmar'),
        ], 'classroom1'),
        namespace='registro_estudiante')),

]
