from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


# Create your models here.


class Usuario(AbstractUser):
    es_docente = models.BooleanField(default=False)
    es_estudiante = models.BooleanField(default=False)
    es_revisor = models.BooleanField(default=False)
    es_verificador = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    def nombre(self):
        return self.last_name + " " + self.first_name


class Docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=10, default='9999999999')

    def __str__(self):
        return self.usuario.nombre()


class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=10, default='9999999999')

    def __str__(self):
        return self.usuario.nombre()


class Periodo(models.Model):
    numero = models.IntegerField()
    descripcion = models.CharField(max_length=128)
    activo = models.BooleanField(default=False)

    def __str__(self):
        return 'P' + str(self.numero)


class Carrera(models.Model):
    director = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=64)
    activo = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Materia(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=32)
    nombre = models.CharField(max_length=128)
    nivel = models.SmallIntegerField(default=0)
    activo = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Distributivo(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    grupo = models.CharField(max_length=16, default='1')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.materia.nombre + " - G" + self.grupo


class Alumno(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    distributivo = models.ForeignKey(Distributivo, on_delete=models.CASCADE)
    es_presidente = models.BooleanField(default=False)

    def __str__(self):
        return self.estudiante.usuario.nombre()


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=64)
    solo_presidente = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Documento(models.Model):
    PARCIAL_CHOICES = [
        ('0', 'TODOS'),
        ('1', '1'),
        ('2', '2'),
    ]

    tipo = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=8)
    descripción = models.CharField(max_length=512)
    activo = models.BooleanField(default=True)

    mensaje_compromiso = models.CharField(max_length=1024, default='')
    parcial = models.CharField(max_length=1, choices=PARCIAL_CHOICES, default='1')

    def __str__(self):
        return self.codigo


class Informe(models.Model):
    distributivo = models.ForeignKey(Distributivo, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    fecha_habilitacion = models.DateField()
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    parcial = models.SmallIntegerField(default=1)
    hash = models.CharField(max_length=512, null=True, blank=True)
    archivo = models.URLField(null=True, blank=True)
    estado = models.CharField(max_length=1, default='A')
    fecha_cierre = models.DateField()

    def __str__(self):
        return str(self.distributivo) + " (" + self.documento.codigo + ")"

    def esta_habilitado(self):
        hoy = datetime.datetime.now().date()
        return self.fecha_habilitacion <= hoy <= self.fecha_cierre


class Firma(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    informe = models.ForeignKey(Informe, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=512)
    observacion = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.alumno.estudiante.usuario.nombre()


class ValidarFirma(models.Model):
    documento_id = models.CharField(max_length=255, blank=True)
    validacion = models.BooleanField(default=False)

    def __str__(self):
        return self.validacion
