import customtkinter as ctk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import SubScale
import SubReadQRCode
import SubSupa
import os
import sys
import subprocess

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

# Simple harvest weigh UI. Reads scale weight (read-only) and QR plant id.
# Places a log entry and updates scaleplants table wet/dry weights.

APP_TITLE = "Weigh Harvest"
DEFAULT_FONT = ("Arial", 15)


class WeighHarvestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("760x560")

        # Layout
        container = ctk.CTkFrame(self, corner_radius=8)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = ctk.CTkLabel(container, text="Harvest Weigh", font=("Arial", 20, "bold"))
        header.grid(row=0, column=0, columnspan=3, pady=(0, 12))
        
        # QR Reader status indicator
        self.QrStatusLabel = ctk.CTkLabel(container, text="QR: Checking...", font=("Arial", 12), 
                                          text_color="#ff8800", corner_radius=6, 
                                          fg_color="#2b2b2b", padx=10, pady=5)
        self.QrStatusLabel.grid(row=0, column=3, sticky="e", pady=(0, 12))

        # Type combo (Wet / Dry)
        ctk.CTkLabel(container, text="Plant Type", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.TypeCombo = ctk.CTkComboBox(container, values=["Wet", "Dry"], width=160, font=DEFAULT_FONT)
        self.TypeCombo.set("Wet")
        self.TypeCombo.grid(row=1, column=1, sticky="w", pady=8)

        # Plant No entry (populated from QR or typed and Enter)
        ctk.CTkLabel(container, text="Plant ID", font=DEFAULT_FONT).grid(row=1, column=2, sticky="e", padx=(6,6))
        self.PlantEntry = ctk.CTkEntry(container, width=160, font=DEFAULT_FONT)
        self.PlantEntry.grid(row=1, column=3, sticky="w", pady=8)
        # Bind Enter key to process plant
        self.PlantEntry.bind('<Return>', lambda e: self.OnPlantEnter())

        # Weight display (read-only)
        ctk.CTkLabel(container, text="Weight (g)", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6))
        self.WeightEntry = ctk.CTkEntry(container, width=160, font=DEFAULT_FONT, state="disabled")
        self.WeightEntry.grid(row=2, column=1, sticky="w", pady=8)

        # Buttons row
        button_row = ctk.CTkFrame(container, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(6,0))
        
        self.BtnProcess = ctk.CTkButton(button_row, text="Process Current Plant", font=DEFAULT_FONT, command=self.ProcessCurrent)
        self.BtnProcess.pack(side="left", padx=(0,8))

        self.BtnClearLog = ctk.CTkButton(button_row, text="Clear Log", font=DEFAULT_FONT, command=self.ClearLog)
        self.BtnClearLog.pack(side="left", padx=(0,8))
        
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self.OnClose).pack(side="left", padx=(0,8))

        # Scrolled text for weigh log
        log_frame = ttk.Frame(container)
        log_frame.grid(row=4, column=0, columnspan=4, pady=(12,0), sticky="nsew")
        container.grid_rowconfigure(4, weight=1)
        container.grid_columnconfigure(2, weight=1)

        self.LogBox = ScrolledText(log_frame, wrap="none", height=18, font=("Courier New", 15, "bold"),
                                   bg="#2b2b2b", fg="#dce4ee", insertbackground="#dce4ee")
        self.LogBox.pack(fill="both", expand=True)

        # Status label
        self.StatusLabel = ctk.CTkLabel(container, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=5, column=0, columnspan=4, sticky="w", pady=(6,0))

        # Polling state
        self._PollId = None
        self._QrPollId = None
        self._PrevWeight = None
        self._QrStatusCheckCounter = 0  # Counter for periodic QR status checks

        # Check QR reader status initially
        self.CheckQrStatus()

        # Start polling scale and QR
        self.StartPolling()

        # Ensure stop on close
        try:
            self.protocol("WM_DELETE_WINDOW", self.OnClose)
        except Exception:
            pass

    # ---- QR Reader Status ----
    def CheckQrStatus(self):
        """Check if QR reader is connected and update status label."""
        try:
            # Check if QrReader exists in SubReadQRCode module
            if hasattr(SubReadQRCode, 'QrReader') and SubReadQRCode.QrReader:
                self.QrStatusLabel.configure(text="QR: Connected", text_color="#00aa00")
            else:
                self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
        except Exception:
            self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")

    # ---- Polling ----
    def StartPolling(self, interval_ms: int = 500):
        self.PollWeight(interval_ms)
        self.PollQr(interval_ms)

    def PollWeight(self, interval_ms: int):
        wstr = '0'
        wstr = SubScale.GetWeight()

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
            self._PollId = self.after(interval_ms, lambda: self.PollWeight(interval_ms))
        except Exception:
            self._PollId = None

    def PollQr(self, interval_ms: int):
        try:
            # SubReadQRCode.CheckQr should return a PlantNo or None/empty
            val = SubReadQRCode.CheckQr()

            # Normalize QR return value: it may be a string or tuple/list.
            plantno = None
            if val is None:
                plantno = None
            else:
                sval = str(val).strip()
                if sval.lower() not in ('none', ''):
                    plantno = sval

            if plantno:
                # populate and process
                try:
                    self.PlantEntry.delete(0, 'end')
                    self.PlantEntry.insert(0, str(plantno))
                except Exception:
                    pass
                # automatically process when QR scanned
                self.ProcessCurrent()
        except Exception:
            pass
        
        # Periodically check QR reader status (every 20 polls = ~10 seconds at 500ms intervals)
        self._QrStatusCheckCounter = getattr(self, '_QrStatusCheckCounter', 0) + 1
        if self._QrStatusCheckCounter >= 20:
            self._QrStatusCheckCounter = 0
            self.CheckQrStatus()
        
        try:
            self._QrPollId = self.after(interval_ms, lambda: self.PollQr(interval_ms))
        except Exception:
            self._QrPollId = None

    def StopPolling(self):
        try:
            if self._PollId:
                self.after_cancel(self._PollId)
                self._PollId = None
        except Exception:
            pass
        try:
            if self._QrPollId:
                self.after_cancel(self._QrPollId)
                self._QrPollId = None
        except Exception:
            pass

    def OnClose(self):
        self.StopPolling()
        try:
            self.destroy()
        except Exception:
            pass

    # ---- Actions ----
    def OnPlantEnter(self):
        # user pressed Enter in plant box
        self.ProcessCurrent()

    def ProcessCurrent(self):
        plantno = (self.PlantEntry.get() or "").strip()
        weight_s = (self.WeightEntry.get() or "").strip()
        plant_type = (self.TypeCombo.get() or "").strip().lower()

        if not plantno:
            self.SetStatus("No Plant ID available", kind='warning')
            return
        try:
            weight = float(weight_s)
        except Exception:
            self.SetStatus("Invalid or missing weight", kind='warning')
            return
        if weight <= 0:
            self.SetStatus("Weight must be > 0", kind='warning')
            return

        # fetch plant record
        try:
            rec = SubSupa.GetOnePlant(plantno)
        except Exception as e:
            self.SetStatus(f"DB lookup failed: {e}", kind='error')
            return

        strain = ""
        wet_existing = 0.0
        dry_existing = 0.0
        if rec:
            # GetOnePlant returns list of rows (or single row); handle both
            row = rec[0] if isinstance(rec, (list, tuple)) and len(rec) else rec
            strain = (row.get('Strain') or "")
            wet_existing = float(row.get('WetWeight') or 0.0)
            dry_existing = float(row.get('DryWeight') or 0.0)

        # Duplicate check
        if plant_type == 'wet' and wet_existing > 0:
            resp = messagebox.askyesno("Duplicate", f"Wet weight already recorded ({wet_existing} g). Continue and overwrite?")
            if not resp:
                self.SetStatus("Operation cancelled by user", kind='info')
                return
        if plant_type == 'dry' and dry_existing > 0:
            resp = messagebox.askyesno("Duplicate", f"Dry weight already recorded ({dry_existing} g). Continue and overwrite?")
            if not resp:
                self.SetStatus("Operation cancelled by user", kind='info')
                return

        # Update DB
        try:
            if plant_type == 'dry':
                SubSupa.UpdateDryWeight(plantno, int(weight))
            else:
                SubSupa.UpdateWetWeight(plantno, int(weight))
        except Exception as e:
            self.SetStatus(f"DB update failed: {e}", kind='error')
            return

        # Insert scale log (SubSupa.InsertScaleLog signature: PlantNo, Strain, PlantType, Weight)
        try:
            SubSupa.InsertScaleLog(str(plantno), strain, plant_type.capitalize(), int(weight))
        except Exception as e:
            # Surface API errors to the status label for debugging
            try:
                self.SetStatus(f"Scale log failed: {e}", kind='error')
            except Exception:
                pass

        # Add to on-screen log and clear plant entry
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{ts} {strain} {plantno} {plant_type.capitalize()} {int(weight)} grams\n"
        try:
            self.LogBox.insert('end', log_line)
            self.LogBox.see('end')
        except Exception:
            pass

        self.PlantEntry.delete(0, 'end')
        self.SetStatus("Recorded", kind='info')

    def ClearLog(self):
        try:
            self.LogBox.delete('1.0', 'end')
        except Exception:
            pass

    def SetStatus(self, msg: str, kind: str = 'info'):
        color = "#00aa00"
        if kind == 'info':
            color = '#00aa00'
        elif kind == 'warning':
            color = '#ff8800'
        elif kind == 'error':
            color = '#ff4444'
        try:
            self.StatusLabel.configure(text=msg, text_color=color)
        except Exception:
            try:
                self.StatusLabel.configure(text=msg)
            except Exception:
                pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = WeighHarvestApp()
    app.mainloop()
    restart_menu()
