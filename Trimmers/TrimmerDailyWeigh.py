# main.py
# Weigh entry screen for daily trimmed flower
# Requires: pip install customtkinter
"""
Weigh entry screen for daily trimmed flower.
Requires: pip install customtkinter
#!/usr/bin/env python3

Trim weight entry UI (CTk) with read-only scale weight display.
User-defined identifiers use CamelCase per request.
"""

import sys
import math
import customtkinter as ctk
from pathlib import Path
# in-window status label will replace modal messagebox popups
from tkcalendar import DateEntry
from datetime import date, datetime, time, timedelta

# Import SubSupa (DB) and SubScale (physical scale). SubScale is optional.
import SubSupa
import os
import sys
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # this is the "scale" folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
import Common.SubScale as SubScale

# Connect to hardware after imports
# SubScale.ConnectScales()

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

def launch_sop():
    # TrimmerDailyWeigh.py is in scale/Trimmers/
    this_file = Path(__file__).resolve()
    scale_root = this_file.parents[1]  # .../scale
    sop_md = scale_root / "sop" / "Trimmers" / "TrimmerDailyWeigh.md"
    viewer_py = scale_root / "common" / "SopViewer.py"

    # Launch separate process (non-blocking)
    subprocess.Popen(
        [sys.executable, str(viewer_py), str(sop_md)],
        cwd=str(scale_root),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
    )

APP_TITLE = "Trim Weight Entry"
DEFAULT_FONT = ("Arial", 20)


def OnlyNumeric(NewValue: str) -> bool:
    """Validation callback: allow empty, integers, or decimal with one dot."""
    if NewValue == "":
        return True
    try:
        val = float(NewValue)
        if math.isnan(val) or math.isinf(val):
            return False
        if val < 0:
            return False
        return True
    except ValueError:
        return False


