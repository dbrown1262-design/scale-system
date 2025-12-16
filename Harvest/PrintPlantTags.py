import customtkinter as ctk
from tkinter import messagebox, filedialog
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import qr
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import SubSupa
import tempfile
import os
import subprocess
import sys

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


APP_TITLE = "Print Plant Tags"
DEFAULT_FONT = ("Arial", 14)


class PrintPlantTagsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("520x200")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Crop", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.CropCombo = ctk.CTkComboBox(frame, values=[], width=280, font=DEFAULT_FONT, command=self.on_crop_selected)
        self.CropCombo.grid(row=0, column=1, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Strain", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], width=280, font=DEFAULT_FONT)
        self.StrainCombo.grid(row=1, column=1, sticky="w", pady=6)

        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12,0))
        
        self.BtnPrint = ctk.CTkButton(button_row, text="Print Tags", font=DEFAULT_FONT, command=self.print_tags)
        self.BtnPrint.pack(side="left", padx=(0,8))
        
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self.destroy).pack(side="left", padx=(0,8))

        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8,0))

        self.load_crops()

    def set_status(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def load_crops(self):
        try:
            crops = SubSupa.LoadCrops()
            if crops:
                self.CropCombo.configure(values=crops)
                self.CropCombo.set(crops[0])
            else:
                self.CropCombo.configure(values=["Select"])
                self.CropCombo.set("Select")
        except Exception as e:
            self.set_status(f"LoadCrops failed: {e}")

    def on_crop_selected(self, val=None):
        sel = (self.CropCombo.get() or "").strip()
        if not sel or sel.lower().startswith("select"):
            self.StrainCombo.configure(values=["Select"])
            self.StrainCombo.set("Select")
            return
        # crop label might be "19 - 2025-11-..." or just "19"
        token = sel.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status("Cannot parse Crop number")
                return
        try:
            strains = SubSupa.LoadStrains(crop_no)
            if strains:
                self.StrainCombo.configure(values=strains)
                self.StrainCombo.set(strains[0])
            else:
                self.StrainCombo.configure(values=["Select"])
                self.StrainCombo.set("Select")
        except Exception as e:
            self.set_status(f"LoadStrains failed: {e}")

    def print_tags(self):
        sel_crop = (self.CropCombo.get() or "").strip()
        sel_strain = (self.StrainCombo.get() or "").strip()
        if not sel_crop or sel_crop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not sel_strain or sel_strain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return

        # parse crop number
        token = sel_crop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status("Cannot parse Crop number")
                return

        try:
            rows = SubSupa.LoadPlantTags(crop_no, sel_strain)
            if not rows:
                self.set_status("No plant tags found")
                return
        except Exception as e:
            self.set_status(f"LoadPlantTags failed: {e}")
            return

        # Label size
        label_w = 2.25 * inch
        label_h = 0.75 * inch

        c = canvas.Canvas("C:\\labels\\label.pdf", pagesize=(label_w, label_h))

        for row in rows:
            # row is expected to have 'Strain' and 'PlantNo'
            strain = row.get('Strain') if isinstance(row, dict) else getattr(row, 'Strain', '')
            plantno = row.get('PlantNo') if isinstance(row, dict) else getattr(row, 'PlantNo', '')
            strain_text = str(strain or "")
            plant_text = str(plantno or "")

            # Top line - Strain
            c.setFont("Helvetica-Bold", 14)
            # center top
            strain_y = label_h - 0.22 * inch
            c.drawCentredString(label_w / 2, strain_y, strain_text)

            # Line 2 - PlantNo (left)
            c.setFont("Helvetica", 16)
            left_x = 0.06 * inch
            plant_y = 0.12 * inch
            c.drawString(left_x, plant_y, plant_text)

            # QR code on right: place below the strain line and 0.25" from the right edge
            try:
                # Use createBarcodeDrawing which returns a Drawing we can reliably scale
                drawing = createBarcodeDrawing('QR', value=plant_text, barWidth=1, barHeight=1, humanReadable=False)
                # try to obtain intrinsic drawing size
                dw = getattr(drawing, 'width', None)
                dh = getattr(drawing, 'height', None)
                if not dw or not dh:
                    try:
                        b = drawing.getBounds()
                        dw = b[2] - b[0]
                        dh = b[3] - b[1]
                    except Exception:
                        dw = dh = 1.0
                desired = 0.5 * inch
                scale = desired / max(dw, dh)
                try:
                    drawing.scale(scale, scale)
                except Exception:
                    pass
                qr_x = label_w - (0.25 * inch) - desired
                qr_y = strain_y - desired - (0.02 * inch)
                renderPDF.draw(drawing, c, qr_x, qr_y)
            except Exception:
                # fallback: do nothing (plantno still printed)
                pass

            c.showPage()

        c.save()

        command = "{} {}".format('c:\\labels\\PDFtoPrinter.exe','C:\\labels\\label.pdf')
        subprocess.call(command,shell=False)

        self.set_status(f"Printed {len(rows)} tags")


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = PrintPlantTagsApp()
    app.mainloop()
    restart_menu()

