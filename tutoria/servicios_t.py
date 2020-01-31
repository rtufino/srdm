from tutoria.models import Firma, Tarjeta, ReporteTutoria, Horario, Distributivo

class Servicios_t(object):

    def get_num_tutorias(self,estudiante):
    #funcion recibe estudiante y devuelve el número de tutorias tomadas
        num_tutorias=Firma.objects.filter(alumno=estudiante).count()
        return num_tutorias

    def get_hash(self):

        return

    def marca_tiempo(self):

        return

    def get_duracion(self):

        return

    def get_observacion(self):

        return

    def get_dia(self):

        return

    def get_hora_inicio(self):
        return

    def get_hora_fin(self):
        return



    def generar_reporte(self,alumno):

        return
