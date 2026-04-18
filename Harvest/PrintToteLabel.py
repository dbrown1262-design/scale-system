import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import SubSupa
import SubPrintLabels
import os
import sys
import subprocess

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "Print Tote Labels"
DEFAULT_FONT = ("Arial", 14)


class PrintToteLabelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        menu_bar = ctk.CTkFrame(self, height=32)
        menu_bar.pack(fill="x", side="top")

        ctk.CTkButton(
            menu_bar,
            text="Close",
            width=60,
            fg_color="transparent",
            text_color="white",
            hover_color="#333333",
            command=self.destroy
        ).pack(side="left", padx=6, pady=4)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.title(APP_TITLE)
        self.geometry("480x380")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Crop combo
        ctk.CTkLabel(frame, text="Crop", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6, 6))
        self.CropCombo = ctk.CTkComboBox(frame, values=[], width=300, font=DEFAULT_FONT, command=self.on_crop_selected)
        self.CropCombo.grid(row=0, column=1, sticky="w", pady=6)

        # Strain combo
        ctk.CTkLabel(frame, text="Strain", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6, 6))
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], width=300, font=DEFAULT_FONT)
        self.StrainCombo.grid(row=1, column=1, sticky="w", pady=6)

        # Label type combo
        ctk.CTkLabel(frame, text="Label Type", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6, 6))
        self.LabelTypeCombo = ctk.CTkComboBox(frame, values=["Flower", "Smalls", "Trim"], width=300, font=DEFAULT_FONT)
        self.LabelTypeCombo.set("Flower")
        self.LabelTypeCombo.grid(row=2, column=1, sticky="w", pady=6)

        # Number of labels
        ctk.CTkLabel(frame, text="# of Labels", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(6, 6))
        self.LabelCountEntry = ctk.CTkEntry(frame, width=300, font=DEFAULT_FONT)
        self.LabelCountEntry.insert(0, "1")
        self.LabelCountEntry.grid(row=3, column=1, sticky="w", pady=6)

        # Buttons
        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.BtnPrint = ctk.CTkButton(button_row, text="Print Labels", font=DEFAULT_FONT, command=self.print_labels)
        self.BtnPrint.pack(side="left", padx=(0, 8))

        # Status label
        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self._harvest_date = ""
        self.load_crops()

    def set_status(self, text: str, color: str = "#00aa00"):
        try:
            self.StatusLabel.configure(text=text, text_color=color)
        except Exception:
            pass

    def load_crops(self):
        try:
            crops = SubSupa.LoadCrops()
            self.CropCombo.configure(values=crops)
            self.CropCombo.set(crops[0])
        except Exception as e:
            self.set_status(f"LoadCrops failed: {e}", "#ff4444")

    def on_crop_selected(self, val=None):
        sel = (self.CropCombo.get() or "").strip()
        self.StrainCombo.configure(values=["Select"])
        self.StrainCombo.set("Select")
        self._harvest_date = ""

        if not sel or sel.lower().startswith("select"):
            return

        # Parse crop number and harvest date from "19 - 2025-11-15"
        parts = sel.split(" - ", 1)
        try:
            crop_no = int(parts[0].strip())
        except Exception:
            self.set_status("Cannot parse crop number", "#ff4444")
            return

        self._harvest_date = parts[1].strip() if len(parts) > 1 else ""

        try:
            strains = SubSupa.LoadStrains(crop_no)
            self.StrainCombo.configure(values=strains)
            self.StrainCombo.set(strains[0])
        except Exception as e:
            self.set_status(f"LoadStrains failed: {e}", "#ff4444")

    def print_labels(self):
        strain = (self.StrainCombo.get() or "").strip()
        label_type = (self.LabelTypeCombo.get() or "").strip()
        count_str = (self.LabelCountEntry.get() or "").strip()

        if not strain or strain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not label_type:
            messagebox.showwarning("Select Label Type", "Please select a label type")
            return
        try:
            count = int(count_str)
            if count < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Count", "Please enter a valid number of labels")
            return

        try:
            for _ in range(count):
                SubPrintLabels.PrintToteLabel(strain, label_type, self._harvest_date)
            self.set_status(f"Printed {count} label(s) for {strain} — {label_type}", "#00aa00")
        except Exception as e:
            self.set_status(f"Print failed: {e}", "#ff4444")
            messagebox.showerror("Print Error", str(e))


if __name__ == "__main__":
    app = PrintToteLabelApp()
    app.mainloop()
    restart_menu()
