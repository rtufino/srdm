from django.db import models
from registro.models import Distributivo


# Create your models here.

class Tarjeta(models.Model):
    codigo = models.CharField(max_length=7, null=False, unique=True)
    hash = models.CharField(max_length=512, null=True, blank=True)
    ubicacion = models.CharField(max_length=128, null=False, blank=False)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} {self.ubicacion}"


class Horario(models.Model):
    DIA_SEMANA = [
        (1, "LUNES"),
        (2, "MARTES"),
        (3, "MIERCOLES"),
        (4, "JUEVES"),
        (5, "VIERNES"),
        (6, "SABADO"),
        (7, "DOMINGO"),
    ]
    dia = models.IntegerField(choices=DIA_SEMANA, default=1)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    distributivo = models.ForeignKey(Distributivo, on_delete=models.CASCADE)
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.distributivo.materia} - {self.dia} {self.hora_inicio}"


class ReporteTutoria(models.Model):
    distributivo = models.ForeignKey(Distributivo, on_delete=models.CASCADE)
    fecha_habilitacion = models.DateField()
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    parcial = models.SmallIntegerField(default=1)
    hash = models.CharField(max_length=512, null=True, blank=True)
    archivo = models.URLField(null=True, blank=True)
    estado = models.CharField(max_length=1, default='A')
    fecha_cierre = models.DateField()

    def __str__(self):
        return str(self.distributivo)


class Firma(models.Model):
    alumno = models.CharField(max_length=128, null=False, blank=False)
    informe = models.ForeignKey(ReporteTutoria, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=512)
    duracion = models.DurationField()
    observacion = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.alumno.estudiante.usuario.nombre()
