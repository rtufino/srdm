from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UsuarioCreateForm, UsuarioChangeForm
from .models import Usuario, Docente, Estudiante, Periodo, Carrera, Materia, Distributivo, Alumno, TipoDocumento, \
    Documento, Informe, Firma
from .utils import TitledFilter


class DocenteAdmin(admin.ModelAdmin):
    model = Docente
    list_display = ('cedula', 'get_apellido', 'get_nombre', 'es_revisor')

    def get_nombre(self, obj):
        return obj.usuario.first_name

    def get_apellido(self, obj):
        return obj.usuario.last_name

    def es_revisor(self, obj):
        return obj.usuario.es_revisor

    es_revisor.boolean = True

    get_nombre.short_description = 'Nombres'
    get_apellido.short_description = 'Apellidos'
    es_revisor.short_description = 'Es revisor'
    get_nombre.admin_order_field = 'usuario__first_name'
    get_apellido.admin_order_field = 'usuario__last_name'
    list_filter = ('usuario__is_active', 'usuario__es_revisor')


class EstudianteAdmin(admin.ModelAdmin):
    model = Estudiante
    list_display = ('cedula', 'get_apellido', 'get_nombre')
    search_fields = ['cedula', 'usuario__first_name', 'usuario__last_name']

    def get_nombre(self, obj):
        return obj.usuario.first_name

    def get_apellido(self, obj):
        return obj.usuario.last_name

    get_nombre.short_description = 'Nombres'
    get_apellido.short_description = 'Apellidos'
    get_nombre.admin_order_field = 'usuario__first_name'
    get_apellido.admin_order_field = 'usuario__last_name'
    list_filter = ('usuario__is_active',)


class UsuarioAdmin(UserAdmin):
    model = Usuario
    # inlines = [DocenteInLine]
    add_form = UsuarioCreateForm
    form = UsuarioChangeForm
    add_fieldsets = (
        ('Datos personales', {'fields': ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')}),
        ('Roles', {'fields': ('es_docente', 'es_estudiante', 'es_revisor', 'es_verificador')}),
        ('Administración', {'fields': ('is_active', 'is_staff')})
    )
    fieldsets = (
        ('Datos personales', {'fields': ('first_name', 'last_name', 'username', 'email', 'password')}),
        ('Roles', {'fields': ('es_docente', 'es_estudiante', 'es_revisor', 'es_verificador')}),
        ('Administración', {'fields': ('is_active', 'is_staff')})
    )
    list_display = ('username', 'first_name', 'last_name', 'es_estudiante', 'es_docente', 'is_staff', 'is_active')
    list_filter = ('es_estudiante', 'es_docente', 'es_revisor', 'is_active', 'is_staff')


class PeriodoAdmin(admin.ModelAdmin):
    model = Periodo
    list_display = ('numero', 'descripcion')


class MateriaInLine(admin.TabularInline):
    model = Materia
    extra = 1


class CarreraAdmin(admin.ModelAdmin):
    model = Carrera
    inlines = [MateriaInLine]
    list_display = ('nombre', 'director', 'activo')


class AlumnoInLine(admin.TabularInline):
    model = Alumno
    raw_id_fields = ('estudiante',)


class DistributivoAdmin(admin.ModelAdmin):
    model = Distributivo
    list_display = ('materia', 'grupo', 'get_carrera', 'docente', 'periodo')
    list_filter = (TitledFilter('periodo activo', 'periodo__activo'), 'materia__carrera')
    search_fields = ['docente__usuario__first_name', 'docente__usuario__last_name', 'materia__nombre']
    inlines = [AlumnoInLine]

    def get_carrera(self, obj: Distributivo):
        return obj.materia.carrera.nombre

    get_carrera.short_description = 'Carrera'
    get_carrera.admin_order_field = 'materia__carrera__nombre'


class DocumentoInLine(admin.TabularInline):
    model = Documento
    extra = 1


class TipoDocumentoAdmin(admin.ModelAdmin):
    model = TipoDocumento
    list_display = 'nombre', 'solo_presidente', 'activo'
    inlines = [DocumentoInLine]


class FirmaAdmin(admin.ModelAdmin):
    model = Firma
    list_display = 'alumno', 'informe', 'timestamp'
    list_filter = ['informe__distributivo__materia__carrera', 'informe__documento']
    search_fields = ['informe__distributivo__materia__nombre']
    date_hierarchy = 'timestamp'


class FirmaInLine(admin.TabularInline):
    model = Firma
    extra = 1


class InformeAdmin(admin.ModelAdmin):
    model = Informe
    inlines = [FirmaInLine]
    list_display = 'distributivo', 'documento', 'fecha_habilitacion', 'fecha_generacion', 'parcial', 'estado'
    list_filter = ('distributivo__materia__carrera', 'parcial', 'documento')
    search_fields = ['distributivo__materia__nombre']

    # class InformeAdmin(admin.ModelAdmin):
    #    model = Informe
    #    inlines = [FirmaInLine]
    #    list_display = 'distributivo', 'documento', 'get_carrera', 'fecha_habilitacion', 'fecha_generacion', 'parcial', \
    #                   'estado', 'get_periodo'

    #    list_filter = (
    #        TitledFilter('periodo activo', 'distributivo__periodo__activo'), 'distributivo__materia__carrera', 'parcial')

    def get_carrera(self, obj: Informe):
        return obj.distributivo.materia.carrera.nombre

    get_carrera.short_description = 'Carrera'
    get_carrera.admin_order_field = 'distributivo__materia__carrera__nombre'

    def get_periodo(self, obj: Informe):
        return obj.distributivo.periodo.numero

    get_periodo.short_description = 'Periodo'
    get_periodo.admin_order_field = 'distributivo__periodo__numero'


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Docente, DocenteAdmin)
admin.site.register(Estudiante, EstudianteAdmin)
admin.site.register(Periodo, PeriodoAdmin)
admin.site.register(Carrera, CarreraAdmin)
admin.site.register(Distributivo, DistributivoAdmin)
admin.site.register(TipoDocumento, TipoDocumentoAdmin)
admin.site.register(Informe, InformeAdmin)
admin.site.register(Firma, FirmaAdmin)
