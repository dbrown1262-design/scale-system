import customtkinter as ctk
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import tempfile
import os
import sys
import subprocess

from SubPrintLabels import PrintOneLabel
import SubSupa
import SubScale

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "Weigh Bucked Totes"
DEFAULT_FONT = ("Arial", 15)
POLL_INTERVAL_MS = 500


class WeighBuckedApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("680x320")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Crop selector
        ctk.CTkLabel(frame, text="Crop", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.CropCombo = ctk.CTkComboBox(frame, values=[], width=200, font=DEFAULT_FONT, command=self.onCropSelected)
        self.CropCombo.grid(row=0, column=1, sticky="w", pady=6)

        # Strain selector
        ctk.CTkLabel(frame, text="Strain", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], width=200, font=DEFAULT_FONT, command=self.onStrainSelected)
        self.StrainCombo.grid(row=1, column=1, sticky="w", pady=6)

        # Tote selector and new tote button
        ctk.CTkLabel(frame, text="Tote", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6))
        self.ToteCombo = ctk.CTkComboBox(frame, values=["Select"], width=200, font=DEFAULT_FONT)
        self.ToteCombo.grid(row=2, column=1, sticky="w", pady=6)

        self.BtnNewTote = ctk.CTkButton(frame, text="New Tote", font=DEFAULT_FONT, command=self.createNewTote)
        self.BtnNewTote.grid(row=2, column=2, sticky="w", padx=(8,0))

        # Weight display (read-only)
        ctk.CTkLabel(frame, text="Tote Weight (g)", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(6,6))
        self.WeightEntry = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT, state="disabled")
        self.WeightEntry.grid(row=3, column=1, sticky="w", pady=6)

        # Buttons row: Save, Print Label, and Close
        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(12,0))
        
        self.BtnSave = ctk.CTkButton(button_row, text="Save Tote Weight", font=DEFAULT_FONT, command=self.saveToteWeight)
        self.BtnSave.pack(side="left", padx=(0,8))

        self.BtnPrintLabel = ctk.CTkButton(button_row, text="Print Label", font=DEFAULT_FONT, command=self.printLabel)
        self.BtnPrintLabel.pack(side="left", padx=(0,8))
        
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self.onClose).pack(side="left", padx=(0,8))

        # Status
        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=5, column=0, columnspan=3, sticky="w", pady=(8,0))

        # Polling state
        self._PollId = None
        self._PrevWeight = None

        # Load crops
        self.loadCrops()

        # start polling
        self.startPolling()

        # ensure stop on close
        try:
            self.protocol("WM_DELETE_WINDOW", self.onClose)
        except Exception:
            pass

    def setStatus(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def loadCrops(self):
        try:
            crops = SubSupa.LoadCrops()
            if crops:
                self.CropCombo.configure(values=crops)
                self.CropCombo.set(crops[0])
                # also populate strains for initial selection
                self.onCropSelected()
            else:
                self.CropCombo.configure(values=["Select"])
                self.CropCombo.set("Select")
        except Exception as e:
            self.setStatus(f"LoadCrops failed: {e}")

    def onCropSelected(self, val=None):
        sel = (self.CropCombo.get() or "").strip()
        if not sel or sel.lower().startswith("select"):
            self.StrainCombo.configure(values=["Select"])
            self.StrainCombo.set("Select")
            self.ToteCombo.configure(values=["Select"])
            self.ToteCombo.set("Select")
            return
        token = sel.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.setStatus("Cannot parse Crop number")
                return
        # load strains for this crop
        try:
            strains = SubSupa.LoadStrains(crop_no)
            if strains:
                self.StrainCombo.configure(values=strains)
                self.StrainCombo.set(strains[0])
                # load totes for the first strain
                self.onStrainSelected()
            else:
                self.StrainCombo.configure(values=["Select"])
                self.StrainCombo.set("Select")
                self.ToteCombo.configure(values=["Select"])
                self.ToteCombo.set("Select")
        except Exception as e:
            self.setStatus(f"LoadStrains failed: {e}")

    def onStrainSelected(self, val=None):
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select") or not selStrain or selStrain.lower().startswith("select"):
            self.ToteCombo.configure(values=["Select"])
            self.ToteCombo.set("Select")
            return
        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.setStatus("Cannot parse Crop number")
                return
        try:
            totes = SubSupa.LoadTotes(crop_no, selStrain)
            if totes:
                self.ToteCombo.configure(values=totes)
                self.ToteCombo.set(totes[0])
            else:
                self.ToteCombo.configure(values=["Select"])
                self.ToteCombo.set("Select")
        except Exception as e:
            self.setStatus(f"LoadTotes failed: {e}")

    def createNewTote(self):
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not selStrain or selStrain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.setStatus("Cannot parse Crop number")
                return
        try:
            newTote = SubSupa.GetNewToteNo(crop_no, selStrain)
            res = SubSupa.InsertNewTote(crop_no, selStrain, newTote)
            self.setStatus(f"Inserted new tote {newTote}")
            # refresh tote list
            self.onStrainSelected()
            # set the tote combo to the new tote
            totes = self.ToteCombo.cget("values")
            if totes and str(newTote) in totes:
                self.ToteCombo.set(str(newTote))
        except Exception as e:
            self.setStatus(f"CreateNewTote failed: {e}")

    # ---- Polling ----
    def startPolling(self):
        self.pollWeight()

    def pollWeight(self):
        wstr = '0'
        try:
            if SubScale is not None:
                w = SubScale.GetWeight()
                wstr = str(w)
        except Exception:
            wstr = '0'

        if wstr != self._PrevWeight:
            self._PrevWeight = wstr
            try:
                self.WeightEntry.configure(state='normal')
                self.WeightEntry.delete(0, 'end')
                self.WeightEntry.insert(0, wstr)
                self.WeightEntry.configure(state='disabled')
            except Exception:
                pass

        try:
            self._PollId = self.after(POLL_INTERVAL_MS, lambda: self.pollWeight())
        except Exception:
            self._PollId = None

    def stopPolling(self):
        try:
            if self._PollId:
                self.after_cancel(self._PollId)
                self._PollId = None
        except Exception:
            pass

    def onClose(self):
        self.stopPolling()
        try:
            self.destroy()
        except Exception:
            pass

    def saveToteWeight(self):
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        selTote = (self.ToteCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not selStrain or selStrain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not selTote or selTote.lower().startswith("select"):
            messagebox.showwarning("Select Tote", "Please select a tote")
            return
        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.setStatus("Cannot parse Crop number")
                return

        try:
            existingWeight = SubSupa.GetOneTote(crop_no, selStrain, int(selTote))
        except Exception as e:
            self.setStatus(f"GetOneTote failed: {e}")
            return

        try:
            currentWeight = float((self.WeightEntry.get() or "0").strip())
        except Exception:
            self.setStatus("Invalid weight")
            return

        if existingWeight and float(existingWeight) > 0:
            resp = messagebox.askyesno("Tote already weighed", f"Tote has weight {existingWeight} g. Update this tote?")
            if not resp:
                self.setStatus("Update cancelled")
                return

        # proceed to update
        try:
            SubSupa.UpdateToteWeight(crop_no, selStrain, int(selTote), int(currentWeight))
            self.setStatus(f"Updated tote {selTote} weight to {int(currentWeight)} g")
        except Exception as e:
            self.setStatus(f"UpdateToteWeight failed: {e}")
        
        PrintOneLabel(selStrain, "Bucked Flower",selCrop, "Tote", selTote, int(currentWeight))
        

    def printLabel(self):
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        selTote = (self.ToteCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not selStrain or selStrain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not selTote or selTote.lower().startswith("select"):
            messagebox.showwarning("Select Tote", "Please select a tote")
            return
        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.setStatus("Cannot parse Crop number")
                return

        # retrieve weight (if any)
        try:
            weight = SubSupa.GetOneTote(crop_no, selStrain, int(selTote))
            weight_val = int(weight) if weight else 0
        except Exception as e:
            self.setStatus(f"GetOneTote failed: {e}")
            return

        PrintOneLabel(selStrain, "Bucked Flower",selCrop, "Tote", selTote, weight_val)

        # build 2" x 3" PDF label
        self.setStatus(f"Sent label to printer for tote {selTote}")

if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = WeighBuckedApp()
    app.mainloop()
    restart_menu()
