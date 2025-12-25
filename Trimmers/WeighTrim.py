"""WeighTrim - weigh trim bags for trimmers

Similar UI to TrimmerDailyWeigh but focused on weighing final trim bags.
Workflow:
 - Select CropNo (SubSupa.LoadCrops)
 - Select Strain (SubSupa.LoadStrains)
 - When Strain selected, load BagNo combo via SubSupa.LoadTrimBagNos
 - Weight display is populated from SubScale.GetWeight polled every 500ms
 - Save Weight validates selections and weight > 0 then calls SubSupa.InsertTrimBag
   (TrimDate passed as ISO datetime string).
"""
import math
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

import os
import sys
import subprocess
import SubSupa

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # this is the "scale" folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import Common.SubScale as SubScale
import Common.SubReadQRCode as SubReadQRCode

# Connect to hardware after imports (before GUI creation)
SubScale.ConnectScales()
SubReadQRCode.ConnectScanner()

ScoutConnected, RangerConnected = SubScale.GetScaleStatus()

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "Weigh Trim Bags"
DEFAULT_FONT = ("Arial", 14)


class WeighTrimApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("640x340")

        container = ctk.CTkFrame(self, corner_radius=12)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = ctk.CTkLabel(container, text="Weigh Trim Bags", font=("Arial", 18, "bold"))
        header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,12))

        ctk.CTkLabel(container, text="Crop", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(0,10))
        self.CmbCrop = ctk.CTkComboBox(container, values=["Loading..."], width=320, font=DEFAULT_FONT, command=self.OnCropChanged)
        self.CmbCrop.grid(row=1, column=1, columnspan=2, sticky="w", pady=6)

        ctk.CTkLabel(container, text="Strain", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(0,10))
        self.CmbStrain = ctk.CTkComboBox(container, values=["Select"], width=320, font=DEFAULT_FONT, command=self.OnStrainChanged)
        self.CmbStrain.grid(row=2, column=1, columnspan=2, sticky="w", pady=6)

        ctk.CTkLabel(container, text="Metric Tag", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(0,10))
        self.EntMetricTag = ctk.CTkEntry(container, width=260, font=DEFAULT_FONT)
        self.EntMetricTag.grid(row=3, column=1, sticky="w", pady=6)

        ctk.CTkLabel(container, text="Weight (g)", font=DEFAULT_FONT).grid(row=4, column=0, sticky="e", padx=(0,10))
        self.EntWeight = ctk.CTkEntry(container, width=160, font=DEFAULT_FONT, state="disabled")
        self.EntWeight.grid(row=4, column=1, sticky="w", pady=6)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=3, pady=(18,0))

        self.BtnSave = ctk.CTkButton(btn_frame, text="Save Weight", font=DEFAULT_FONT, command=self.OnSave)
        self.BtnClear = ctk.CTkButton(btn_frame, text="Clear", font=DEFAULT_FONT, command=self.OnClear)
        self.BtnRefresh = ctk.CTkButton(btn_frame, text="Refresh Lists", font=DEFAULT_FONT, command=self.LoadLists)
        self.BtnClose = ctk.CTkButton(btn_frame, text="Close", font=DEFAULT_FONT, command=self._on_close)

        self.BtnSave.grid(row=0, column=0, padx=8)
        self.BtnClear.grid(row=0, column=1, padx=8)
        self.BtnRefresh.grid(row=0, column=2, padx=8)
        self.BtnClose.grid(row=0, column=3, padx=8)

        self.StatusLabel = ctk.CTkLabel(container, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=7, column=0, columnspan=3, sticky="w", pady=(12,0))

        # initial load
        self.LoadLists()

        # scale poll
        self.PrevScaleWeight = None
        self.ScalePollId = None
        self.StartScalePoll()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def SetStatus(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def LoadLists(self):
        try:
            crops = SubSupa.LoadCrops() or []
            self.CmbCrop.configure(values=crops)
            self.CmbCrop.set("Select")
        except Exception as e:
            self.SetStatus(f"LoadCrops failed: {e}")
        try:
            self.CmbStrain.configure(values=["Select"])
            self.CmbStrain.set("Select")
            self.EntMetricTag.delete(0, 'end')
        except Exception:
            pass

    def OnCropChanged(self, value):
        try:
            sel = (value or "").strip()
            if not sel or sel.lower().startswith("select"):
                self.CmbStrain.configure(values=["Select"])
                self.CmbStrain.set("Select")
                return
            crop_no = int(sel.split('-')[0])
        except Exception:
            self.SetStatus("Cannot parse Crop number")
            return
        try:
            strains = SubSupa.LoadStrains(crop_no) or ["Select"]
            self.CmbStrain.configure(values=strains)
            self.CmbStrain.set("Select")
        except Exception as e:
            self.SetStatus(f"LoadStrains failed: {e}")

    def OnStrainChanged(self, value):
        try:
            strain = (value or "").strip()
            if not strain or strain.lower().startswith("select"):
                self.SetStatus("Please select a strain")
                return
            self.SetStatus(f"Selected {strain}. Scan metric tag or enter manually.")
        except Exception:
            self.SetStatus("Cannot parse strain")
            return

    def OnClear(self):
        try:
            self.CmbCrop.set("Select")
            self.CmbStrain.set("Select")
            self.EntMetricTag.delete(0, 'end')
            self.EntWeight.configure(state='normal')
            self.EntWeight.delete(0, 'end')
            self.EntWeight.configure(state='disabled')
            self.SetStatus("")
        except Exception:
            pass

    def OnSave(self):
        crop_display = (self.CmbCrop.get() or "").strip()
        strain = (self.CmbStrain.get() or "").strip()
        metric_tag = (self.EntMetricTag.get() or "").strip()
        wstr = (self.EntWeight.get() or "").strip()

        if not crop_display or crop_display.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not strain or strain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not metric_tag:
            messagebox.showwarning("Enter Metric Tag", "Please scan or enter a metric tag number")
            return
        try:
            weight = float(wstr)
            if weight <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Invalid Weight", "Weight must be a positive number")
            return

        try:
            crop_no = int(crop_display.split('-')[0])
        except Exception:
            self.SetStatus("Cannot parse Crop number")
            return

        # Check if tag exists in database
        try:
            check_result = SubSupa.CheckTrimBag(crop_no, strain, metric_tag)
            
            if check_result == "Error":
                messagebox.showerror("Tag Mismatch", f"Metric tag {metric_tag} belongs to a different strain/crop. Cannot use this tag.")
                return
            elif check_result == "InUse":
                resp = messagebox.askyesno("Tag In Use", f"Metric tag {metric_tag} already has data. Update weight to {weight} g?")
                if not resp:
                    self.SetStatus("Update cancelled")
                    return
                # Update existing bag
                try:
                    SubSupa.UpdateTrimBag(int(metric_tag), weight)
                    self.SetStatus(f"Updated tag {metric_tag} weight to {weight} g")
                except Exception as e:
                    self.SetStatus(f"UpdateTrimBag failed: {e}")
                    return
            else:  # "OkToAdd"
                # Insert new bag
                try:
                    SubSupa.InsertTrimBag(crop_no, strain, int(metric_tag), datetime.now().isoformat())
                    # Now update with weight
                    SubSupa.UpdateTrimBag(int(metric_tag), weight)
                    self.SetStatus(f"Saved tag {metric_tag} for {strain} ({weight} g)")
                except Exception as e:
                    self.SetStatus(f"InsertTrimBag failed: {e}")
                    return
        except Exception as e:
            self.SetStatus(f"CheckTrimBag failed: {e}")
            return

        # Clear metric tag for next bag
        self.EntMetricTag.delete(0, 'end')

    # ---------- Scale polling ----------
    def StartScalePoll(self, IntervalMs: int = 500):
        try:
            if getattr(self, 'ScalePollId', None):
                self.after_cancel(self.ScalePollId)
        except Exception:
            pass
        self._poll_scale(IntervalMs)

    def _poll_scale(self, IntervalMs: int = 500):
        WStr = '0'
        try:
            ScoutConnected, RangerConnected
            if RangerConnected:
                W = SubScale.GetRangerWeight()
                WStr = str(W)
            elif ScoutConnected:
                W = SubScale.GetScoutWeight()
                WStr = str(W)
        except Exception:
            WStr = '0'

        if WStr != getattr(self, 'PrevScaleWeight', None):
            self.PrevScaleWeight = WStr
            try:
                self.EntWeight.configure(state='normal')
                self.EntWeight.delete(0, 'end')
                self.EntWeight.insert(0, WStr)
                self.EntWeight.configure(state='disabled')
            except Exception:
                pass

        # Check QR reader for metric tag
        try:
            if hasattr(SubReadQRCode, 'QrReader'):
                qr_code = SubReadQRCode.CheckMetricQr()
                if qr_code and qr_code != "none":
                    # Update metric tag entry
                    self.EntMetricTag.delete(0, 'end')
                    self.EntMetricTag.insert(0, qr_code)
                    self.SetStatus(f"Scanned metric tag: {qr_code}")
        except Exception as e:
            # Silently ignore QR reader errors
            pass

        try:
            self.ScalePollId = self.after(IntervalMs, lambda: self._poll_scale(IntervalMs))
        except Exception:
            self.ScalePollId = None

    def StopScalePoll(self):
        try:
            if getattr(self, 'ScalePollId', None):
                self.after_cancel(self.ScalePollId)
                self.ScalePollId = None
        except Exception:
            pass

    def _on_close(self):
        try:
            self.StopScalePoll()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = WeighTrimApp()
    app.mainloop()
    restart_menu()