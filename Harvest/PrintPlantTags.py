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
        self.geometry("520x250")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Crop", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.CropCombo = ctk.CTkComboBox(frame, values=[], width=280, font=DEFAULT_FONT, command=self.on_crop_selected)
        self.CropCombo.grid(row=0, column=1, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Strain", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], width=280, font=DEFAULT_FONT, command=self.on_strain_selected)
        self.StrainCombo.grid(row=1, column=1, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Number of Labels", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6))
        self.LabelCountEntry = ctk.CTkEntry(frame, width=280, font=DEFAULT_FONT)
        self.LabelCountEntry.grid(row=2, column=1, sticky="w", pady=6)
        self.LabelCountEntry.insert(0, "0")

        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12,0))
        
        self.BtnPrint = ctk.CTkButton(button_row, text="Print Tags", font=DEFAULT_FONT, command=self.print_tags)
        self.BtnPrint.pack(side="left", padx=(0,8))
        
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self.destroy).pack(side="left", padx=(0,8))

        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8,0))

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
            self.LabelCountEntry.delete(0, "end")
            self.LabelCountEntry.insert(0, "0")
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
                # Trigger strain selection to update count
                self.on_strain_selected()
            else:
                self.StrainCombo.configure(values=["Select"])
                self.StrainCombo.set("Select")
                self.LabelCountEntry.delete(0, "end")
                self.LabelCountEntry.insert(0, "0")
        except Exception as e:
            self.set_status(f"LoadStrains failed: {e}")

    def on_strain_selected(self, val=None):
        """Query plant count when strain is selected"""
        sel_crop = (self.CropCombo.get() or "").strip()
        sel_strain = (self.StrainCombo.get() or "").strip()
        
        if not sel_crop or sel_crop.lower().startswith("select"):
            self.LabelCountEntry.delete(0, "end")
            self.LabelCountEntry.insert(0, "0")
            return
        
        if not sel_strain or sel_strain.lower().startswith("select"):
            self.LabelCountEntry.delete(0, "end")
            self.LabelCountEntry.insert(0, "0")
            return
        
        # Parse crop number
        token = sel_crop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status("Cannot parse Crop number")
                return
        
        # Query scaleplants table for count
        try:
            count = SubSupa.CountPlants(crop_no, sel_strain)
            
            self.LabelCountEntry.delete(0, "end")
            self.LabelCountEntry.insert(0, str(count))
            self.set_status(f"Found {count} plants for {sel_strain}")
        except Exception as e:
            self.set_status(f"Query failed: {e}")
            self.LabelCountEntry.delete(0, "end")
            self.LabelCountEntry.insert(0, "0")

    def print_tags(self):
        sel_crop = (self.CropCombo.get() or "").strip()
        sel_strain = (self.StrainCombo.get() or "").strip()
        if not sel_crop or sel_crop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not sel_strain or sel_strain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return

        # Get number of labels to print
        try:
            num_labels = int(self.LabelCountEntry.get())
            if num_labels <= 0:
                messagebox.showwarning("Invalid Count", "Please enter a valid number of labels")
                return
        except ValueError:
            messagebox.showwarning("Invalid Count", "Please enter a valid number")
            return

        # Label size
        label_w = 2.25 * inch
        label_h = 0.75 * inch

        c = canvas.Canvas("C:\\labels\\label.pdf", pagesize=(label_w, label_h))

        # Print the specified number of labels with just the strain name
        for i in range(num_labels):
            # Center the strain name vertically and horizontally
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(label_w / 2, label_h / 2, sel_strain)
            c.showPage()

        c.save()

        command = "{} {}".format('c:\\labels\\PDFtoPrinter.exe','C:\\labels\\label.pdf')
#        subprocess.call(command,shell=False)

        self.set_status(f"Printed {num_labels} labels for {sel_strain}")


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = PrintPlantTagsApp()
    app.mainloop()
    restart_menu()

