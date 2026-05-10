"""TrimBagSummary - Display bag summary for a crop/strain/type

Workflow:
 - Select CropNo, Strain, Type (Flower, Smalls, Trim)
 - When Type changes, load bag list via SubSupa.GetBagSummary
 - Display in treeview: Bag No, Weight (g), Est. Units
 - Total row at the bottom
"""
import customtkinter as ctk
from tkinter import ttk
import os
import sys
import subprocess

import SubSupa

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


APP_TITLE = "Trim Bag Summary"
DEFAULT_FONT = ("Arial", 14)


def calc_est_units(weight: float, trim_type: str) -> float:
    t = trim_type.lower()
    if t == "flower":
        return weight / 3.5
    elif t == "smalls":
        return weight / 1.1
    elif t == "trim":
        return weight * 0.04
    return 0.0


class TrimBagSummaryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_TITLE)
        self.geometry("800x560")

        # --- Treeview style ---
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Large.Treeview",
                        background="#2b2b2b",
                        foreground="#dce4ee",
                        fieldbackground="#2b2b2b",
                        font=("Arial", 14),
                        rowheight=30)
        style.configure("Large.Treeview.Heading",
                        background="#1f538d",
                        foreground="#ffffff",
                        font=("Arial", 14, "bold"))
        style.map("Large.Treeview",
                  background=[("selected", "#144870")])

        # --- Title ---
        ctk.CTkLabel(self, text="Trim Bag Summary", font=("Arial", 22, "bold")).pack(pady=(10, 6))

        # --- Filter row ---
        filter_row = ctk.CTkFrame(self)
        filter_row.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(filter_row, text="Crop:", font=DEFAULT_FONT).pack(side="left", padx=(6, 4))
        self.CmbCrop = ctk.CTkComboBox(filter_row, values=["Loading..."], width=220,
                                       font=DEFAULT_FONT, command=self.OnCropChanged)
        self.CmbCrop.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filter_row, text="Strain:", font=DEFAULT_FONT).pack(side="left", padx=(0, 4))
        self.CmbStrain = ctk.CTkComboBox(filter_row, values=["Select"], width=200,
                                         font=DEFAULT_FONT, command=self.OnStrainChanged)
        self.CmbStrain.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filter_row, text="Type:", font=DEFAULT_FONT).pack(side="left", padx=(0, 4))
        self.CmbType = ctk.CTkComboBox(filter_row, values=["Select", "Flower", "Smalls", "Trim"],
                                       width=140, font=DEFAULT_FONT, command=self.OnTypeChanged)
        self.CmbType.set("Select")
        self.CmbType.pack(side="left", padx=(0, 12))

        ctk.CTkButton(filter_row, text="Close", width=90, font=DEFAULT_FONT,
                      command=self._on_close).pack(side="right", padx=6)

        # --- Treeview ---
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        cols = ("Bag No", "Weight (g)", "Est. Units")
        self.Tree = ttk.Treeview(tree_frame, style="Large.Treeview",
                                  columns=cols, show="headings")
        self.Tree.heading("Bag No", text="Bag No")
        self.Tree.heading("Weight (g)", text="Weight (g)")
        self.Tree.heading("Est. Units", text="Est. Units")

        self.Tree.column("Bag No", width=280, anchor="w")
        self.Tree.column("Weight (g)", width=160, anchor="e")
        self.Tree.column("Est. Units", width=160, anchor="e")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=vsb.set)
        self.Tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # --- Status ---
        self.StatusLabel = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="#aaaaaa")
        self.StatusLabel.pack(pady=(0, 8))

        self._load_crops()

    # ------------------------------------------------------------------ #

    def SetStatus(self, msg):
        self.StatusLabel.configure(text=msg)

    def _load_crops(self):
        try:
            crops = SubSupa.LoadCrops() or ["Select"]
            self.CmbCrop.configure(values=crops)
            self.CmbCrop.set("Select")
        except Exception as e:
            self.SetStatus(f"LoadCrops failed: {e}")

    def OnCropChanged(self, value):
        sel = (value or "").strip()
        self.CmbStrain.configure(values=["Select"])
        self.CmbStrain.set("Select")
        self.CmbType.set("Select")
        self.Tree.delete(*self.Tree.get_children())
        if not sel or sel.lower().startswith("select"):
            return
        try:
            crop_no = int(sel.split("-")[0])
            strains = SubSupa.LoadStrains(crop_no) or ["Select"]
            self.CmbStrain.configure(values=strains)
            self.CmbStrain.set("Select")
        except Exception as e:
            self.SetStatus(f"LoadStrains failed: {e}")

    def OnStrainChanged(self, value):
        self.CmbType.set("Select")
        self.Tree.delete(*self.Tree.get_children())

    def OnTypeChanged(self, value):
        self._load_bags()

    def _load_bags(self):
        self.Tree.delete(*self.Tree.get_children())

        crop_display = (self.CmbCrop.get() or "").strip()
        strain = (self.CmbStrain.get() or "").strip()
        trim_type = (self.CmbType.get() or "").strip()

        if (not crop_display or crop_display.lower().startswith("select") or
                not strain or strain.lower().startswith("select") or
                not trim_type or trim_type.lower() == "select"):
            return

        try:
            crop_no = int(crop_display.split("-")[0])
        except Exception:
            self.SetStatus("Cannot parse Crop number")
            return

        try:
            rows = SubSupa.GetBagSummary(crop_no, strain, trim_type) or []
        except Exception as e:
            self.SetStatus(f"GetBagSummary failed: {e}")
            return

        total_weight = 0.0
        total_units = 0.0

        for row in rows:
            bag_no = row.get("MetrcId", "")
            weight = float(row.get("Weight") or 0)
            units = calc_est_units(weight, trim_type)
            total_weight += weight
            total_units += units
            self.Tree.insert("", "end", values=(bag_no, f"{weight:,.0f}", f"{units:,.1f}"))

        # Total row
        if rows:
            self.Tree.insert("", "end", values=("TOTAL", f"{total_weight:,.0f}", f"{total_units:,.1f}"),
                             tags=("total",))
            self.Tree.tag_configure("total", background="#1f538d", foreground="#ffffff")

        self.SetStatus(f"{len(rows)} bag(s)  |  Total weight: {total_weight:,.0f} g  |  Est. units: {total_units:,.1f}")

    def _on_close(self):
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = TrimBagSummaryApp()
    app.mainloop()
    restart_menu()
