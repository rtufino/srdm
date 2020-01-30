from django.contrib import admin
from .models import Horario, Tarjeta


# Register your models here.

class TarjetaAdmin(admin.ModelAdmin):
    model = Tarjeta


class HorarioAdmin(admin.ModelAdmin):
    model = Horario


admin.site.register(Tarjeta, TarjetaAdmin)
admin.site.register(Horario, HorarioAdmin)
