from django.contrib import admin
from .models import Tarjeta, ReporteTutoria, Firma, Parametro


# Register your models here.

class TarjetaAdmin(admin.ModelAdmin):
    model = Tarjeta
    list_display = 'docente', 'hash'
    search_fields = ['docente__usuario__first_name', 'docente__usuario__last_name']


class ReporteTutoriaAdmin(admin.ModelAdmin):
    model = ReporteTutoria
    list_display = 'distributivo', 'fecha_habilitacion', 'fecha_generacion', 'parcial'
    list_filter = ['distributivo__materia__carrera', ]
    search_fields = ['distributivo__materia__nombre']


class FirmaAdmin(admin.ModelAdmin):
    model = Firma
    list_display = 'timestamp', 'reporte', 'estudiante', 'duracion'
    list_filter = ['reporte__distributivo__materia__carrera', ]
    search_fields = ['docente__usuario__first_name', 'docente__usuario__last_name',
                     'reporte__distributivo__materia__nombre']

    date_hierarchy = 'timestamp'


class ParametroAdmin(admin.ModelAdmin):
    model = Parametro
    list_display = 'clave', 'valor'
    search_fields = ['clave']


admin.site.register(Tarjeta, TarjetaAdmin)
admin.site.register(ReporteTutoria, ReporteTutoriaAdmin)
admin.site.register(Firma, FirmaAdmin)
admin.site.register(Parametro, ParametroAdmin)
