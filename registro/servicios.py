from registro.models import Estudiante, Alumno, Materia, Carrera, Docente, Distributivo, Periodo, Informe, Documento, \
    Firma, ValidarFirma
from django.contrib.auth import get_user
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
#
from tutoria.models import Firma, ReporteTutoria
#
#from tutoria.servicios_t import Servicios_t
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
import os
#servicios_t=Servicios_t()
PARCIAL=2

class Servicios(object):
    # Funcion que devuelve el nombre del usuario
    def getuser(self, usuario):
        try:
            return (Docente.objects.filter(usuario=usuario)[0])
        except Exception as e:
            pass

    # Funcion que devuelve las materias de un docente
    def getmaterias(self, docente,periodo):
        try:
            return (Distributivo.objects.filter(docente=docente,periodo=periodo))
        except Exception as e:
            pass

    # Funcion que devuelve los detalles de una materia
    def materia_detalles(self, materia):
        try:
            periodo = Periodo.objects.filter(activo=True).first()
            return (Materia.objects.filter(nombre=materia).values())
        except Exception as e:
            pass

    # Funcion que devuelve los detalles de una carrera
    def carrera_detalles(self, id):
        try:
            periodo=Periodo.objects.filter(activo=True).first()
            return (Distributivo.objects.filter(periodo_id=periodo,materia_id=id).values())
        except Exception as e:
            pass

    # Función que devuelve la carrera
    def getcarrera(self, id):
        try:
            return (Carrera.objects.filter(id=id).values())
        except Exception as e:
            pass

    # Funcion que devuelve los detalles del periodo academico
    def periodo_detalles(self, id):
        try:
            return Periodo.objects.filter(id=id).values()
        except Exception as e:
            pass

    # Funcion que devuelve los estudiante de una materia
    def getalumnos(self, distributivo_id):
        try:
            periodo = Periodo.objects.filter(activo=True).first()
            #d = Distributivo.objec 
            d = Distributivo.objects.filter(pk=distributivo_id,periodo_id=periodo)[0].id
            print("----distributivo----",d)
            #modificado periodo 2

            return Alumno.objects.filter(distributivo=d)

        except Exception as e:
            pass

    # Funcion para generar código de barras de los estudiantes con cedula
    def setbarcode(self, cedula):
        try:
            return (code128.Code128(cedula, barHeight=3 * mm, barWidth=1))

        except Exception as e:
            pass

    def getFecha(self):
        fecha = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        fecha1 = fecha.replace("-", '')
        fecha2 = fecha1.replace(":", '')
        fecha3 = fecha2.replace(" ", '')

        return fecha3

    def getFechaActual(self):
        return time.strftime("%Y-%m-%d")

    def getHoraActual(self):
        return time.strftime("%H:%M")

    def getFechaActualCalendario(self):
        return time.strftime("%Y-%m-%d")

    def validardocente(self, docente, materia):
        if Distributivo.objects.filter(docente__carrera__materia__nombre=materia):
            return True
        else:
            return False

    def sethash(self,materia,tipo):
        #modificado para parcial 2
        #i=Informe.objects.filter(distributivo_id=materia,documento__codigo=tipo)
        print("######",tipo)
        i = Informe.objects.filter(distributivo_id=materia, documento__codigo=tipo, parcial=PARCIAL)

        print("hashh",i)
        return i[0]

    def verificar_estado_informe(self, materia, tipo):
        print(materia)
        #i = Informe.objects.filter(distributivo_id=materia, documento__codigo=tipo)
        #i = Informe.objects.filter(distributivo_id=materia,documento__codigo=tipo).values()
        periodo=Periodo.objects.filter(activo=True).first()
        i = Informe.objects.filter(distributivo_id=materia, documento__codigo=tipo,parcial=PARCIAL).values()
        print("tipo///",tipo)
        print("////estado",i)
        if len(i)!=0:

            print(i.first()['estado'])
            return i.first()
        else:
            print("resultado nulo")
            return None


    def getinforme(self, alumno):

        alu = Estudiante.objects.filter(cedula=alumno).values('id')
        print("****************** get informe *****************")
        print(alu)
        al_id = alu[0].get('id')
        print(al_id)
        doc = Documento.objects.filter(informe__firma__alumno_id=al_id)
        print(doc)
        return doc

    def crear_directorio(self,periodo,carrera,docente,materia,grupo):
        path="./media/documents/firmados"+"/"+"P"+str(periodo)+"/"+str(carrera)+"/"+str(docente)+"/"+str(materia)+" - G"+str(grupo)+"/"
        print(path)
        return str(path)

    def validar_materia_docente(self,distributivo_id,docente):
         val=Docente.objects.filter(distributivo=distributivo_id)
         print("validacion docente",val.first())
         print("docente",docente)
         if val.first()==docente:
            validacion=True
         else:
            validacion=False
         return validacion

    def validardocumentos(self, alumno, tipo):
        servicios = Servicios()
        alu = Estudiante.objects.filter(cedula=alumno).values('id')
        valid = "False"
        # documentos=Documento.objects.filter(informe__firma__alumno_id__in=alu)
        #documentos = Documento.objects.filter(informe__firma__alumno_id=alumno)
        documentos = Documento.objects.filter(informe__firma__alumno_id=alumno,informe__parcial=PARCIAL)
        #############################################################################################
        #modificado parcial 2
        print(documentos)
        if len(documentos) != 0:
            for m in documentos:
                codigo = m.codigo

                print("codigo", codigo)
                print("tipo", tipo)
                if m.codigo == tipo:
                    # print(m.codigo,tipo)
                    valid = "True"




        else:
            valid = "None"
        return valid

    def validarfirma(self, hash_id):

        hash_doc = Informe.objects.filter(hash=hash_id).values("hash").exists()

        if hash_doc==True:

            return hash_doc

        elif hash_doc==False:

            hash_doc = ReporteTutoria.objects.filter(hash=hash_id).values("hash").exists()

            if hash_doc==True:

                return hash_doc
            else:
                hash_doc=None
                return hash_doc




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

    def get_pdf(self, docente, distributivo_id, tipo):
        periodo = Periodo.objects.filter(activo=True).first()
        materia=Distributivo.objects.filter(pk=distributivo_id,periodo_id=periodo)[0].materia.nombre
        periodo = Periodo.objects.filter(activo=True).first()
        servicios = Servicios()
        #materias = servicios.getmaterias(docente,periodo)
        materia_detalles = servicios.materia_detalles(materia)
        validar = servicios.validardocente(docente, materia)
        print(validar)
        print(materia_detalles[0])
        nivel = materia_detalles[0].get('nivel')
        codigo = materia_detalles[0].get('codigo')
        materia_nombre = materia_detalles[0].get('nombre')
        carrera_id = materia_detalles[0].get('carrera_id')
        carrera_det = servicios.getcarrera(carrera_id)
        nombre_carrera = carrera_det[0].get('nombre')
        id_materia = materia_detalles[0].get('id')

        carrera_detalles = servicios.carrera_detalles(id_materia)
        grupo= Distributivo.objects.filter(pk=distributivo_id)[0].grupo
        #grupo = carrera_detalles[0].get('grupo')
        periodo_id = carrera_detalles[0].get('periodo_id')
        periodo_detalles = servicios.periodo_detalles(periodo_id)
        periodo_numero = periodo_detalles[0].get('numero')
        periodo_descripcion = periodo_detalles[0].get('descripcion')

        print(periodo_detalles)

        print(carrera_detalles)

        # attachment para descargar
        # inline para ver online
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
                                  fontName="Times-Bold",spaceBefore=24,spaceAfter=0))
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

        if tipo == "REVEX":
            #headings = ('Nombre del Estudiante', 'No de cédula', 'Firma')
            allclientes = []
            allclientes2 = []
            print("----------revex--------------")
            documento = "REVEX"
            codigo = codigo
            fecha = servicios.getFecha()

            documentoid = str(
                #modificado periodo 2    ####################################################################################
                #documento + "-" + str(codigo) + "-" + str(grupo) + "-" + str(periodo_numero) + "-" + str(fecha))
                documento + "-" + str(codigo) + "-" + str(grupo) + "-" + str(periodo_numero) + "-" + str(fecha)+"-"+str(PARCIAL))
            # print(documentoid)
            # print("Genero el PDF")
            response = HttpResponse(content_type='application/pdf')
            pdf_name = documentoid  # llamado clientes
            # la linea 26 es por si deseas descargar el pdf a tu computadora
            response['Content-Disposition'] = 'inline; filename=%s' % pdf_name

            header = Paragraph("CARRERA " + nombre_carrera + " <br/>", styles['ejemplo'])
            header2 = Paragraph("Registro de Firmas de la Recepción de Exámenes. <br/>", styles['ejemplo'])
            # header3=Paragraph("Por medio del presente documento, el docente y los estudiantes que firman la lista, certifican que revisarion los exámenes <br/>", styles['ejemplo'])
            header4 = Paragraph("<br/> <br/>", styles['ejemplo'])
            clientes.append(header)
            clientes.append(header2)
            # clientes.append(header3)
            clientes.append(header4)
            alumnos = servicios.getalumnos(distributivo_id)
            print(alumnos)
            for q in alumnos:
                cedula = q.estudiante.cedula
                # print(cedula)
                print("*******pk", q.pk)
                valid = servicios.validardocumentos(q.pk, tipo)
                print("VALID", valid)
                if valid == "True":
                    allclientes = (q.estudiante, q.estudiante.cedula,
                                   code128.Code128(q.estudiante.cedula, barHeight=3 * mm, barWidth=1))
                    allclientes2.append(allclientes)
            print(allclientes2)


        elif tipo == "ADM":
            print("---------------adm--------------")
            #headings = ('Nombre del Estudiante', 'No de cédula', 'Firma')
            allclientes = []
            allclientes2 = []
            documento = "ADM"
            fecha = servicios.getFecha()
            documentoid = str(
                documento + "-" + str(codigo) + "-" + str(grupo) + "-" + str(periodo_numero) + "-" + str(fecha)+"-"+str(PARCIAL))
            # documentoid = str(documento+"-"+str(codigo)+"-"+str(grupo)+"-"+str(periodo_numero)+"-"+ time.strftime("%Y-%m-%d %H:%M:%S"))
            # documentoid = str(documento + time.strftime("%Y-%m-%d %H:%M:%S"))
            # print(documentoid)
            # print("Genero el PDF")
            response = HttpResponse(content_type='application/pdf')
            pdf_name = documentoid  # llamado clientes
            # la linea 26 es por si deseas descargar el pdf a tu computadora
            response['Content-Disposition'] = 'inline; filename=%s' % pdf_name

            header = Paragraph("ACTA DE CONFIRMACION DE DIFUSIÓN DE DOCUMENTOS DOCENTES MICROCURRICULARES <br/> <br/>",
                               styles['ejemplo'])
            header2 = Paragraph(
                "Por medio del presente documento, el docente y los estudiantes que firman la lista, certifican que el contenido de los documentos micro curriculares (PLAN ANALÍTICO, SÍLABO Y RÚBRICAS DE EVALUACIÓN) correspondientes a la materia, han sido difundidos y socializados. <br/> <br/>",
                styles['Normal'])
            header4 = Paragraph("<br/> <br/>", styles['ejemplo'])
            clientes.append(header)
            clientes.append(header2)
            #alumnos = servicios.getalumnos(id_materia)
            alumnos = servicios.getalumnos(distributivo_id)
            print("alumnos",alumnos)
            for q in alumnos:
                cedula = q.estudiante.cedula
                # print(cedula)
                valid = servicios.validardocumentos(q.pk, tipo)
                print("VALID", valid)
                if valid == "True":
                    allclientes = (q.estudiante, q.estudiante.cedula,
                                   code128.Code128(q.estudiante.cedula, barHeight=3 * mm, barWidth=1))
                    allclientes2.append(allclientes)
            print(allclientes2)



        elif tipo == "RN30":
            print("-------------------rn30----------")
           # headings = ('Nombre del Estudiante', 'No de cédula', 'Firma')
            allclientes = []
            allclientes2 = []
            documento = "RN30"
            fecha = servicios.getFecha()
            documentoid = str(
                documento + "-" + str(codigo) + "-" + str(grupo) + "-" + str(periodo_numero) + "-" + str(fecha)+"-"+str(PARCIAL))    
                #modificado periodo2
                #documento + "-" + str(codigo) + "-" + str(grupo) + "-" + str(periodo_numero) + "-" + str(fecha))

            # print(documentoid)
            # print("Genero el PDF")
            response = HttpResponse(content_type='application/pdf')
            pdf_name = documentoid  # llamado clientes
            # la linea 26 es por si deseas descargar el pdf a tu computadora
            response['Content-Disposition'] = 'inline; filename=%s' % pdf_name
            header = Paragraph("CARRERA " + nombre_carrera + " <br/>", styles['ejemplo'])
            header2 = Paragraph("Registro de Firmas Notas sobre 30 Puntos. <br/>", styles['ejemplo'])
            # header3=Paragraph("Por medio del presente documento, el docente y los estudiantes que firman la lista, certifican que revisarion las notas sobre 30 puntos <br/>", styles['ejemplo'])

            header4 = Paragraph("<br/> <br/>", styles['ejemplo'])
            clientes.append(header)
            clientes.append(header2)
            clientes.append(header4)

            #alumnos = servicios.getalumnos(id_materia)
            alumnos = servicios.getalumnos(distributivo_id)
            # print(alumnos)
            
            for q in alumnos:
                
                cedula = q.estudiante.cedula
                # print(cedula)
                valid = servicios.validardocumentos(q.pk, tipo)
                if valid == "True":
                    allclientes = (q.estudiante, q.estudiante.cedula,
                                   code128.Code128(q.estudiante.cedula, barHeight=3 * mm, barWidth=1))
                    allclientes2.append(allclientes)
                

            print("***clientes***", allclientes2)

            # clientes.append(header3)
        # elif tipo=="tutoria":
        #     print("tutoria")
        #     headings = ('Nombre del Estudiante', 'No de cédula', 'Firma', 'Inicio', 'Fin', 'Tema','Día')
        #     ######################################################
        #     print("-------------------tutoria----------")
        #     allclientes = []
        #     allclientes2 = []
        #     documento = "tutoria"
        #     fecha = servicios.getFecha()
        #     documentoid = str(
        #         documento + "-" + str(codigo) + "-" + str(grupo) + "-" + str(periodo_numero) + "-" + str(
        #             fecha) + "-" + str(PARCIAL))
        #     # modificado periodo2
        #     # documento + "-" + str(codigo) + "-" + str(grupo) + "-" + str(periodo_numero) + "-" + str(fecha))
        #
        #     # print(documentoid)
        #     # print("Genero el PDF")
        #     response = HttpResponse(content_type='application/pdf')
        #     pdf_name = documentoid  # llamado clientes
        #     # la linea 26 es por si deseas descargar el pdf a tu computadora
        #     response['Content-Disposition'] = 'inline; filename=%s' % pdf_name
        #     header = Paragraph("CARRERA " + nombre_carrera + " <br/>", styles['ejemplo'])
        #     header2 = Paragraph("Registro de Tutorías. <br/>", styles['ejemplo'])
        #     # header3=Paragraph("Por medio del presente documento, el docente y los estudiantes que firman la lista, certifican que revisarion las notas sobre 30 puntos <br/>", styles['ejemplo'])
        #
        #     header4 = Paragraph("<br/> <br/>", styles['ejemplo'])
        #     clientes.append(header)
        #     clientes.append(header2)
        #     clientes.append(header4)
        #
        #     # alumnos = servicios.getalumnos(id_materia)
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

        t = Table([headings] + allclientes2,repeatRows=0)
        t.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (3, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.transparent)
            ]
        ))

        # buff.close()

        #id_docente = Paragraph("<br/> Firmado por: " + str(docente_nombre) + " <br/> <br/>", styles['ejemplo'])
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
        qr = servicios.createqr("http://172.17.42.144/validar")
        clientes1.append(qr)

        # print(clientes1)
        doc1.build(clientes1)

        response.write(buff1.getvalue())
        ip = "172.17.42.144"
        directorio = servicios.crear_directorio(periodo_numero, nombre_carrera, docente_nombre, materia_nombre, grupo)
        #path = "./media/documents/firmados"
        #path_id = str(path + pdf_name + ".pdf")
        url = "http://" + str(ip) + "/" + directorio + pdf_name + ".pdf"
        #url = "http://" + str(ip) + "/" + "media/documents/firmados/" + pdf_name + ".pdf"
        print("URL",url)
        with open(directorio +pdf_name + ".pdf", 'wb') as f:
            myfile = File(f)
            f = open(directorio + pdf_name + ".pdf", 'wb')
            myfile = File(f)
            myfile.write(buff1.getvalue())
        myfile.closed
        f.close()

        buff.close()
        buff1.close()

        s = servicios.sethash(distributivo_id, documento)

        s.hash= hash
        s.fecha_generacion = time.strftime("%Y-%m-%d %H:%M:%S")
        s.archivo = url
        s.estado = "C"
        s.save()

        return response
