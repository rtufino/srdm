from tutoria.models import Firma, Tarjeta, ReporteTutoria, Horario, Distributivo
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
import time
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.http import HttpResponse

# Create your views here.
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.pagesizes import letter
from django.core.files import File
import os

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

    def setbarcode(self, cedula):
        try:
            return (code128.Code128(cedula, barHeight=3 * mm, barWidth=1))

        except Exception as e:
            pass

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


    def generar_reporte(self,alumno):

        return
