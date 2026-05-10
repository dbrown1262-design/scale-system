"""PrintTareTag - Print a tare tag for buckets

Workflow:
 - Select Ranger or Scout scale via radio buttons
 - Tare button zeroes the Ranger scale (Ranger only)
 - Weight display is polled every 500ms from the selected scale
 - Print Tare Tag prints a label with the current weight via SubPrintLabel
"""
import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # the "scale" folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import Common.SubScale as SubScale
import Common.SubPrintLabel as SubPrintLabel

SubScale.ConnectScales()
ScoutConnected, RangerConnected = SubScale.GetScaleStatus()

BASE_DIR = ROOT_DIR

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


APP_TITLE = "Print Tare Tag"
DEFAULT_FONT = ("Arial", 14)


class PrintTareTagApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_TITLE)
        self.geometry("480x340")

        # -- Menu bar --
        menu_bar = ctk.CTkFrame(self, height=32)
        menu_bar.pack(fill="x", side="top")

        self.ScaleStatusLabel = ctk.CTkLabel(
            menu_bar, text="Scale: Checking...", font=("Arial", 12),
            text_color="#ff8800", corner_radius=6,
            fg_color="#2b2b2b", padx=10, pady=5
        )
        self.ScaleStatusLabel.pack(side="right", padx=6, pady=4)

        # -- Main container --
        container = ctk.CTkFrame(self, corner_radius=12)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = ctk.CTkLabel(container, text="Print Tare Tag", font=("Arial", 18, "bold"))
        header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))

        # Scale selection
        ctk.CTkLabel(container, text="Scale:", font=DEFAULT_FONT).grid(
            row=1, column=0, sticky="e", padx=(0, 10))

        scale_frame = ctk.CTkFrame(container, fg_color="transparent")
        scale_frame.grid(row=1, column=1, columnspan=2, sticky="w", pady=6)

        self.ScaleVar = ctk.StringVar(value="Ranger")
        self.RadioRanger = ctk.CTkRadioButton(
            scale_frame, text="Ranger", variable=self.ScaleVar,
            value="Ranger", font=DEFAULT_FONT, command=self.OnScaleChanged
        )
        self.RadioRanger.pack(side="left", padx=(0, 20))

        self.RadioScout = ctk.CTkRadioButton(
            scale_frame, text="Scout", variable=self.ScaleVar,
            value="Scout", font=DEFAULT_FONT, command=self.OnScaleChanged
        )
        self.RadioScout.pack(side="left")

        # Weight display
        ctk.CTkLabel(container, text="Weight (g):", font=DEFAULT_FONT).grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=10)

        self.EntWeight = ctk.CTkEntry(container, width=160, font=("Arial", 18, "bold"),
                                      justify="right", state="disabled")
        self.EntWeight.grid(row=2, column=1, sticky="w", pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=3, pady=(14, 0), sticky="w")

        self.BtnTare = ctk.CTkButton(
            btn_frame, text="Tare Scale", width=130, font=DEFAULT_FONT,
            command=self.OnTare
        )
        self.BtnTare.pack(side="left", padx=(0, 10))

        self.BtnPrint = ctk.CTkButton(
            btn_frame, text="Print Tare Tag", width=150, font=DEFAULT_FONT,
            command=self.OnPrint
        )
        self.BtnPrint.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="Close", width=100, font=DEFAULT_FONT,
            command=self._on_close
        ).pack(side="left")

        # Status bar
        self.StatusLabel = ctk.CTkLabel(container, text="", font=("Arial", 12),
                                        text_color="#aaaaaa")
        self.StatusLabel.grid(row=4, column=0, columnspan=3, sticky="w", pady=(12, 0))

        # Internal state
        self.PrevWeight = None
        self.PrevRangerStatus = None
        self.PrevScoutStatus = None
        self.StatusCheckCounter = 0
        self.ScalePollId = None

        self._update_tare_button()
        self.StartScalePoll()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #

    def SetStatus(self, msg):
        self.StatusLabel.configure(text=msg)

    def OnScaleChanged(self):
        self._update_tare_button()
        self.SetStatus(f"Scale changed to {self.ScaleVar.get()}")

    def _update_tare_button(self):
        """Tare only supported on Ranger."""
        if self.ScaleVar.get() == "Ranger" and RangerConnected:
            self.BtnTare.configure(state="normal")
        else:
            self.BtnTare.configure(state="disabled")

    def OnTare(self):
        ok = SubScale.SetRangerTare()
        if ok:
            self.SetStatus("Ranger scale tared.")
        else:
            self.SetStatus("Tare failed - Ranger not connected.")

    def OnPrint(self):
        weight_str = self.EntWeight.get().strip()
        if not weight_str or weight_str == "0":
            messagebox.showwarning("No Weight", "Place the bucket on the scale first.")
            return
        try:
            SubPrintLabel.PrintOneLabel(weight_str)
            self.SetStatus(f"Printed tare tag: {weight_str} g")
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not print label:\n{e}")

    # ------------------------------------------------------------------ #
    # Scale polling
    # ------------------------------------------------------------------ #

    def StartScalePoll(self, IntervalMs: int = 500):
        try:
            if self.ScalePollId:
                self.after_cancel(self.ScalePollId)
        except Exception:
            pass
        self._poll_scale(IntervalMs)

    def _poll_scale(self, IntervalMs: int = 500):
        selected = self.ScaleVar.get()
        try:
            if selected == "Ranger" and RangerConnected:
                W = SubScale.GetRangerWeight()
                WStr = str(W) if W is not None else "0"
            elif selected == "Scout" and ScoutConnected:
                W = SubScale.GetScoutWeight()
                WStr = str(round(W)) if W is not None else "0"
            else:
                WStr = "0"
        except Exception:
            WStr = "0"

        if WStr != self.PrevWeight:
            self.PrevWeight = WStr
            try:
                self.EntWeight.configure(state="normal")
                self.EntWeight.delete(0, "end")
                self.EntWeight.insert(0, WStr)
                self.EntWeight.configure(state="disabled")
            except Exception:
                pass

        # Periodic status check (every ~5 polls)
        self.StatusCheckCounter += 1
        if self.StatusCheckCounter >= 5:
            self.StatusCheckCounter = 0
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
            if self.ScalePollId:
                self.after_cancel(self.ScalePollId)
                self.ScalePollId = None
        except Exception:
            pass

    def _on_close(self):
        self.StopScalePoll()
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = PrintTareTagApp()
    app.mainloop()
    restart_menu()
