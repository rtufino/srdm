from tutoria.models import Firma, Horario


class Servicios_t(object):

    def get_num_tutorias(self,estudiante):
    #funcion recibe estudiante y devuelve el número de tutorias tomadas
        num_tutorias=Firma.objects.filter(alumno=estudiante).count()
        print("numero tutoias:",num_tutorias)
        return num_tutorias

    def get_observacion(self,estudiante):
       observacion=Firma.objects.filter(alumno=estudiante).values_list('observacion',flat=True)
       print("temas:", observacion)
       return observacion

    def get_inicio(self,estudiante):
        informe_id=Firma.objects.filter(alumno=estudiante).values_list('id',flat=True)
        print(informe_id)
        hora_inicio = []
        for i in informe_id:

           # print("**informe_id**",i['id'])
            hora=Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_inicio',flat=True)[0].hour
            minuto = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_inicio', flat=True)[0].minute
            second= Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_inicio', flat=True)[0].second
            inicio=str(hora)+":"+str(minuto)
            hora_inicio.append(inicio)
            #print("hora inicio:", inicio)
        #print("hora inicio",hora_aux)
        return hora_inicio

    def get_fin(self,estudiante):
        informe_id = Firma.objects.filter(alumno=estudiante).values_list('id', flat=True)
        print(informe_id)
        hora_fin = []
        for i in informe_id:
            # print("**informe_id**",i['id'])
            hora = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_fin', flat=True)[0].hour
            minuto = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_fin', flat=True)[0].minute
            second = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_fin', flat=True)[0].second
            fin = str(hora) + ":" + str(minuto)
            hora_fin.append(fin)
            # print("hora inicio:", inicio)
        # print("hora inicio",hora_aux)
        return hora_fin

    def get_dia(self,estudiante):
        informe_id = Firma.objects.filter(alumno=estudiante).values_list('id', flat=True)
        print(informe_id)
        dia_aux = []
        for i in informe_id:
            # print("**informe_id**",i['id'])
            dia = Horario.objects.filter(pk=i).values_list('distributivo__horario__dia', flat=True)[0]

            dia_aux.append(dia)
            # print("hora inicio:", inicio)
        print("hora inicio",dia_aux)
        return dia_aux