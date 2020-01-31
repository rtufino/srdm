from tutoria.models import Firma, Horario


class Servicios_t(object):

    def get_num_tutorias(self,estudiante):
    #funcion recibe estudiante y devuelve el número de tutorias tomadas
        num_tutorias=Firma.objects.filter(alumno=estudiante).count()
        print("numero tutoias:",num_tutorias)
        return num_tutorias

    def get_observacion(self,estudiante):
       observacion=Firma.objects.filter(alumno=estudiante).values('observacion')
       print("temas:", observacion)
       return observacion

    def get_inicio(self,estudiante):
        inicio = Horario.objects.filter(alumno=estudiante).values('hora_inicio')
        print("hora inicio:", inicio)

        return inicio

    def get_fin(self,estudiante):
        fin = Horario.objects.filter(alumno=estudiante).values('hora_fin')
        print("hora fin:", fin)
        return fin
