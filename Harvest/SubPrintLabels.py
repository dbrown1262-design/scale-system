from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import tempfile
import os
import sys
import subprocess


        # build 2" x 3" PDF label
def PrintOneLabel(Strain, LabelType,HarvestDate, ToteType, ToteNo, Weight):

    w = 230
    h = 140
    c = canvas.Canvas("C:\\labels\\label.pdf", pagesize=(w, h))
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(115, 115, Strain)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(115, 90, LabelType)
    c.drawCentredString(115, 70, f"Harvest Date: {HarvestDate}")
    c.drawCentredString(115, 50, f"{ToteType}: {ToteNo}")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(115, 25, f"{Weight} Grams")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(115, 5, "Adirondack Hemp Company")
    c.showPage()
    c.save()
#    os.startfile("C:\\labels\\label.pdf", "print")

    command = "{} {}".format('c:\\labels\\PDFtoPrinter.exe','C:\\labels\\label.pdf')
    subprocess.call(command,shell=True)
#PrintOneLabel("Chocolate Dipped Bananas","Bucked Flower","2024-06-15","Tote",42,15000)

