
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from registro.models import Periodo, Distributivo, Documento, Informe


class Command(BaseCommand):
    help = '''Genera los informes de cada documento microcuricular para las asignaturas 
    de un periodo establecido. Si un informe ya se encuentra generado, no se vuleve a generar'''

    def get_version(self):
        return '0.1'

    def add_arguments(self, parser):
        parser.add_argument(
            'periodo',
            help='Número de periodo para el cual se genera los informes'
        )

        parser.add_argument(
            'parcial',
            help='Número del parcial (1 o 2) para el cual se genera los informes'
        )

        parser.add_argument(
            'fecha-habilitacion',
            help='Fecha de habilitación en formato dd-mm-yyyy'
        )

        parser.add_argument(
            'fecha-cierre',
            help='Fecha de cierre en formato dd-mm-yyyy'
        )

    def handle(self, *args, **options):
        periodo = options['periodo']
        parcial = options['parcial']
        fh = options['fecha-habilitacion']
        fc = options['fecha-cierre']

        # obtener el periodo activo
        periodo = Periodo.objects.filter(numero=periodo).first()

        # obtener los distributivos
        distributivos = Distributivo.objects.filter(periodo=periodo)

        # obtener documentos
        documentos = Documento.objects.filter(activo=True, parcial__in=['0', parcial])

        # establecer la fecha de habilitación
        fecha_h = datetime.strptime(fh, '%d-%m-%Y')

        # establecer fecha de cierre
        fecha_c = datetime.strptime(fc, '%d-%m-%Y')

        for d in documentos:
            for m in distributivos:
                existe = self.existe_informe(m, d, int(parcial))
                if not existe:
                    # crear un informe
                    informe = Informe(
                        distributivo=m,
                        documento=d,
                        fecha_habilitacion=fecha_h,
                        fecha_cierre=fecha_c,
                        parcial=int(parcial),
                        estado='A'
                    )
                    self.stdout.write("[+] Generando " + str(informe))
                    informe.save()
                else:
                    self.stdout.write("[-] Ya existe " + str(d) + " para " + str(m))

    @staticmethod
    def existe_informe(distributivo, documento, parcial):
        i = Informe.objects.filter(distributivo=distributivo, documento=documento, parcial=parcial)
        return len(i) > 0