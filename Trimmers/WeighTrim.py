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
from pathlib import Path

import os
import sys
import subprocess
import SubSupa
import SubPrintLabels

Testing = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # this is the "scale" folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import Common.SubScale as SubScale
import Common.SubReadQRCode as SubReadQRCode

# Connect to hardware after imports (before GUI creation)
ScannerConnected = SubReadQRCode.ConnectScanner()
SubScale.ConnectScales()
ScoutConnected, RangerConnected = SubScale.GetScaleStatus()

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

def launch_sop():
    # WeighTrim.py is in scale/Trimmers/
    this_file = Path(__file__).resolve()
    scale_root = this_file.parents[1]  # .../scale
    sop_md = scale_root / "sop" / "Trimmers" / "WeighTrim.md"
    viewer_py = scale_root / "common" / "SopViewer.py"

    # Launch separate process (non-blocking)
    subprocess.Popen(
        [sys.executable, str(viewer_py), str(sop_md)],
        cwd=str(scale_root),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
    )

APP_TITLE = "Weigh Trim Bags"
DEFAULT_FONT = ("Arial", 14)


class WeighTrimApp(ctk.CTk):
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
        
        # QR scanner status indicator
        self.QrStatusLabel = ctk.CTkLabel(menu_bar, text="QR: Checking...", font=("Arial", 12), 
                                          text_color="#ff8800", corner_radius=6, 
                                          fg_color="#2b2b2b", padx=10, pady=5)
        self.QrStatusLabel.pack(side="right", padx=6, pady=4)
        
        # Scale status indicator
        self.ScaleStatusLabel = ctk.CTkLabel(menu_bar, text="Scale: Checking...", font=("Arial", 12), 
                                             text_color="#ff8800", corner_radius=6, 
                                             fg_color="#2b2b2b", padx=10, pady=5)
        self.ScaleStatusLabel.pack(side="right", padx=6, pady=4)
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("800x640")

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

        ctk.CTkLabel(container, text="Type", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(0,10))
        self.CmbType = ctk.CTkComboBox(container, values=["Select", "Flower", "Smalls", "Trim"], width=320, font=DEFAULT_FONT, command=self.OnTypeChanged)
        self.CmbType.grid(row=3, column=1, columnspan=2, sticky="w", pady=6)
        self.CmbType.set("Select")

        ctk.CTkLabel(container, text="Bag", font=DEFAULT_FONT).grid(row=4, column=0, sticky="e", padx=(0,10))
        self.CmbBag = ctk.CTkComboBox(container, values=["Select", "New"], width=320, font=DEFAULT_FONT, command=self.OnBagChanged)
        self.CmbBag.grid(row=4, column=1, columnspan=2, sticky="w", pady=6)
        self.CmbBag.set("Select")

        ctk.CTkLabel(container, text="Tare (g)", font=DEFAULT_FONT).grid(row=5, column=0, sticky="e", padx=(0,10))
        self.EntTare = ctk.CTkEntry(container, width=260, font=DEFAULT_FONT)
        self.EntTare.grid(row=5, column=1, sticky="w", pady=6)

        ctk.CTkLabel(container, text="Scale", font=DEFAULT_FONT).grid(row=6, column=0, sticky="e", padx=(0,10))
        scale_frame = ctk.CTkFrame(container, fg_color="transparent")
        scale_frame.grid(row=6, column=1, columnspan=2, sticky="w", pady=6)
        self.ScaleVar = ctk.StringVar(value="Ranger")
        self.RadioRanger = ctk.CTkRadioButton(scale_frame, text="Ranger", variable=self.ScaleVar,
                                              value="Ranger", font=DEFAULT_FONT, command=self.OnScaleChanged)
        self.RadioRanger.pack(side="left", padx=(0, 20))
        self.RadioScout = ctk.CTkRadioButton(scale_frame, text="Scout", variable=self.ScaleVar,
                                             value="Scout", font=DEFAULT_FONT, command=self.OnScaleChanged)
        self.RadioScout.pack(side="left")

        ctk.CTkLabel(container, text="Weight (g)", font=DEFAULT_FONT).grid(row=7, column=0, sticky="e", padx=(0,10))
        # Weight entry is editable if no scale connected, disabled if a scale is connected
        initial_weight_state = "disabled" if (RangerConnected or ScoutConnected) else "normal"
        self.EntWeight = ctk.CTkEntry(container, width=160, font=DEFAULT_FONT, state=initial_weight_state)
        self.EntWeight.grid(row=7, column=1, sticky="w", pady=6)

        ctk.CTkLabel(container, text="Net Weight (g)", font=DEFAULT_FONT).grid(row=8, column=0, sticky="e", padx=(0,10))
        self.NetWeightLabel = ctk.CTkLabel(container, text="--", font=("Arial", 16, "bold"), text_color="#44cc44")
        self.NetWeightLabel.grid(row=8, column=1, sticky="w", pady=6)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=9, column=0, columnspan=3, pady=(18,0))

        self.BtnSave = ctk.CTkButton(btn_frame, text="Save Weight", font=DEFAULT_FONT, command=self.OnSave)
        self.BtnPrintLabel = ctk.CTkButton(btn_frame, text="Print Label", font=DEFAULT_FONT, command=self.OnPrintLabel)
        self.BtnTare = ctk.CTkButton(btn_frame, text="Tare Scale", font=DEFAULT_FONT, command=self.OnTare)
        self.BtnClear = ctk.CTkButton(btn_frame, text="Clear", font=DEFAULT_FONT, command=self.OnClear)
        self.BtnRefresh = ctk.CTkButton(btn_frame, text="Refresh Lists", font=DEFAULT_FONT, command=self.LoadLists)
        self.BtnClose = ctk.CTkButton(btn_frame, text="Close", font=DEFAULT_FONT, command=self._on_close)

        self.BtnSave.grid(row=0, column=0, padx=8)
        self.BtnPrintLabel.grid(row=0, column=1, padx=8)
        self.BtnTare.grid(row=0, column=2, padx=8)
        self.BtnClear.grid(row=1, column=0, padx=8, pady=(8,0))
        self.BtnRefresh.grid(row=1, column=1, padx=8, pady=(8,0))
        self.BtnClose.grid(row=1, column=2, padx=8, pady=(8,0))

        self.StatusLabel = ctk.CTkLabel(container, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=10, column=0, columnspan=3, sticky="w", pady=(12,0))

        # initial load
        self.LoadLists()

        # scale poll
        self.PrevScaleWeight = None
        self.PrevRangerStatus = None
        self.PrevQrStatus = None
        self.StatusCheckCounter = 0
        self.ScalePollId = None
        self.StartScalePoll()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def OnScaleChanged(self):
        self.SetStatus(f"Scale changed to {self.ScaleVar.get()}")

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
            self.CmbBag.configure(values=["Select", "New"])
            self.CmbBag.set("Select")
            self.EntTare.delete(0, 'end')
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
            # Load bags when strain changes
            self.LoadBags()
        except Exception:
            self.SetStatus("Cannot parse strain")
            return

    def OnTypeChanged(self, value):
        """Load bags when type is changed."""
        try:
            self.LoadBags()
        except Exception as e:
            self.SetStatus(f"LoadBags failed: {e}")

    def LoadBags(self):
        """Load bags based on current crop, strain, and type selection."""
        try:
            crop_display = (self.CmbCrop.get() or "").strip()
            strain = (self.CmbStrain.get() or "").strip()
            trim_type = (self.CmbType.get() or "").strip()
            
            if not crop_display or crop_display.lower().startswith("select"):
                self.CmbBag.configure(values=["Select", "New"])
                self.CmbBag.set("Select")
                return
            if not strain or strain.lower().startswith("select"):
                self.CmbBag.configure(values=["Select", "New"])
                self.CmbBag.set("Select")
                return
                
            crop_no = int(crop_display.split('-')[0])
            bags = SubSupa.GetTrimBags(crop_no, strain, trim_type) or ["Select", "New"]
            self.CmbBag.configure(values=bags)
            self.CmbBag.set("Select")
        except Exception as e:
            self.SetStatus(f"LoadBags error: {e}")
            self.CmbBag.configure(values=["Select", "New"])
            self.CmbBag.set("Select")

    def OnBagChanged(self, value):
        """Enable/disable Save Weight button based on bag selection."""
        try:
            bag = (value or "").strip()
            if bag == "New":
                self.BtnSave.configure(state="normal")
                self.EntTare.delete(0, 'end')
                self.SetStatus("New bag selected - you can save weight")
            else:
                self.BtnSave.configure(state="disabled")
                # Clear the tare field 
                self.EntTare.delete(0, 'end')
                # Get and populate the weight for this bag
                try:
                    weight = SubSupa.GetBagWeight(bag)
                    self.EntWeight.configure(state='normal')
                    self.EntWeight.delete(0, 'end')
                    self.EntWeight.insert(0, str(weight))
                    if RangerConnected:
                        self.EntWeight.configure(state='disabled')
                except Exception as e:
                    self.SetStatus(f"Error loading bag weight: {e}")
                self.SetStatus(f"Existing bag {bag} - you can only print label")
        except Exception:
            pass

    def OnClear(self):
        try:
            self.CmbCrop.set("Select")
            self.CmbStrain.set("Select")
            self.CmbType.set("Flower")
            self.CmbBag.set("Select", "New")
            self.EntTare.delete(0, 'end')
            self.EntWeight.configure(state='normal')
            self.EntWeight.delete(0, 'end')
            self.EntWeight.configure(state='disabled')
            self.BtnSave.configure(state="normal")
            self.SetStatus("")
        except Exception:
            pass

    def OnTare(self):
        """Tare the Ranger scale to zero"""
        try:
            SubScale.SetRangerTare()
            self.SetStatus("Scale tared successfully")
        except Exception as e:
            self.SetStatus(f"Tare failed: {e}")
            messagebox.showerror("Tare Error", f"Failed to tare scale: {e}")

    def OnPrintLabel(self):
        crop_display = (self.CmbCrop.get() or "").strip()
        strain = (self.CmbStrain.get() or "").strip()
        label_type = (self.CmbType.get() or "").strip()
        bag_no = (self.EntTare.get() or "").strip()
        wstr = (self.EntWeight.get() or "").strip()

        if not crop_display or crop_display.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not strain or strain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not label_type:
            messagebox.showwarning("Select Type", "Please select a type")
            return
        if not bag_no:
            messagebox.showwarning("Tare Missing", "Please scan a tare tag")
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

        # Get harvest date from database
        try:
            harvest_date = SubSupa.GetHarvestDate(crop_no)
            if not harvest_date:
                messagebox.showwarning("No Harvest Date", "Cannot retrieve harvest date for this crop")
                return
        except Exception as e:
            self.SetStatus(f"GetHarvestDate failed: {e}")
            return

        # Print label
        try:
            SubPrintLabels.PrintOneLabel(strain, label_type, harvest_date, bag_no, int(weight))
            self.SetStatus(f"Label printed for {strain} - {label_type} ({weight} g)")
        except Exception as e:
            self.SetStatus(f"Print failed: {e}")

    def OnSave(self):
        crop_display = (self.CmbCrop.get() or "").strip()
        strain = (self.CmbStrain.get() or "").strip()
        trim_type = (self.CmbType.get() or "").strip()
        bag_no = (self.CmbBag.get() or "").strip()
        tare = (self.EntTare.get() or "").strip()
        wstr = (self.EntWeight.get() or "").strip()

        if Testing:
            wstr = "2500"
            tare = "200"    

        if not crop_display or crop_display.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not strain or strain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not trim_type:
            messagebox.showwarning("Select Type", "Please select a type")
            return
        if not bag_no or bag_no.lower().startswith("select"):
            messagebox.showwarning("Select Bag", "Please select a bag")
            return
        if not tare:
            messagebox.showwarning("Tare Missing", "Please scan a tare tag")
            return
        try:
            weight = float(wstr)
            if weight <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Invalid Weight", "Weight must be a positive number")
            return

        try:
            tare_val = float(tare)
        except Exception:
            messagebox.showwarning("Invalid Tare", "Tare value must be a number")
            return

        net_weight = weight - tare_val
        if net_weight <= 0:
            messagebox.showwarning("Invalid Weight", f"Net weight ({net_weight:.0f} g) must be positive after subtracting tare ({tare_val:.0f} g)")
            return

        try:
            crop_no = int(crop_display.split('-')[0])
        except Exception:
            self.SetStatus("Cannot parse Crop number")
            return

        # If bag_no is "New", generate a new bag number
        if bag_no.lower() == "new":
            try:
                new_num = SubSupa.GetNewBagNo(crop_no, strain)
                bag_no = f"{new_num}"
                print(f"Generated new bag number: {bag_no}")
            except Exception as e:
                self.SetStatus(f"GetNewBagNo failed: {e}")
                return
        try:
            check_result = SubSupa.CheckTrimBag(crop_no, strain, bag_no)
            
            if check_result == "Error":
                messagebox.showerror("Tag Mismatch", f"Bag {bag_no} belongs to a different strain/crop. Cannot use this tag.")
                return
            elif check_result == "InUse":
                resp = messagebox.askyesno("Tag In Use", f"Bag {bag_no} already has data. Update weight to {net_weight:.0f} g?")
                if not resp:
                    self.SetStatus("Update cancelled")
                    return
                # Update existing bag using new signature
                try:
                    SubSupa.UpdateTrimBag(bag_no, net_weight)
                    self.SetStatus(f"Updated bag {bag_no} weight to {net_weight:.0f} g")
                except Exception as e:
                    self.SetStatus(f"Update failed: {e}")
                    return
            else:  # "OkToAdd"
                # Insert new bag with new signature
                try:
                    SubSupa.InsertTrimBag(crop_no, strain, trim_type, bag_no, net_weight, datetime.now().isoformat())
                    self.SetStatus(f"Saved bag {bag_no} for {strain} ({net_weight:.0f} g)")
                except Exception as e:
                    self.SetStatus(f"InsertTrimBag failed: {e}")
                    return
        except Exception as e:
            self.SetStatus(f"CheckTrimBag failed: {e}")
            return

        # Print label
        harvest_date = SubSupa.GetHarvestDate(crop_no)
        try:
            SubPrintLabels.PrintOneLabel(strain, trim_type, harvest_date, bag_no, net_weight)
            self.SetStatus(f"Label printed for {strain} - {trim_type} ({net_weight:.0f} g)")
        except Exception as e:
            self.SetStatus(f"Print failed: {e}")

        # Clear metric tag for next bag
        self.EntTare.delete(0, 'end')

    # ---------- Scale polling ----------
    def StartScalePoll(self, IntervalMs: int = 500):
        try:
            if getattr(self, 'ScalePollId', None):
                self.after_cancel(self.ScalePollId)
        except Exception:
            pass
        self._poll_scale(IntervalMs)

    def _poll_scale(self, IntervalMs: int = 500):
        selected = self.ScaleVar.get()
        try:
            if selected == "Ranger" and RangerConnected:
                W = SubScale.GetRangerWeight()
                WStr = str(W) if W is not None else '0'
            elif selected == "Scout" and ScoutConnected:
                W = SubScale.GetScoutWeight()
                WStr = str(round(W)) if W is not None else '0'
            else:
                WStr = '0'
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

        # Update net weight display
        try:
            tare_val = float(self.EntTare.get() or 0)
            scale_val = float(WStr or 0)
            net = scale_val - tare_val
            self.NetWeightLabel.configure(text=f"{net:,.0f}")
        except Exception:
            self.NetWeightLabel.configure(text="--")

        # Check QR reader for tare tag (only if scanner is connected)
        if ScannerConnected:
            try:
                if hasattr(SubReadQRCode, 'QrReader'):
                    qr_code = SubReadQRCode.CheckMetricQr()
                    if qr_code and qr_code != "none":
                        if qr_code.lower().startswith("tare "):
                            tare_weight = qr_code[5:].strip()
                            self.EntTare.delete(0, 'end')
                            self.EntTare.insert(0, tare_weight)
                            self.SetStatus(f"Tare scanned: {tare_weight} g")
                        else:
                            self.SetStatus(f"Invalid QR code (expected Tare tag): {qr_code}")

            except Exception as e:
                # Silently ignore QR reader errors
                pass
        
        # Periodically check QR and scale status (every 20 polls = ~10 seconds)
        self.StatusCheckCounter += 1
        self.interval = 5
        if self.StatusCheckCounter >= self.interval:
            self.StatusCheckCounter = 0
            
            # Check QR scanner status
            try:
                qr_available = ScannerConnected and hasattr(SubReadQRCode, 'QrReader') and SubReadQRCode.QrReader is not None
                if qr_available != self.PrevQrStatus:
                    self.PrevQrStatus = qr_available
                    if qr_available:
                        self.QrStatusLabel.configure(text="QR: Connected", text_color="#00aa00")
                    else:
                        self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
            except Exception:
                if self.PrevQrStatus is not False:
                    self.PrevQrStatus = False
                    self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
            
            # Check scale status
            try:
                scout_ok, ranger_ok = SubScale.GetScaleStatus()
                parts = []
                if ranger_ok:
                    parts.append("Ranger")
                if scout_ok:
                    parts.append("Scout")
                text = "Scale: " + ", ".join(parts) if parts else "Scale: Not Found"
                color = "#00aa00" if parts else "#ff4444"
                self.ScaleStatusLabel.configure(text=text, text_color=color)
            except Exception:
                self.ScaleStatusLabel.configure(text="Scale: Error", text_color="#ff4444")

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