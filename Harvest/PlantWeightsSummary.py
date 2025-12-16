import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
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

GRAMS_TO_LBS = 0.00220462262185
DEFAULT_FONT = ("Arial", 15)

class PlantWeightsSummary(ctk.CTk):
    """Summary of plant wet/dry weights per strain for a selected crop.

    For each strain show:
      Strain | WetWeight (lbs) | WetCount | DryWeight (lbs) | DryCount

    WetCount/DryCount are counts of rows with weight > 0.
    Totals row at the bottom.

    Uses SubSupa.LoadCrops() to populate the crop list (caller asked for GetCropNo; using LoadCrops as that exists).
    """

    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("Plant Weights Summary")
        self.geometry("1200x600")

        self.crop_no = None

        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=8)

        # Configure treeview style for dark theme
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="#dce4ee",
                       fieldbackground="#2b2b2b",
                       font=("Arial", 15),
                       rowheight=30)
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="#ffffff",
                       font=("Arial", 15, "bold"))
        style.map("Treeview",
                 background=[("selected", "#144870")])
        self.option_add("*TCombobox*Listbox.font", ("Arial", 15))
        self.option_add("*Big.TCombobox*Listbox.font", ("Arial", 15))

        ctk.CTkLabel(top, text="Crop:", font=DEFAULT_FONT).pack(side="left", padx=(0,6))
        crops = SubSupa.LoadCrops()
        self.crop_combo = ctk.CTkComboBox(top, values=crops, width=360, font=DEFAULT_FONT, command=self.on_crop_select)
        if crops:
            self.crop_combo.set(crops[0])
        self.crop_combo.pack(side="left")

        ctk.CTkButton(top, text="Load Summary", command=self.on_crop_select).pack(side="left", padx=8)

        # Treeview with averages
        cols = ("Strain", "WetWeight (lbs)", "WetCount", "Avg Wet (lbs)", "DryWeight (lbs)", "DryCount", "Avg Dry (lbs)")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            if c == "Strain":
                self.tree.column(c, width=320, anchor="w")
            elif c in ("Avg Wet (lbs)", "Avg Dry (lbs)"):
                self.tree.column(c, width=140, anchor="e")
            else:
                self.tree.column(c, width=120, anchor="e")
        # Configure treeview row tags for dark theme
        self.tree.tag_configure("odd", background="#1f1f1f", foreground="#dce4ee")
        self.tree.tag_configure("even", background="#2b2b2b", foreground="#dce4ee")
        self.tree.tag_configure("total", background="#1f538d", foreground="#ffffff", font=("Arial", 15, "bold"))
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0,10))
        self.status = ctk.CTkLabel(bottom, text="", font=("Arial", 12), text_color="#00aa00")
        self.status.pack(side="left")
        ctk.CTkButton(bottom, text="Export CSV", command=self.export_csv, width=140, font=DEFAULT_FONT).pack(side="right", padx=6)
        ctk.CTkButton(bottom, text="Close", command=self.destroy, width=100, font=DEFAULT_FONT).pack(side="right", padx=6)

    def show_status(self, msg, secs=4):
        self.status.configure(text=msg)
        if secs:
            self.after(secs*1000, lambda: self.status.configure(text=""))

    def parse_crop_no(self, label: str):
        if not label:
            return None
        try:
            return int(str(label).split(" - ")[0])
        except Exception:
            try:
                return int(label)
            except Exception:
                return None

    def on_crop_select(self, _=None):
        sel = self.crop_combo.get()
        crop_no = self.parse_crop_no(sel)
        if not crop_no:
            self.show_status("Please select a valid crop")
            return
        self.crop_no = crop_no
        self.show_status("Loading summary...")
        self.load_summary(crop_no)

    def load_summary(self, crop_no: int):
        # Clear tree
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        try:
            res = SubSupa.sb.schema("scale").table("scaleplants").select("Strain,WetWeight,DryWeight").eq("CropNo", crop_no).execute()
            rows = res.data or []
        except Exception as e:
            self.show_status(f"Error querying scaleplants: {e}")
            return

        # aggregate by strain
        agg = {}
        for r in rows:
            strain = (r.get("Strain") or "").strip()
            wet = float(r.get("WetWeight") or 0.0)
            dry = float(r.get("DryWeight") or 0.0)
            if strain not in agg:
                agg[strain] = {"wet_g": 0.0, "dry_g": 0.0, "wet_count": 0, "dry_count": 0}
            agg[strain]["wet_g"] += wet
            agg[strain]["dry_g"] += dry
            if wet > 0:
                agg[strain]["wet_count"] += 1
            if dry > 0:
                agg[strain]["dry_count"] += 1

        # display sorted by strain
        total_wet_g = 0.0
        total_dry_g = 0.0
        total_wet_count = 0
        total_dry_count = 0

        for i, (strain, vals) in enumerate(sorted(agg.items(), key=lambda kv: kv[0])):
            wet_lbs = vals["wet_g"] * GRAMS_TO_LBS
            dry_lbs = vals["dry_g"] * GRAMS_TO_LBS
            wet_count = vals["wet_count"]
            dry_count = vals["dry_count"]
            # averages: avoid division by zero
            avg_wet = (wet_lbs / wet_count) if wet_count else 0.0
            avg_dry = (dry_lbs / dry_count) if dry_count else 0.0
            total_wet_g += vals["wet_g"]
            total_dry_g += vals["dry_g"]
            total_wet_count += wet_count
            total_dry_count += dry_count
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", values=(strain, f"{wet_lbs:.2f}", str(wet_count), f"{avg_wet:.2f}" if wet_count else "", f"{dry_lbs:.2f}", str(dry_count), f"{avg_dry:.2f}" if dry_count else ""), tags=(tag,))

        # totals row
        total_wet_lbs = total_wet_g * GRAMS_TO_LBS
        total_dry_lbs = total_dry_g * GRAMS_TO_LBS
        # Totals: leave average columns blank for total row
        self.tree.insert("", "end", values=("TOTAL", f"{total_wet_lbs:.2f}", str(total_wet_count), "", f"{total_dry_lbs:.2f}", str(total_dry_count), ""), tags=("total",))

        self.show_status(f"Loaded {len(agg)} strains")

    def export_csv(self):
        # Optional convenience: export visible table to CSV
        try:
            import csv, tempfile, os
            tmp = tempfile.gettempdir()
            path = os.path.join(tmp, f"plant_weights_crop_{self.crop_no or 'X'}.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["Strain", "WetWeight (lbs)", "WetCount", "Avg Wet (lbs)", "DryWeight (lbs)", "DryCount", "Avg Dry (lbs)"])
                for iid in self.tree.get_children():
                    vals = self.tree.item(iid, "values")
                    writer.writerow(vals)
            self.show_status(f"Exported CSV to {path}")
        except Exception as e:
            self.show_status(f"Error exporting CSV: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = PlantWeightsSummary()
    app.mainloop()
    restart_menu()
