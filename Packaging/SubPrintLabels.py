from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import tempfile
import os
import sys
import subprocess


        # build 2" x 3" PDF label
def PrintPackageLabel(Strain, HarvestDate, PackageType, CaseNo, MetrcID, Units, Weight):

    w = 230
    h = 140
    c = canvas.Canvas("C:\\labels\\label.pdf", pagesize=(w, h))
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(115, 115, Strain)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(115, 90, PackageType + f" Case #{CaseNo}")
    c.drawCentredString(115, 70, f"Harvest Date: {HarvestDate}")
    c.drawCentredString(115, 50, f"ID: {MetrcID}")
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(115, 25, f"{Units} Units {Weight} Grams")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(115, 5, "Adirondack Hemp Company")
    c.showPage()
    c.save()
    os.startfile("C:\\labels\\label.pdf", "print")

##    command = "{} {}".format('c:\\labels\\PDFtoPrinter.exe','C:\\labels\\label.pdf')
##    subprocess.call(command,shell=True)
#PrintPackageLabel("Chocolate Dipped Bananas","2024-06-15","Jars",1,"1A4120300001DE2000000002",10,2500)
