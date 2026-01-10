import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import tempfile
import os
import sys
import subprocess

from SubPrintLabels import PrintOneLabel
import SubSupa

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # this is the "scale" folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
import Common.SubScale as SubScale
import Common.SubReadQRCode as SubReadQRCode

SubReadQRCode.ConnectScanner()

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "Weigh Bucked Totes"
DEFAULT_FONT = ("Arial", 15)
POLL_INTERVAL_MS = 500

def launch_sop():
    # WeighBucked.py is in scale/Harvest/
    this_file = Path(__file__).resolve()
    scale_root = this_file.parents[1]  # .../scale
    sop_md = scale_root / "sop" / "Harvest" / "WeighBucked.md"
    viewer_py = scale_root / "common" / "SopViewer.py"

    # Launch separate process (non-blocking)
    subprocess.Popen(
        [sys.executable, str(viewer_py), str(sop_md)],
        cwd=str(scale_root),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
    )


class WeighBuckedApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        menu_bar = ctk.CTkFrame(self, height=32)
        menu_bar.pack(fill="x", side="top")

        help_btn = ctk.CTkButton(
            menu_bar,
            text="Help",
            width=60,
            fg_color="transparent",
            text_color="white",
            hover_color="#333333",
            command=launch_sop
        )
        help_btn.pack(side="left", padx=6, pady=4)
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("680x320")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Header row with status indicators
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        
        # QR Reader status indicator
        self.QrStatusLabel = ctk.CTkLabel(header_frame, text="QR: Checking...", font=("Arial", 12), 
                                          text_color="#ff8800", corner_radius=6, 
                                          fg_color="#2b2b2b", padx=10, pady=5)
        self.QrStatusLabel.pack(side="right", padx=(8, 0))
        
        # Scale status indicator
        self.ScaleStatusLabel = ctk.CTkLabel(header_frame, text="Scale: Checking...", font=("Arial", 12), 
                                             text_color="#ff8800", corner_radius=6, 
                                             fg_color="#2b2b2b", padx=10, pady=5)
        self.ScaleStatusLabel.pack(side="right", padx=(0, 0))

        # Crop selector
        ctk.CTkLabel(frame, text="Crop", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.CropCombo = ctk.CTkComboBox(frame, values=[], width=200, font=DEFAULT_FONT, command=self.onCropSelected)
        self.CropCombo.grid(row=1, column=1, sticky="w", pady=6)

        # Strain selector
        ctk.CTkLabel(frame, text="Strain", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6))
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], width=200, font=DEFAULT_FONT, command=self.onStrainSelected)
        self.StrainCombo.grid(row=2, column=1, sticky="w", pady=6)

        # Metric Tag Number entry box (populated from QR reader)
        ctk.CTkLabel(frame, text="Metric Tag", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(6,6))
        self.MetricTagEntry = ctk.CTkEntry(frame, width=220, font=DEFAULT_FONT)
        self.MetricTagEntry.grid(row=3, column=1, sticky="w", pady=6)

        # Weight display (read-only)
        ctk.CTkLabel(frame, text="Tote Weight (g)", font=DEFAULT_FONT).grid(row=4, column=0, sticky="e", padx=(6,6))
        self.WeightEntry = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT, state="disabled")
        self.WeightEntry.grid(row=4, column=1, sticky="w", pady=6)

        # Buttons row: Save, Print Label, and Close
        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(12,0))
        
        self.BtnSave = ctk.CTkButton(button_row, text="Save Tote Weight", font=DEFAULT_FONT, command=self.saveToteWeight)
        self.BtnSave.pack(side="left", padx=(0,8))

        self.BtnPrintLabel = ctk.CTkButton(button_row, text="Print Label", font=DEFAULT_FONT, command=self.printLabel)
        self.BtnPrintLabel.pack(side="left", padx=(0,8))
        
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self.onClose).pack(side="left", padx=(0,8))

        # Status
        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=6, column=0, columnspan=3, sticky="w", pady=(8,0))

        # Polling state
        self._PollId = None
        self._PrevWeight = None
        self._PrevRangerStatus = None
        self._QrStatusCheckCounter = 0  # Counter for periodic QR status checks

        # Check QR reader status initially
        self.checkQrStatus()

        # Load crops
        self.loadCrops()

        # start polling
        self.startPolling()

        # ensure stop on close
        try:
            self.protocol("WM_DELETE_WINDOW", self.onClose)
        except Exception:
            pass

    # ---- QR Reader Status ----
    def checkQrStatus(self):
        """Check if QR reader is connected and update status label."""
        try:
            # Check if QrReader exists in SubReadQRCode module
            if hasattr(SubReadQRCode, 'QrReader') and SubReadQRCode.QrReader:
                self.QrStatusLabel.configure(text="QR: Connected", text_color="#00aa00")
            else:
                self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
        except Exception:
            self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")

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
                # trigger strain selection
                self.onStrainSelected()
            else:
                self.StrainCombo.configure(values=["Select"])
                self.StrainCombo.set("Select")
        except Exception as e:
            self.setStatus(f"LoadStrains failed: {e}")

    def onStrainSelected(self, val=None):
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select") or not selStrain or selStrain.lower().startswith("select"):
            return
        # Strain selected, ready for metric tag scanning
        self.setStatus(f"Selected {selStrain}. Scan metric tag or enter manually.")

    # ---- Polling ----
    def startPolling(self):
        self.pollWeight()

    def pollWeight(self):
        wstr = '0'
        try:
            if SubScale is not None:
                w = SubScale.GetRangerWeight()
                wstr = str(w)
            else:
                wstr = 'Error'
        except Exception:
            wstr = 'Error'

        if wstr != self._PrevWeight:
            self._PrevWeight = wstr
            try:
                self.WeightEntry.configure(state='normal')
                self.WeightEntry.delete(0, 'end')
                self.WeightEntry.insert(0, wstr)
                self.WeightEntry.configure(state='disabled')
            except Exception:
                pass
        
        # Check scale status and update if changed
        try:
            scout_connected, ranger_connected = SubScale.GetScaleStatus()
            if ranger_connected != self._PrevRangerStatus:
                self._PrevRangerStatus = ranger_connected
                if ranger_connected:
                    self.ScaleStatusLabel.configure(text="Scale: Connected", text_color="#00aa00")
                else:
                    self.ScaleStatusLabel.configure(text="Scale: Not Found", text_color="#ff4444")
        except Exception:
            if self._PrevRangerStatus is not False:
                self._PrevRangerStatus = False
                self.ScaleStatusLabel.configure(text="Scale: Error", text_color="#ff4444")

        # Check QR reader for metric tag
        try:
            if hasattr(SubReadQRCode, 'QrReader'):
                qr_code = SubReadQRCode.CheckMetricQr()
                if qr_code and qr_code != "none":
                    # Verify tag is valid before accepting
                    try:
                        tag_valid = SubSupa.CheckTag(qr_code)
                        if tag_valid:
                            # Update metric tag entry
                            self.MetricTagEntry.delete(0, 'end')
                            self.MetricTagEntry.insert(0, qr_code)
                            self.setStatus(f"Scanned metric tag: {qr_code}")
                        else:
                            self.setStatus(f"Invalid tag: {qr_code} - Not found in Metric tag list")
                    except Exception as e:
                        self.setStatus(f"CheckTag error: {e}")
        except Exception as e:
            self.setStatus(f"QR Reader error: {e}")
        
        # Periodically check QR reader status (every 20 polls = ~10 seconds at 500ms intervals)
        self._QrStatusCheckCounter = getattr(self, '_QrStatusCheckCounter', 0) + 1
        if self._QrStatusCheckCounter >= 20:
            self._QrStatusCheckCounter = 0
            self.checkQrStatus()

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
        metricTag = (self.MetricTagEntry.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not selStrain or selStrain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not metricTag:
            messagebox.showwarning("Enter Metric Tag", "Please scan or enter a metric tag number")
            return
        
        # Validate that tag exists in metrictags table
        try:
            if not SubSupa.CheckTag(metricTag):
                messagebox.showerror("Invalid Tag", f"Tag {metricTag} is not in the Metric tag list. Please verify the tag number.")
                return
        except Exception as e:
            self.setStatus(f"CheckTag failed: {e}")
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

        # Check if tag already has weight data
        try:
            existingWeight = SubSupa.GetOneTag(crop_no, selStrain, metricTag)
        except Exception as e:
            self.setStatus(f"GetOneTag failed: {e}")
            return

        try:
            currentWeight = float((self.WeightEntry.get() or "0").strip())
        except Exception:
            self.setStatus("Invalid weight")
            return

        if existingWeight and float(existingWeight) > 0:
            resp = messagebox.askyesno("Tag Already Weighed", f"Metric tag {metricTag} has weight {existingWeight} g. Replace this weight?")
            if not resp:
                self.setStatus("Update cancelled")
                return
            # Update existing weight
            try:
                SubSupa.UpdateTagWeight(crop_no, selStrain, metricTag, int(currentWeight))
                self.setStatus(f"Updated metric tag {metricTag} weight to {int(currentWeight)} g")
            except Exception as e:
                self.setStatus(f"UpdateTagWeight failed: {e}")
                return
        else:
            # Insert new tag weight
            try:
                SubSupa.InsertNewTag(crop_no, selStrain, metricTag, int(currentWeight))
                self.setStatus(f"Saved metric tag {metricTag} weight: {int(currentWeight)} g")
            except Exception as e:
                self.setStatus(f"InsertNewTag failed: {e}")
                return
        
        PrintOneLabel(selStrain, "Bucked Flower", selCrop, "Metric", metricTag, int(currentWeight))
        
        # Clear metric tag for next bag
        self.MetricTagEntry.delete(0, 'end')
        

    def printLabel(self):
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        metricTag = (self.MetricTagEntry.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not selStrain or selStrain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not metricTag:
            messagebox.showwarning("Enter Metric Tag", "Please scan or enter a metric tag number")
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
            weight = SubSupa.GetOneTag(crop_no, selStrain, metricTag)
            weight_val = int(weight) if weight else 0
        except Exception as e:
            self.setStatus(f"GetOneTag failed: {e}")
            return

        PrintOneLabel(selStrain, "Bucked Flower", selCrop, "Metric", metricTag, weight_val)

        self.setStatus(f"Sent label to printer for metric tag {metricTag}")

if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = WeighBuckedApp()
    app.mainloop()
    restart_menu()
