from tutoria.models import Firma, Tarjeta, ReporteTutoria, Horario, Distributivo

class Servicios_t(object):

    def get_num_tutorias(self,estudiante):
    #funcion recibe estudiante y devuelve el número de tutorias tomadas
        num_tutorias=Firma.objects.filter(alumno=estudiante).count()
        return num_tutorias
    def generar_reporte(self):

        return
