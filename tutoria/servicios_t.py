import hashlib
import os
import time
from io import BytesIO

import qrcode
from django.core.files import File
from django.http import HttpResponse
from reportlab.graphics.barcode import code128
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, PageBreak
from reportlab.platypus import Table

from registro.models import Periodo, Distributivo, Docente
from registro.servicios import Servicios
from tutoria.models import Firma, ReporteTutoria, Tarjeta
from SRDM.util import get_parcial, get_IP

# Create your views here.

PARCIAL = get_parcial()
IP = get_IP()
servicios = Servicios()


class Servicios_t(object):

    def get_cedula(self, user):
        cedula = Docente.objects.filter(usuario=user).values("cedula")
        for i in cedula:
            print(i['cedula'])
        print("cedula", i['cedula'])
        return i['cedula']

    def set_qr_hash_url(self, docente, qr_hash, url):
        docente_id = Docente.objects.filter(usuario=docente).values("id")
        url_aux = str(url)
        for i in docente_id:
            docente_aux = i['id']
        print("docente_id", docente_aux)
        t = Tarjeta.objects.filter(docente_id=docente_aux)

        print("existe", t.exists())
        if t.exists() is False:
            t = Tarjeta(
                docente_id=docente_aux,
                hash=qr_hash,
                url=url_aux
            )
            t.save()
        else:
            t_aux = Tarjeta.objects.get(docente_id=docente_aux)
            t_aux.url = url_aux
            t_aux.hash = qr_hash
            t_aux.save()
        print("guarda hash")
        return

    def crear_directorio_qr(self, periodo, docente):

        path = "./media/qrs" + "/" + str(periodo)
        print(path)
        if not os.path.exists(path):
            os.makedirs(path)
        return str(path)

    def generar_qr_png(self, enlace, output):
        qr = qrcode.QRCode(box_size=4)
        qr.add_data(enlace)
        qr.make()
        img = qr.make_image()
        # img = qrcode.make(enlace)
        img.save(output)
        return

    def generar_hash(self, cedula):
        codigo_hash = hashlib.sha224(str(cedula).encode()).hexdigest()
        print("codigo_hash", codigo_hash)
        return codigo_hash

    def get_num_tutorias(self, estudiante, parcial, periodo, distributivo_id):
        # funcion recibe estudiante y devuelve el número de tutorias tomadas
        num_tutorias = Firma.objects.filter(reporte__distributivo_id=distributivo_id, estudiante_id=estudiante,
                                            reporte__parcial=parcial, reporte__distributivo__periodo=periodo).count()
        # num_tutorias = Firma.objects.filter(estudiante_id=estudiante,reporte__parcial=parcial).count()
        print("numero tutorias:", num_tutorias)
        return num_tutorias

    def get_observacion(self, estudiante, parcial, periodo, distributivo_id):
        observacion = Firma.objects.filter(reporte__distributivo_id=distributivo_id, estudiante=estudiante,
                                           reporte__parcial=parcial,
                                           reporte__distributivo__periodo=periodo).values_list('tema', flat=True)
        print("temas:", observacion)
        return observacion

    def get_inicio(self, estudiante, parcial, periodo):
        informe_id = Firma.objects.filter(estudiante=estudiante, reporte__parcial=parcial,
                                          reporte__distributivo__periodo=periodo).values_list('id', flat=True)
        print(informe_id)
        hora_inicio = []
        return hora_inicio

    def get_fin(self, estudiante, parcial, periodo):
        informe_id = Firma.objects.filter(estudiante=estudiante, reporte__parcial=parcial,
                                          reporte__distributivo__periodo=periodo).values_list('id', flat=True)
        print(informe_id)
        hora_fin = []
        return hora_fin

    def get_dia(self, estudiante, parcial, periodo):
        informe_id = Firma.objects.filter(estudiante=estudiante, reporte__parcial=parcial,
                                          reporte__distributivo__periodo=periodo).values_list('id', flat=True)
        print(informe_id)
        dia_aux = []
        print("hora inicio", dia_aux)
        return dia_aux

    def get_timestamp(self, estudiante, parcial, periodo, distributivo_id):
        time_stamp = Firma.objects.filter(reporte__distributivo_id=distributivo_id, estudiante=estudiante,
                                          reporte__parcial=parcial, reporte__distributivo__periodo=periodo)
        lista = []
        for i in time_stamp:
            lista.append(i.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        return lista

    def get_duracion(self, estudiante, parcial, periodo, distributivo_id):
        duracion = Firma.objects.filter(reporte__distributivo_id=distributivo_id, estudiante=estudiante,
                                        reporte__parcial=parcial, reporte__distributivo__periodo=periodo).values_list(
            'duracion', flat=True)
        return duracion

    def gen_cabecera_table(self):
        headings = ('Estudiante', 'cédula', 'Tema', 'Fecha', 'Duración', 'Firma')
        return headings

    def getFecha(self):
        fecha = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        fecha1 = fecha.replace("-", '')
        fecha2 = fecha1.replace(":", '')
        fecha3 = fecha2.replace(" ", '')

        return fecha3

    def get_data(self, distributivo_id):
        periodo = Distributivo.objects.filter(pk=distributivo_id, periodo__activo=True)[0].periodo
        materia = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.nombre
        codigo = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.codigo
        grupo = Distributivo.objects.filter(pk=distributivo_id)[0].grupo
        nombre_docente = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo, )[
            0].docente.usuario.nombre()
        carrera = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.carrera
        nivel = Distributivo.objects.filter(pk=distributivo_id, periodo_id=periodo)[0].materia.nivel
        fecha = self.getFecha()
        datos = {
            "carrera": carrera.nombre,
            "nombre_docente": nombre_docente,
            "materia": materia,
            "codigo": codigo,
            "periodo": periodo.numero,
            "grupo": grupo,
            "nivel": nivel,
            "fecha": fecha,
            "parcial": PARCIAL,
        }
        # print("*****datos*******", datos)
        return datos

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
        i = ReporteTutoria.objects.filter(distributivo_id=materia, parcial=PARCIAL)
        if len(i) != 0:
            print("hashh", i)
            return i[0]
        else:
            print("ERROR HASH")
            return None

    def crear_directorio(self, periodo, carrera, docente, materia, grupo):
        path = "./media/documents/firmados" + "/" + "P" + str(periodo) + "/" + str(carrera) + "/" + str(
            docente) + "/" + str(materia) + " - G" + str(grupo) + "/"
        print(path)
        return str(path)

    def get_info(self, distributivo_id):
        informacion = []
        datos = []
        elemento_aux = []
        fechas_aux = []
        duracion_aux = []
        periodo = Distributivo.objects.filter(pk=distributivo_id, periodo__activo=True)[0].periodo
        # ************** se obtiene los alumnos por el id de distributivo ************
        for q in (servicios.getalumnos(distributivo_id)):
            elemento = []
            print(q.estudiante_id)
            nombre = q.estudiante
            cedula = q.estudiante.cedula
            elemento.append(nombre)
            tutorias = self.get_num_tutorias(q.estudiante_id, PARCIAL, periodo, distributivo_id)
            temas = self.get_observacion(q.estudiante_id, PARCIAL, periodo, distributivo_id)
            timestamp = self.get_timestamp(q.estudiante_id, PARCIAL, periodo, distributivo_id)
            duracion = self.get_duracion(q.estudiante_id, PARCIAL, periodo, distributivo_id)
            for i in temas:
                elemento.append(i)
            for i in timestamp:
                fechas_aux.append(i)

            for i in duracion:
                duracion_aux.append(i)
            elemento.append(tutorias)
            datos.append(elemento)
            for i in temas:
                elemento_aux.append(i)
            print("elemento_aux", elemento_aux)

            informacion_aux = {
                'nombre': q.estudiante,
                'cedula': q.estudiante.cedula,
                'num_tutorias': tutorias,
                'temas': elemento_aux,
                'fecha': fechas_aux,
                'duracion': duracion,
                'id': q.estudiante.pk
            }
            # print("informacion_aux",informacion_aux)

            informacion.append(informacion_aux)
            elemento_aux = []
            fechas_aux = []
            duracion_aux = []
        print("informacion", informacion)
        return informacion

    def verificar_estado_informe(self, materia, tipo):
        print(materia)
        # i = Informe.objects.filter(distributivo_id=materia, documento__codigo=tipo)
        # i = Informe.objects.filter(distributivo_id=materia,documento__codigo=tipo).values()
        periodo = Periodo.objects.filter(activo=True).first()
        i = ReporteTutoria.objects.filter(distributivo_id=materia, parcial=PARCIAL).values()
        print("tipo///", tipo)
        print("////estado", i)
        if len(i) != 0:

            print(i.first()['estado'])
            return i.first()
        else:
            print("resultado nulo")
            return None

    def gen_reporte(self, datos, tipo, distributivo):
        allclientes2 = []
        print("llega_distributivo", distributivo)
        print("entra al reporte")
        print("obtiene datos de materias y docente")
        datos_aux = self.get_data(distributivo)
        print("datos_obtenidos", datos_aux)

        buff = BytesIO()
        buff1 = BytesIO()

        ###############################################333
        doc1 = SimpleDocTemplate(buff1,
                                 pagesize=A4,
                                 rightMargin=7,
                                 leftMargin=7,
                                 topMargin=25,
                                 bottomMargin=30,
                                 )
        clientes1 = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="ejemplo", aligment=TA_CENTER, fontSize=8,
                                  fontName="Times-Bold", spaceBefore=24, spaceAfter=0), )
        ##################################################################################3
        doc = SimpleDocTemplate(buff,
                                pagesize=A4,
                                rightMargin=7,
                                leftMargin=7,
                                topMargin=30,
                                bottomMargin=30,
                                )
        clientes = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="ejemplo", aligment=TA_CENTER, fontSize=8,
                                  fontName="Times-Bold"))
        print("Genero el PDF")
        response = HttpResponse(content_type='application/pdf')
        fecha = self.getFecha()
        print("fecha", fecha)
        print("tipo", tipo)
        print("codigo", datos_aux['codigo'])
        print("grupo", datos_aux['grupo'])
        print("periodo", datos_aux['periodo'])
        print("parcial", PARCIAL)

        documentoid = str(str(tipo) + "-" + str(datos_aux['codigo']) + "-" + str(datos_aux['grupo']) + "-" + str(
            datos_aux['periodo']) + "-" + str(fecha) + "-" + str(PARCIAL))
        print("documento-id", documentoid)

        # documentoid= self.gen_documento_id(tipo)
        pdf_name = documentoid  # llamado clientes
        response['Content-Disposition'] = 'inline; filename=%s' % pdf_name

        header = Paragraph("CARRERA " + datos_aux['carrera'] + " <br/>", styles['ejemplo'])
        header2 = Paragraph("Registro de Firmas de tutorias. <br/>", styles['ejemplo'])
        # header3=Paragraph("Por medio del presente documento, el docente y los estudiantes que firman la lista, certifican que revisarion los exámenes <br/>", styles['ejemplo'])
        header4 = Paragraph("<br/> <br/>", styles['ejemplo'])
        clientes.append(header)
        clientes.append(header2)
        # clientes.append(header3)
        clientes.append(header4)
        print("Obtenemos datos de los estudiantes")
        print("datos de estudiantes", datos)
        #     alumnos = servicios.getalumnos(distributivo_id)
        #     # print(alumnos)
        #
        for q in datos:
            cedula = q['cedula']
            nombre_estudiante = q['nombre']
            numero_tutorias = q['num_tutorias']
            for i in range(0, numero_tutorias):
                print("temas", q['temas'][i])
                print("fechas", q['fecha'][i])
                print("duracion", q['duracion'][i])
                allclientes = (nombre_estudiante, cedula,
                               q['temas'][i], q['fecha'][i], q['duracion'][i],
                               code128.Code128(cedula, barHeight=2 * mm, barWidth=0.6))
                allclientes2.append(allclientes)
        ################################################################
        headings2 = ('', '')
        # docente_nombre = docente
        # materiaid = materia
        # print(materias)
        # for p in materias:
        allcabecera = [('CARRERA:', datos_aux['carrera']), ('NOMBRE DEL DOCENTE:', datos_aux['nombre_docente']),
                       ('MATERIA:', datos_aux['materia']),
                       ('Periodo:', str(datos_aux['periodo']) + " (" + str(PARCIAL) + ")"),
                       ('GRUPO:', datos_aux['grupo']), ('NIVEL:', datos_aux['nivel']),
                       ('FECHA:', time.strftime("%Y-%m-%d"))]
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

        headings = self.gen_cabecera_table()

        # *******************************************************************

        # print(allclientes2)

        t = Table([headings] + allclientes2,
                  repeatRows=0,
                  colWidths=[7 * cm, 2 * cm, 4 * cm, 3 * cm, 1.5 * cm, 3 * cm])
        # t = Table([headings], repeatRows=0)
        t.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (6, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BACKGROUND', (0, 0), (-1, 0), colors.transparent)
            ]
        ))

        # buff.close()

        # id_docente = Paragraph("<br/> Firmado por: " + str(docente_nombre) + " <br/> <br/>", styles['ejemplo'])
        id_docente = Paragraph("Firmado por: " + str(datos_aux['nombre_docente']), styles['ejemplo'])
        # hash_1 = Paragraph("Documento ID: " + hash + " <br/>", styles['ejemplo'])
        fecha = Paragraph("Fecha:" + str(time.strftime("%Y-%m-%d")), styles['ejemplo'])
        verificacion = Paragraph("Puede revisar la validez del documento en http://172.17.42.144/validar",
                                 styles['ejemplo'])

        clientes.append(t)
        ###############################################################
        numEst = len(allclientes2)

        if numEst > 21 and numEst < 32:
            clientes.append(PageBreak())
        ###################################################################
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
        directorio = self.crear_directorio(datos_aux['periodo'], datos_aux['carrera'], datos_aux['nombre_docente'],
                                           datos_aux['materia'], datos_aux['grupo'])
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

        s = self.sethash(distributivo, tipo)
        if s is not None:
            s.hash = hash
            s.fecha_generacion = time.strftime("%Y-%m-%d %H:%M:%S")
            s.archivo = url
            s.estado = "C"
            s.save()
        else:
            print("ERROR HASH")
        return response
