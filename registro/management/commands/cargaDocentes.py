import csv

from django.core.management.base import BaseCommand, CommandError
from registro.models import Periodo, Carrera, Usuario, Docente, Materia, Distributivo


class Command(BaseCommand):
    help = '''Carga los datos de docentes a partir de datos 
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
        print(len(registros))

        self.stdout.write("[*] Creando Docentes ...")
        for row in registros:
            self.crear_docente(row)

        self.stdout.write("[*] Creando Materias ...")
        for row in registros:
            self.crear_materia(row)

        self.stdout.write("[*] Creando Distributivos ...")
        for row in registros:
            self.crear_distributivo(periodo, row)

    @staticmethod
    def crear_docente(docente):
        # obtener la carrera
        carrera = docente[3]
        carrera_ds = Carrera.objects.filter(nombre=carrera)
        if len(carrera_ds) == 0:
            print("[!] Error: No existe la carrera:", carrera)
            return None

        correo = docente[11]
        cedula = docente[4]
        data = Usuario.objects.filter(username=correo)
        if len(data) > 0:
            print("[-] Ya existe:", data[0])
            return data[0].docente
        # Crear el usuario
        usuario = Usuario(
            email=correo,
            es_docente=True,
            es_estudiante=False,
            es_revisor=False,
            es_verificador=False,
            first_name=docente[6],
            last_name=docente[5],
            is_active=True,
            is_staff=False,
            is_superuser=False,
            username=correo
        )
        usuario.set_password(cedula)
        # guardar en BDD
        usuario.save()
        docente = Docente(
            usuario=usuario,
            cedula=cedula
        )
        docente.save()
        print("[+] Creando ", usuario.pk, usuario)

    @staticmethod
    def crear_materia(registro):
        # obtener la carrera
        carrera = registro[3]
        carrera_ds = Carrera.objects.filter(nombre=carrera)
        if len(carrera_ds) == 0:
            print("[!] Error: No existe la carrera:", carrera)
            return None

        carrera_obj = carrera_ds[0]
        materia_cod = registro[7]
        materia_ds = Materia.objects.filter(codigo=materia_cod)
        if len(materia_ds) > 0:
            print("[-] Ya existe:", materia_ds[0])
            return materia_ds[0]
        else:
            # Crear la materia
            materia = Materia(
                codigo=materia_cod,
                nombre=registro[8],
                carrera=carrera_obj,
                nivel=registro[10],
                activo=True
            )
            # guardar en BDD
            materia.save()
            print("[+] Creando ", carrera, "-", materia)
            return materia

    @staticmethod
    def crear_distributivo(periodo, docente):
        # obtener la carrera
        carrera = docente[3]
        carrera_ds = Carrera.objects.filter(nombre=carrera)
        if len(carrera_ds) == 0:
            print("[!] Error: No existe la carrera:", carrera)
            return None

        # obtener el periodo
        periodo_ds = Periodo.objects.filter(numero=periodo)
        if len(periodo_ds) == 0:
            print("[!] Error: No existe el período:", periodo)
            return None

        # obtener la materia
        materia_cod = docente[7]
        materia_nom = docente[8]
        materia_ds = Materia.objects.filter(codigo=materia_cod)
        if len(materia_ds) == 0:
            print("[!] Error: No existe la materia:", materia_cod, materia_nom)
            return None

        # obtener el docente
        cedula = docente[4]
        nombre = docente[5] + ' ' + docente[6]
        docente_ds = Docente.objects.filter(cedula=cedula)
        if len(docente_ds) == 0:
            print("[!] Error: No existe el docente:", cedula, nombre)
            return None

        # crear distributivo
        docente_obj = docente_ds[0]
        materia_obj = materia_ds[0]
        periodo_obj = periodo_ds[0]
        grupo = docente[9]
        distributivo = Distributivo(
            docente=docente_obj,
            materia=materia_obj,
            periodo=periodo_obj,
            activo=True,
            grupo=grupo
        )
        # verificar si el distributivo ya existe
        distributivo_ds = Distributivo.objects.filter(
            docente=distributivo.docente,
            materia=distributivo.materia,
            periodo=distributivo.periodo,
            grupo=distributivo.grupo
        )
        if len(distributivo_ds) > 0:
            print("[-] Ya existe:", distributivo_ds[0])
            return distributivo_ds[0]
        else:
            # guardar el distributivo
            distributivo.save()
            print("[+] Creado:", distributivo)
            return distributivo
