from django.db import models
from registro.models import Distributivo, Docente, Estudiante


# Create your models here.

class Tarjeta(models.Model):
    hash = models.CharField(max_length=512, null=True, blank=True)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, null=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return "Tarjeta de " + self.docente.usuario.nombre()


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
    reporte = models.ForeignKey(ReporteTutoria, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    duracion = models.DurationField()
    tema = models.CharField(max_length=32, blank=True)
    hash = models.CharField(max_length=512)

    def __str__(self):
        return self.estudiante.usuario.nombre()


class Parametro(models.Model):
    clave = models.CharField(max_length=32, unique=True)
    valor = models.TextField()

    def __str__(self):
        return self.clave + " - " + self.valor[0:20]
