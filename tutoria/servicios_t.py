from tutoria.models import Firma #, Horario
from registro.models import Periodo,Distributivo
import time
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.http import HttpResponse

from django.shortcuts import render, redirect
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import letter, A4
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm, cm
# from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

import hashlib
import io
from io import BytesIO

from reportlab.pdfgen import canvas

from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing

# Create your views here.
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.pagesizes import letter
from django.core.files import File

PARCIAL=1
class Servicios_t(object):

    def get_num_tutorias(self, estudiante,parcial):
        # funcion recibe estudiante y devuelve el número de tutorias tomadas
        num_tutorias = Firma.objects.filter(estudiante_id=estudiante,reporte__parcial=parcial).count()
        print("numero tutorias:", num_tutorias)
        return num_tutorias

    def get_observacion(self, estudiante,parcial):
        observacion = Firma.objects.filter(estudiante=estudiante,reporte__parcial=parcial).values_list('tema', flat=True)

        print("temas:", observacion)
        return observacion

    def get_inicio(self, estudiante,parcial):
        informe_id = Firma.objects.filter(estudiante=estudiante,reporte__parcial=parcial).values_list('id', flat=True)
        print(informe_id)
        hora_inicio = []
        # for i in informe_id:
            # print("**informe_id**",i['id'])
            # hora = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_inicio', flat=True)[0].hour
            # minuto = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_inicio', flat=True)[0].minute
            # second = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_inicio', flat=True)[0].second
            # inicio = str(hora) + ":" + str(minuto)
            # hora_inicio.append(inicio)
        # print("hora inicio:", inicio)
        # print("hora inicio",hora_aux)
        return hora_inicio

    def get_fin(self, estudiante,parcial):
        informe_id = Firma.objects.filter(estudiante=estudiante,reporte__parcial=parcial).values_list('id', flat=True)
        print(informe_id)
        hora_fin = []
        # for i in informe_id:
        #     # print("**informe_id**",i['id'])
        #     hora = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_fin', flat=True)[0].hour
        #     minuto = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_fin', flat=True)[0].minute
        #     second = Horario.objects.filter(pk=i).values_list('distributivo__horario__hora_fin', flat=True)[0].second
        #     fin = str(hora) + ":" + str(minuto)
        #     hora_fin.append(fin)
        #     # print("hora inicio:", inicio)
        # print("hora inicio",hora_aux)
        return hora_fin

    def get_dia(self, estudiante,parcial):
        informe_id = Firma.objects.filter(estudiante=estudiante,reporte__parcial=parcial).values_list('id', flat=True)
        print(informe_id)
        dia_aux = []
        # for i in informe_id:
        #     # print("**informe_id**",i['id'])
        #     dia = Horario.objects.filter(pk=i).values_list('distributivo__horario__dia', flat=True)[0]
        #
        #     dia_aux.append(dia)
        #     # print("hora inicio:", inicio)
        print("hora inicio", dia_aux)
        return dia_aux


    def get_timestamp(self,estudiante,parcial):
        time_stamp=Firma.objects.filter(estudiante=estudiante,reporte__parcial=parcial).values_list('timestamp',flat=True)
        return time_stamp

    def get_duracion(self,estudiante,parcial):
        duracion=Firma.objects.filter(estudiante=estudiante,reporte__parcial=parcial).values_list('duracion',flat=True)
        return duracion

    def gen_cabecera_table(self):
        headings=('Nombre del Estudiante', 'cédula', 'Firma', 'Tema', 'Fecha')
        return headings

    def getFecha(self):
        fecha = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        fecha1 = fecha.replace("-", '')
        fecha2 = fecha1.replace(":", '')
        fecha3 = fecha2.replace(" ", '')

        return fecha
    def get_data(self,distributivo_id):
        periodo = Distributivo.objects.filter(pk=distributivo_id,periodo__activo=True)[0].periodo
        materia = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.nombre
        codigo=Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.codigo
        grupo=Distributivo.objects.filter(pk=distributivo_id)[0].grupo
        #grupo=Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.
        nombre_docente=Distributivo.objects.filter(pk=distributivo_id,periodo_id=periodo,)[0].docente.usuario.nombre()
        carrera = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.carrera
        nivel= Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.nivel
        fecha=self.getFecha()
        datos={
            "carrera":carrera.nombre,
            "nombre_docente":nombre_docente,
            "materia":materia,
            "codigo":codigo,
            "periodo":periodo.numero,
            "grupo":grupo,
            "nivel":nivel,
            "fecha":fecha,
            "parcial":PARCIAL,
                    }
        print("*****datos*******",datos)

    def createqr(self, enlace):
        # generate and rescale QR
        qr_code = qr.QrCodeWidget(enlace)
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        drawing = Drawing(
            3.5 * cm, 3.5 * cm, transform=[3.5 * cm / width, 0, 0, 3.5 * cm / height, 0, 0])
        drawing.add(qr_code)

        return drawing

    #
    def sethash(self, materia, tipo):
        # modificado para parcial 2
        # i=Informe.objects.filter(distributivo_id=materia,documento__codigo=tipo)
        print("######", tipo)
        i = Informe.objects.filter(distributivo_id=materia, documento__codigo=tipo, parcial=PARCIAL)

        print("hashh", i)
        return i[0]

    def crear_directorio(self, periodo, carrera, docente, materia, grupo):
        path = "./media/documents/firmados" + "/" + "P" + str(periodo) + "/" + str(carrera) + "/" + str(
            docente) + "/" + str(materia) + " - G" + str(grupo) + "/"
        print(path)
        return str(path)

    def gen_reporte(self,datos,tipo,distributivo):

        print("entra al reporte")
        buff = BytesIO()
        buff1 = BytesIO()

        ###############################################333
        doc1 = SimpleDocTemplate(buff1,
                                 pagesize=A4,
                                 rightMargin=15,
                                 leftMargin=15,
                                 topMargin=25,
                                 bottomMargin=30,
                                 )
        clientes1 = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="ejemplo", aligment=TA_CENTER, fontSize=8,
                                  fontName="Times-Bold", spaceBefore=24, spaceAfter=0))
        ##################################################################################3
        doc = SimpleDocTemplate(buff,
                                pagesize=A4,
                                rightMargin=15,
                                leftMargin=15,
                                topMargin=30,
                                bottomMargin=30,
                                )
        clientes = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="ejemplo", aligment=TA_CENTER, fontSize=8,
                                  fontName="Times-Bold"))
        print("Genero el PDF")
        response = HttpResponse(content_type='application/pdf')
        documentoid= self.gen_documento_id(tipo)
        pdf_name = documentoid  # llamado clientes
        response['Content-Disposition'] = 'inline; filename=%s' % pdf_name

        header = Paragraph("CARRERA " + nombre_carrera + " <br/>", styles['ejemplo'])
        header2 = Paragraph("Registro de Firmas de la Recepción de Exámenes. <br/>", styles['ejemplo'])
        # header3=Paragraph("Por medio del presente documento, el docente y los estudiantes que firman la lista, certifican que revisarion los exámenes <br/>", styles['ejemplo'])
        header4 = Paragraph("<br/> <br/>", styles['ejemplo'])
        clientes.append(header)
        clientes.append(header2)
        # clientes.append(header3)
        clientes.append(header4)

        #     alumnos = servicios.getalumnos(distributivo_id)
        #     # print(alumnos)
        #
        #     for q in alumnos:
        #
        #         cedula = q.estudiante.cedula
        #         tutorias = servicios_t.get_num_tutorias(cedula)
        #         observaciones=servicios_t.get_observacion(cedula)
        #         inicio=servicios_t.get_inicio(cedula)
        #         fin=servicios_t.get_fin(cedula)
        #         dia=servicios_t.get_dia(cedula)
        #         #print("********dia",dia)
        #         # print(cedula)
        #         valid = servicios.validardocumentos(q.pk, tipo)
        #         #valid="True"
        #         if valid == "True":
        #             for i in range(0,tutorias):
        #                 #print("*****i",inicio[i])
        #                 #print("****f",fin[i])
        #                 #print("***o",observaciones[i])
        #                 #print("***d",dia[i])
        #                 allclientes = (q.estudiante, q.estudiante.cedula,
        #                            code128.Code128(q.estudiante.cedula, barHeight=3 * mm, barWidth=1),inicio[i],fin[i],observaciones[i],dia[i])
        #
        #
        #                 allclientes2.append(allclientes)
        #         #allclientes2.append(allclientes)
        #             #print("clientes",allclientes2)
        #     #print("***clientes***", allclientes2)
        #
        #     # clientes.append(header3)
        ################################################################

        headings2 = ('', '')
        docente_nombre = docente
        materiaid = materia
        # print(materias)
        # for p in materias:
        allcabecera = [('CARRERA:', nombre_carrera), ('NOMBRE DEL DOCENTE:', docente_nombre),
                       ('MATERIA:', materia_nombre),
                       ('Periodo:', str(periodo_numero) + " (" + str(periodo_descripcion) + ")"),
                       ('GRUPO:', grupo), ('NIVEL:', nivel), ('FECHA:', time.strftime("%Y-%m-%d"))]
        t1 = Table(allcabecera)
        t1.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (3, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.transparent)
            ]
        ))
        clientes.append(t1)
        clientes.append(header4)

        headings = ('Nombre del Estudiante', 'No de cédula', 'Firma')

        # *******************************************************************

        print(allclientes2)

        t = Table([headings] + allclientes2, repeatRows=0)
        t.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (3, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.transparent)
            ]
        ))

        # buff.close()

        # id_docente = Paragraph("<br/> Firmado por: " + str(docente_nombre) + " <br/> <br/>", styles['ejemplo'])
        id_docente = Paragraph("Firmado por: " + str(docente_nombre), styles['ejemplo'])
        # hash_1 = Paragraph("Documento ID: " + hash + " <br/>", styles['ejemplo'])
        fecha = Paragraph("Fecha:" + str(time.strftime("%Y-%m-%d")), styles['ejemplo'])
        verificacion = Paragraph("Puede revisar la validez del documento en http://172.17.42.144/validar",
                                 styles['ejemplo'])

        clientes.append(t)

        numEst = len(allclientes2)
        if numEst > 21 and numEst < 32:
            clientes.append(PageBreak())

        clientes.append(id_docente)
        clientes.append(fecha)
        clientes.append(verificacion)
        # print(clientes)
        # genera bufer
        clientes1 = clientes.copy()
        # print(clientes1)
        # buff1 = buff
        doc.build(clientes)

        #########################################sacar hash################
        BLOCKSIZE = 65536
        hasher = hashlib.sha1()

        buff.seek(0)
        buf = buff.read(BLOCKSIZE)
        # print(buff)
        while len(buf) > 0:
            hasher.update(buf)
            buf = buff.read(BLOCKSIZE)
            # print("buf", buf)
        hash = hasher.hexdigest()
        # print(hash)
        ########################################################################

        ##########################################################################
        hash_1 = Paragraph("Documento ID: " + hash + " <br/>", styles['ejemplo'])
        clientes1.append(hash_1)
        qr = self.createqr("http://172.17.42.144/validar")
        clientes1.append(qr)

        # print(clientes1)
        doc1.build(clientes1)

        response.write(buff1.getvalue())
        ip = "172.17.42.144"
        directorio = self.crear_directorio(periodo_numero, nombre_carrera, docente_nombre, materia_nombre, grupo)
        # path = "./media/documents/firmados"
        # path_id = str(path + pdf_name + ".pdf")
        url = "http://" + str(ip) + "/" + directorio + pdf_name + ".pdf"
        # url = "http://" + str(ip) + "/" + "media/documents/firmados/" + pdf_name + ".pdf"
        print("URL", url)
        with open(directorio + pdf_name + ".pdf", 'wb') as f:
            myfile = File(f)
            f = open(directorio + pdf_name + ".pdf", 'wb')
            myfile = File(f)
            myfile.write(buff1.getvalue())
        myfile.closed
        f.close()

        buff.close()
        buff1.close()

        s = self.sethash(distributivo_id, documento)

        s.hash = hash
        s.fecha_generacion = time.strftime("%Y-%m-%d %H:%M:%S")
        s.archivo = url
        s.estado = "C"
        s.save()

        return response

        return