class WeighApp(ctk.CTk):
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
        
        # Scout scale status indicator
        self.ScaleStatusLabel = ctk.CTkLabel(menu_bar, text="Scale: Checking...", font=("Arial", 12), 
                                             text_color="#ff8800", corner_radius=6, 
                                             fg_color="#2b2b2b", padx=10, pady=5)
        self.ScaleStatusLabel.pack(side="right", padx=6, pady=4)
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("700x400")

        # Data caches / mappings
        self.CropDisplayToNo = {}

        # ---- Layout ----
        Container = ctk.CTkFrame(self, corner_radius=16)
        Container.pack(fill="both", expand=True, padx=16, pady=16)

        Header = ctk.CTkLabel(Container, text="Daily Trim Weigh", font=("Arial", 22, "bold"))
        Header.grid(row=0, column=0, columnspan=4, pady=(0, 18))

        # Trimmer
        ctk.CTkLabel(Container, text="Trimmer", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=8)
        self.CmbTrimmer = ctk.CTkComboBox(Container, values=["Loading..."], font=DEFAULT_FONT, width=260)
        self.CmbTrimmer.grid(row=1, column=1, sticky="w", pady=8)

        # Trim Date
        ctk.CTkLabel(Container, text="Trim Date", font=DEFAULT_FONT).grid(row=1, column=2, sticky="e", padx=(0, 10), pady=8)
        self.DateBox = DateEntry(Container, font=DEFAULT_FONT, width=12, year=date.today().year,
                                  background='#343638', foreground='#DCE4EE', 
                                  fieldbackground='#343638', borderwidth=2)
        self.DateBox.grid(row=1, column=3, sticky="w", pady=8)
        # Style the entry widget inside DateEntry
        try:
            self.DateBox.entry.configure(bg='#343638', fg='#DCE4EE', insertbackground='#DCE4EE')
        except Exception:
            pass

        # Crop No
        ctk.CTkLabel(Container, text="Crop No", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(0, 10), pady=8)
        self.CmbCrop = ctk.CTkComboBox(Container, values=["Loading..."], font=DEFAULT_FONT, width=260, command=self.OnCropChanged)
        self.CmbCrop.grid(row=2, column=1, sticky="w", pady=8)

        # Strain
        ctk.CTkLabel(Container, text="Strain", font=DEFAULT_FONT).grid(row=2, column=2, sticky="e", padx=(30, 10), pady=8)
        self.CmbStrain = ctk.CTkComboBox(Container, values=["Select"], font=DEFAULT_FONT, width=260)
        self.CmbStrain.grid(row=2, column=3, sticky="w", pady=8)

        # Type combo
        ctk.CTkLabel(Container, text="Type", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(0, 10), pady=8)
        self.CmbType = ctk.CTkComboBox(Container, values=["Select", "Flower", "Smalls"], font=DEFAULT_FONT, width=260)
        self.CmbType.grid(row=3, column=1, sticky="w", pady=8)

        # AM/PM combo
        ctk.CTkLabel(Container, text="AM/PM", font=DEFAULT_FONT).grid(row=3, column=2, sticky="e", padx=(0, 10), pady=8)
        self.CmbAmpm = ctk.CTkComboBox(Container, values=["Select", "Morning", "Afternoon"], font=DEFAULT_FONT, width=260, command=self.OnAmpmChanged)
        self.CmbAmpm.grid(row=3, column=3, sticky="w", pady=8)

        # Start Time / End Time (15-minute intervals 8:00 AM - 5:00 PM)
        self.TimeValues = self.GenerateTimeValues()

        ctk.CTkLabel(Container, text="Start Time", font=DEFAULT_FONT).grid(row=4, column=0, sticky="e", padx=(0, 10), pady=8)
        self.CmbStart = ctk.CTkComboBox(Container, values=["Select"] + self.TimeValues, font=DEFAULT_FONT, width=200)
        self.CmbStart.grid(row=4, column=1, sticky="w", pady=8)

        ctk.CTkLabel(Container, text="End Time", font=DEFAULT_FONT).grid(row=4, column=2, sticky="e", padx=(30, 10), pady=8)
        self.CmbEnd = ctk.CTkComboBox(Container, values=["Select"] + self.TimeValues, font=DEFAULT_FONT, width=200)
        self.CmbEnd.grid(row=4, column=3, sticky="w", pady=8)

        # Weight display (read-only, populated from scale)
        ctk.CTkLabel(Container, text="Weight (g)", font=DEFAULT_FONT).grid(row=5, column=2, sticky="e", padx=(30, 10), pady=8)
        self.EntGrams = ctk.CTkEntry(Container, font=DEFAULT_FONT, width=160, state="disabled")
        self.EntGrams.grid(row=5, column=3, sticky="w", pady=8)

        # Buttons
        BtnRow = ctk.CTkFrame(Container, fg_color="transparent")
        BtnRow.grid(row=6, column=0, columnspan=4, pady=(24, 0))

        self.BtnSave = ctk.CTkButton(BtnRow, text="Save Entry", font=("Arial", 15, "bold"), command=self.OnSave)
        self.BtnClear = ctk.CTkButton(BtnRow, text="Clear", command=self.OnClear)
        self.BtnRefresh = ctk.CTkButton(BtnRow, text="Refresh Lists", command=self.LoadStaticLists)
        self.BtnClose = ctk.CTkButton(BtnRow, text="Close", command=self._on_close)

        self.BtnSave.grid(row=0, column=0, padx=10)
        self.BtnClear.grid(row=0, column=1, padx=10)
        self.BtnRefresh.grid(row=0, column=2, padx=10)
        self.BtnClose.grid(row=0, column=3, padx=10)

        # make grid stretch a bit
        Container.grid_columnconfigure(1, weight=1)
        Container.grid_columnconfigure(3, weight=1)

        # In-window status label (replaces modal messageboxes)
        self.StatusLabel = ctk.CTkLabel(Container, text="", font=DEFAULT_FONT, text_color="#00aa00")
        self.StatusLabel.grid(row=7, column=0, columnspan=4, sticky="w", pady=(8, 0))

        # Initial data load
        self.LoadStaticLists()

        # Start polling the physical scale and update the weight display periodically
        self.PrevScaleWeight = None
        self.PrevScoutStatus = None
        self.ScalePollId = None
        self.StartScalePoll()

        # Ensure polling stops on window close
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def GenerateTimeValues(self) -> list:
        """Return list of formatted times from 8:00 AM to 5:00 PM every 15 minutes."""
        Start = datetime.combine(date.today(), time(hour=8, minute=0))
        End = datetime.combine(date.today(), time(hour=17, minute=0))
        Values = []
        Cur = Start
        while Cur <= End:
            Values.append(Cur.strftime("%I:%M %p"))
            Cur += timedelta(minutes=15)
        Normalized = [t.lstrip('0') if t.startswith('0') else t for t in Values]
        return Normalized

    # ---------- Data loading ----------
    def LoadStaticLists(self):
        """Populate Trimmer and Crop combos at startup or refresh."""
        Trimmers = SubSupa.LoadTrimmers() or []
        self.CmbTrimmer.configure(values=Trimmers)
        self.CmbTrimmer.set("Select")

        Crops = SubSupa.LoadCrops() or []
        self.CmbCrop.configure(values=Crops)
        self.CmbCrop.set("Select")

        # Reset strain list
        self.CmbStrain.configure(values=["Select"])
        self.CmbStrain.set("Select")
        # AM/PM default and time ranges
        try:
            self.CmbAmpm.set("Select")
            # ensure time lists reflect the AM/PM selection
            self.OnAmpmChanged("Select")
        except Exception:
            pass
        # Time combos
        try:
            self.CmbStart.configure(values=["Select"] + self.TimeValues)
            self.CmbEnd.configure(values=["Select"] + self.TimeValues)
        except Exception:
            pass
        try:
            self.CmbStart.set("Select")
            self.CmbEnd.set("Select")
        except Exception:
            pass

    def OnCropChanged(self, x):
        CropNo = int(x.strip().split('-')[0])
        print("crop no is", CropNo)
        if not CropNo:
            self.CmbStrain.configure(values=["Select"])
            self.CmbStrain.set("Select")
            return
        Strains = SubSupa.LoadStrains(CropNo)
        self.CmbStrain.configure(values=(Strains) if Strains else ["Select"])
        self.CmbStrain.set("Select")

    def OnAmpmChanged(self, value):
        """Adjust start/end combo values when AM/PM changes.

        Morning: 8:00 AM - 1:00 PM
        Afternoon: 12:00 PM - 5:00 PM
        Select: full 8:00 AM - 5:00 PM
        """
        Val = (value or "").strip()
        if Val == "Morning":
            StartS, EndS = "8:00 AM", "1:00 PM"
        elif Val == "Afternoon":
            StartS, EndS = "12:00 PM", "5:00 PM"
        else:
            StartS, EndS = "8:00 AM", "5:00 PM"

        try:
            St = datetime.strptime(StartS, "%I:%M %p")
            Et = datetime.strptime(EndS, "%I:%M %p")
        except Exception:
            Allowed = self.TimeValues
        else:
            Allowed = [t for t in self.TimeValues if St <= datetime.strptime(t, "%I:%M %p") <= Et]

        Vals = ["Select"] + Allowed
        try:
            self.CmbStart.configure(values=Vals)
            self.CmbEnd.configure(values=Vals)
            if self.CmbStart.get() not in Vals:
                self.CmbStart.set("Select")
            if self.CmbEnd.get() not in Vals:
                self.CmbEnd.set("Select")
        except Exception:
            pass

    # ---------- Actions ----------
    def OnClear(self):
        try:
            self.EntGrams.delete(0, "end")
        except Exception:
            pass
        self.CmbAmpm.set("Select")
        try:
            self.CmbStart.set("Select")
            self.CmbEnd.set("Select")
        except Exception:
            pass

    def OnSave(self):
        Trimmer = self.CmbTrimmer.get().strip()
        GramsS = self.EntGrams.get().strip()
        CropDisplay = self.CmbCrop.get().strip()
        Strain = self.CmbStrain.get().strip()
        TypeVal = self.CmbType.get().strip()
        TrimDate = self.DateBox.get_date()
        Ampm = self.CmbAmpm.get().strip()

        if Trimmer == "Select" or Trimmer == "":
            self.ShowStatus("Please choose a Trimmer.", kind="warning")
            return

        if GramsS == "":
            self.ShowStatus("Please enter Grams.", kind="warning")
            return

        try:
            Grams = float(GramsS)
            if Grams <= 0:
                raise ValueError
        except Exception:
            self.ShowStatus("Grams must be a positive number.", kind="warning")
            return

        if CropDisplay == "Select" or CropDisplay == "":
            self.ShowStatus("Please choose a Crop No.", kind="warning")
            return
        CropNo = int(CropDisplay.strip().split('-')[0])
        if not CropNo:
            self.ShowStatus("Please choose a Crop No.", kind="warning")
            return

        if Strain == "Select" or Strain == "":
            self.ShowStatus("Please choose a Strain.", kind="warning")
            return

        if Ampm == "Select" or Ampm == "":
            self.ShowStatus("Please choose Morning or Afternoon.", kind="warning")
            return

        # Start/End time validation
        StartTime = self.CmbStart.get().strip()
        EndTime = self.CmbEnd.get().strip()
        if StartTime == "Select" or StartTime == "":
            self.ShowStatus("Please choose a Start Time.", kind="warning")
            return
        if EndTime == "Select" or EndTime == "":
            self.ShowStatus("Please choose an End Time.", kind="warning")
            return

        # Ensure start <= end
        try:
            St = datetime.strptime(StartTime, "%I:%M %p")
            Et = datetime.strptime(EndTime, "%I:%M %p")
            if St > Et:
                self.ShowStatus("Start Time must be before or equal to End Time.", kind="warning")
                return
        except Exception:
            self.ShowStatus("Could not parse start/end times.", kind="warning")
            return

        try:
            SubSupa.SaveTrimmer(trimmer=Trimmer, grams=Grams, crop_no=CropNo, strain=Strain, trimtype=TypeVal, trimdate=TrimDate, ampm=Ampm, StartTime=StartTime, EndTime=EndTime)
        except Exception as e:
            self.ShowStatus(f"Could not save entry: {e}", kind="error")
            print({e})
            return
        self.ShowStatus("Trim weight recorded.", kind="info")
        self.OnClear()

    def ShowStatus(self, msg: str, kind: str = "info"):
        """Show a short, non-modal status message in the window.

        kind: 'info'|'warning'|'error' — selects color.
        """
        color = "#00aa00"  # green for dark theme
        if kind == "info":
            color = "#00aa00"  # green
        elif kind == "warning":
            color = "#ff8800"  # orange
        elif kind == "error":
            color = "#ff4444"  # red
        try:
            self.StatusLabel.configure(text=msg, text_color=color)
        except Exception:
            try:
                # fallback for older CTk versions
                self.StatusLabel.configure(text=msg)
            except Exception:
                pass

    # ---------- Scale polling ----------
    def StartScalePoll(self, IntervalMs: int = 500):
        """Begin periodic polling of the scale and update displayed weight."""
        # Cancel existing poll if any
        try:
            if getattr(self, 'ScalePollId', None):
                self.after_cancel(self.ScalePollId)
        except Exception:
            pass
        # Kick off polling
        self._poll_scale(IntervalMs)

    def _poll_scale(self, IntervalMs: int):
        """Single poll iteration; reschedules itself via after()."""
        WStr = '0'
        try:
            W = SubScale.GetScoutWeight()
            WStr = str(W)
        except Exception as e:
            # If reading fails, leave as '0'
            WStr = 'Error'
            print(f"Scale read failed: {e}")

        if WStr != getattr(self, 'PrevScaleWeight', None):
            self.PrevScaleWeight = WStr
            # Update the disabled entry safely
            try:
                self.EntGrams.configure(state='normal')
                self.EntGrams.delete(0, 'end')
                self.EntGrams.insert(0, WStr)
                self.EntGrams.configure(state='disabled')
            except Exception:
                pass
        
        # Check scale status and update if changed
        try:
            scout_connected, ranger_connected = SubScale.GetScaleStatus()
            if scout_connected != self.PrevScoutStatus:
                self.PrevScoutStatus = scout_connected
                if scout_connected:
                    self.ScaleStatusLabel.configure(text="Scale: Connected", text_color="#00aa00")
                else:
                    self.ScaleStatusLabel.configure(text="Scale: Not Found", text_color="#ff4444")
        except Exception:
            if self.PrevScoutStatus is not False:
                self.PrevScoutStatus = False
                self.ScaleStatusLabel.configure(text="Scale: Error", text_color="#ff4444")

        # schedule next poll
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
        # Stop polling then destroy
        try:
            self.StopScalePoll()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    app = WeighApp()
    app.mainloop()
    restart_menu()

