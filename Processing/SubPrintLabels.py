from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import tempfile
import os
import sys
import subprocess


        # build 2" x 3" PDF label
def PrintLabel(BatchId, LabelType, BatchDate, Strain1, Strain2, Strain3, Strain4, Weight):

    w = 230
    h = 140
    c = canvas.Canvas("C:\\labels\\label.pdf", pagesize=(w, h))
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(115, 115, f"{LabelType} Batch {BatchId}")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(115, 95, f"Batch Date: {BatchDate}")
    c.drawCentredString(115, 75, Strain1)
    c.drawCentredString(115, 65, Strain2)
    c.drawCentredString(115, 55, Strain3)
    c.drawCentredString(115, 45, Strain4)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(115, 20, f"{Weight} Grams")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(115, 5, "Adirondack Hemp Company")
    c.showPage()
    c.save()

    command = "{} {}".format('c:\\labels\\PDFtoPrinter.exe','C:\\labels\\label.pdf')
    subprocess.call(command,shell=True)
"""
    # send to printer (Windows default print via os.startfile)
    try:
        if sys.platform.startswith('win'):
            # This will open the system print dialog for the file and send to default printer
            os.startfile(fname, "print")
            self.setStatus("Sent label to printer")
        else:
            # fallback: open the file
            os.startfile(fname)
            self.setStatus("Label saved and opened")
    except Exception as e:
        self.setStatus(f"Print failed: {e}")
"""
#PrintLabel("TSHASH202501", "Hash", "2025-11-19","Chocolate Dipped Bananas","Blue Lobster ",15000)

