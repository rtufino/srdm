import csv

from django.core.management.base import BaseCommand, CommandError
from registro.models import Periodo, Carrera, Usuario, Estudiante, Materia, Distributivo, Alumno


class Command(BaseCommand):
    help = '''Carga los datos de estudiantes y materias a partir de datos 
    proporcionados por el departamento de informática de la UPS-Q'''

    def get_version(self):
        return '0.1'

    def add_arguments(self, parser):
        parser.add_argument(
            'periodo',
            help='Número de periodo para el cual se cargara la información'
        )

        parser.add_argument(
            'archivo',
            help='Path del archivo csv con la información para cargar al sistema'
        )

    def handle(self, *args, **options):
        periodo = options['periodo']
        archivo = options['archivo']

        registros = []
        with open(archivo) as csvfile:
            read_csv = csv.reader(csvfile, delimiter=';')
            for row in read_csv:
                registros.append(row)

        self.stdout.write("[*] Creando Estudiantes ...")
        for row in registros:
            self.crear_estudiante(row)

        self.stdout.write("[*] Matriculando Estudiantes ...")
        for row in registros:
            self.matricular(row, periodo)

    @staticmethod
    def crear_estudiante(estudiante):
        correo = estudiante[10]
        data = Usuario.objects.filter(username=correo)
        if len(data) > 0:
            return data[0].estudiante
        # Crear el usuario
        usuario = Usuario(
            email=correo,
            es_docente=False,
            es_estudiante=True,
            es_revisor=False,
            es_verificador=False,
            first_name=estudiante[4],
            last_name=estudiante[3],
            is_active=True,
            is_staff=False,
            is_superuser=False,
            username=correo
        )
        usuario.set_password(estudiante[2])
        # guardar en BDD
        usuario.save()
        estudiante = Estudiante(
            usuario=usuario,
            cedula=estudiante[2]
        )
        estudiante.save()
        print("[+] Creando ", usuario.pk, "-", usuario)
        return estudiante

    @staticmethod
    def matricular(registro, periodo):
        # obtener la carrera
        carrera = registro[1]
        carrera_ds = Carrera.objects.filter(nombre=carrera)
        if len(carrera_ds) == 0:
            print("[!] Error: No existe la carrera:", carrera)
            return None

        # obtener el periodo
        periodo_ds = Periodo.objects.filter(numero=periodo)
        if len(periodo_ds) == 0:
            print("[!] Error: No existe el período:", periodo)
            return None

        # obtener estudiante
        cedula = registro[2]
        estudiante_ds = Estudiante.objects.filter(cedula=cedula)
        if len(estudiante_ds) == 0:
            correo = registro[10]
            usuario_ds = Usuario.objects.filter(username=correo)
            if len(usuario_ds) > 0:
                print("[!] No existe es estudiante:",cedula,correo)
                usuario = usuario_ds[0]
                estudiante = Estudiante(
                    usuario = usuario,
                    cedula = cedula
                )
                estudiante.save()
                print("[+] Creando estudiante", cedula, usuario)
                estudiante_ds = Estudiante.objects.filter(cedula=cedula)
            else:
                print("[!] Error: No existe el estudiante:", cedula)
                return None

        # obtener la materia
        materia_cod = registro[5]
        materia_nom = registro[6]
        materia_ds = Materia.objects.filter(codigo=materia_cod)
        if len(materia_ds) == 0:
            print("[!] Error: No existe la materia:", materia_cod, materia_nom)
            return None

        # obtener el distributivo
        periodo_obj = periodo_ds[0]
        materia_obj = materia_ds[0]
        grupo = registro[7]
        distributivo_ds = Distributivo.objects.filter(
            materia=materia_obj, grupo=grupo, periodo=periodo_obj
        )
        if len(distributivo_ds) == 0:
            print("[!] Error: No existe el distributivo:", materia_obj, grupo, periodo_obj)
            return None

        # crear la matricula (alumno)
        distributivo_obj = distributivo_ds[0]
        estudiante_obj = estudiante_ds[0]
        alumno = Alumno(
            distributivo=distributivo_obj,
            estudiante=estudiante_obj
        )
        # verificar si el estudiante ya esta matriculado
        alumnos_ds = Alumno.objects.filter(
            distributivo=alumno.distributivo,
            estudiante=alumno.estudiante
        )
        if len(alumnos_ds) > 0:
            print("[-] Ya existe:", alumnos_ds[0])
            return alumnos_ds[0]
        else:
            # guardar en BDD
            alumno.save()
            print("[+] Matriculando:", alumno)
            return alumno
