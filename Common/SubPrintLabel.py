from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import tempfile
import os
import sys
import subprocess


        # build 2" x 3" PDF label
def PrintOneLabel(Weight):

    w = 230
    h = 140
    c = canvas.Canvas("C:\\labels\\label.pdf", pagesize=(w, h))
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(115, 115, "Tare")
    c.drawCentredString(115, 90, f"{Weight}")
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(115, 5, "Adirondack Hemp Company")

    # QR code encoding "Tare <weight>"
    qr_code = qr.QrCodeWidget(f"Tare {Weight}")
    bounds = qr_code.getBounds()
    qr_width = bounds[2] - bounds[0]
    qr_height = bounds[3] - bounds[1]
    qr_size = 60
    d = Drawing(qr_size, qr_size, transform=[qr_size / qr_width, 0, 0, qr_size / qr_height, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, c, (w - qr_size) / 2, 20)

    c.showPage()
    c.save()
    os.startfile("C:\\labels\\label.pdf", "print")

#    command = "{} {}".format('c:\\labels\\PDFtoPrinter.exe','C:\\labels\\label.pdf')
#    subprocess.call(command,shell=True)
PrintOneLabel(2500)
