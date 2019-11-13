from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from registro.models import Periodo, Distributivo, Documento, Informe, Carrera
import os.path

class Command(BaseCommand):
    help = '''Genera los directorios de cada documento microcuricular para las asignaturas 
    de un periodo establecido. Si un directorio ya se encuentra generado, no se vuleve a generar'''

    def get_version(self):
        return '0.2'

    def add_arguments(self, parser):
        parser.add_argument(
            'periodo',
            help='Número de periodo para el cual se genera los informes'
        )

        parser.add_argument(
            'carrera',
            help='Nombre de la carrera entre comillas. Ejemplo: INGENIERÍA DE SISTEMAS'
        )



    def handle(self, *args, **options):
        in_periodo = options['periodo']
        in_carrera = options['carrera']

        path_estatico = "./media/documents/firmados"

        # obtener el periodo para el cual se generan los directorios
        periodo = Periodo.objects.filter(numero=in_periodo).first()

        # obtener la carrera
        carrera=Carrera.objects.filter(nombre=in_carrera).first()

        # obtener los distributivos
        distributivos = Distributivo.objects.filter(periodo=periodo).filter(materia__carrera=carrera)

        dir_home = path_estatico + "/" + str(periodo) + "/" + str(carrera)
        os.makedirs(dir_home,exist_ok=True)

        for d in distributivos:
        	# armar path del docente
            dir_docente = dir_home + '/' + str(d.docente)
            # verificar si existe el directorio
            existe = self.existe_path(dir_docente)
            if not existe:
            	# crear el directorio docente
                os.makedirs(dir_docente)
                self.stdout.write("[+] Docente: " + str(d.docente))
            # armar path de la asignatura
            dir_materia= dir_docente + "/" + str(d)
            # verificar si existe el directorio
            existe = self.existe_path(dir_materia)
            if not existe:
            	# crear directorio materia
                os.makedirs(dir_materia)
                self.stdout.write("[+]   Materia: " + str(d)) 
    
    @staticmethod
    def existe_path(path1):
        estado=os.path.exists(path1)
        return estado


