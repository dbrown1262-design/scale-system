"""TrimmerStrainSummary - Trimmer Strain Summary Report

Display trimmer performance by strain, showing flower and smalls weights
for each trimmer.
"""
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
import subprocess
from SubSupa import LoadFlowerTrimRecords, LoadCrops, LoadStrains
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import os, tempfile, sys
from typing import Optional

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Conversion constant
#GRAMS_TO_LBS = 0.00220462262185
GRAMS_TO_LBS = 1.0

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


def hours_between(start_pg: Optional[str], end_pg: Optional[str]) -> float:
    """Return hours (float) between start and end DB times. Returns 0.0 if invalid."""
    if not start_pg or not end_pg:
        return 0.0
    try:
        s = datetime.strptime(start_pg, "%H:%M:%S")
    except Exception:
        try:
            s = datetime.strptime(start_pg, "%H:%M")
        except Exception:
            return 0.0
    try:
        e = datetime.strptime(end_pg, "%H:%M:%S")
    except Exception:
        try:
            e = datetime.strptime(end_pg, "%H:%M")
        except Exception:
            return 0.0
    delta = e - s
    # if negative, treat as 0
    total_seconds = max(delta.total_seconds(), 0.0)
    return round(total_seconds / 3600.0, 2)


class TrimmerStrainSummaryApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def _open_file(self, path):
        # Open the file with the default app on each OS
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)

    def create_widgets(self):
        # Main title
        title = ctk.CTkLabel(self, text="Trimmer Strain Summary", font=("Arial", 22, "bold"))
        title.pack(pady=(10, 6))

        # Configure treeview style for dark theme
        style = ttk.Style()
        try:
            try:
                # Use clam theme for dark mode
                style.theme_use("clam")
            except Exception:
                pass
            style.configure("TNotebook", background="#2b2b2b")
            # Create a larger Treeview style for row detail readability with dark theme
            style.configure("Large.Treeview", 
                           background="#2b2b2b",
                           foreground="#dce4ee",
                           fieldbackground="#2b2b2b",
                           font=("Arial", 18), 
                           rowheight=36)
            style.configure("Large.Treeview.Heading", 
                           background="#1f538d",
                           foreground="#ffffff",
                           font=("Arial", 18, "bold"))
            style.map("Large.Treeview",
                     background=[("selected", "#144870")])
        except Exception:
            pass

        # Filter controls
        strain_filter = ctk.CTkFrame(self)
        strain_filter.pack(fill="x", padx=10, pady=(6, 8))

        # Crop selector
        ctk.CTkLabel(strain_filter, text="Crop:", font=("Arial", 14)).pack(side="left", padx=(0,6))
        crops = LoadCrops() or ["Select"]
        self.CropCombo = ctk.CTkComboBox(strain_filter, values=crops, width=180, font=("Arial",13), command=self.on_strain_crop_changed)
        self.CropCombo.set("Select")
        self.CropCombo.pack(side="left", padx=(0,10))

        # Strain selector
        ctk.CTkLabel(strain_filter, text="Strain:", font=("Arial", 14)).pack(side="left", padx=(0,6))
        self.StrainCombo = ctk.CTkComboBox(strain_filter, values=["Select"], width=220, font=("Arial",13))
        self.StrainCombo.set("Select")
        self.StrainCombo.pack(side="left", padx=(0,10))

        ctk.CTkButton(strain_filter, text="Load Strain Summary", command=self.load_strain_summary, width=170).pack(side="left", padx=6)
        ctk.CTkButton(strain_filter, text="Export Strain PDF", command=self.export_strain_pdf, width=150).pack(side="left", padx=6)
        ctk.CTkButton(strain_filter, text="Close", width=100, command=lambda: self.master.destroy()).pack(side="left", padx=6)

        # Tree for strain summary: Date, Trimmer, Flower, Smalls, Hours, Grams/Hour
        self.StrainTree = ttk.Treeview(self, style="Large.Treeview", columns=("Date","Trimmer","Flower","Smalls","Hours","GramsPerHour"), show="headings")
        headings = {"Date": "Date", "Trimmer": "Trimmer", "Flower": "Flower", "Smalls": "Smalls", "Hours": "Hours", "GramsPerHour": "Grams/Hour"}
        for c in ("Date","Trimmer","Flower","Smalls","Hours","GramsPerHour"):
            self.StrainTree.heading(c, text=headings[c])
            if c == "Trimmer":
                self.StrainTree.column(c, width=200, anchor="w")
            elif c == "Date":
                self.StrainTree.column(c, width=140, anchor="w")
            elif c in ("Hours", "GramsPerHour"):
                self.StrainTree.column(c, width=110, anchor="e")
            else:
                self.StrainTree.column(c, width=120, anchor="e")
        self.StrainTree.pack(fill="both", expand=True, padx=10, pady=8)
        # style tags for strain tree (so the TOTAL row is highlighted) - dark theme
        try:
            self.StrainTree.tag_configure("odd", background="#1f1f1f", foreground="#dce4ee")
            self.StrainTree.tag_configure("even", background="#2b2b2b", foreground="#dce4ee")
            self.StrainTree.tag_configure("total", background="#1f538d", foreground="#ffffff", font=("Arial", 14, "bold"))
        except Exception:
            pass

    def on_strain_crop_changed(self, val):
        """Called when the Crop combo changes. Populate the Strain list."""
        v = (val or "").strip()
        if not v or v == "Select":
            self.StrainCombo.configure(values=["Select"])
            self.StrainCombo.set("Select")
            return
        try:
            crop_no = int(v.split("-")[0].strip())
        except Exception:
            self.StrainCombo.configure(values=["Select"])
            self.StrainCombo.set("Select")
            return
        try:
            strains = LoadStrains(crop_no) or ["Select"]
            self.StrainCombo.configure(values=strains)
            self.StrainCombo.set("Select")
        except Exception:
            self.StrainCombo.configure(values=["Select"])
            self.StrainCombo.set("Select")

    def load_strain_summary(self):
        """Load trimmer rows for the selected CropNo+Strain and populate the StrainTree."""
        crop_display = (self.CropCombo.get() or "").strip()
        strain = (self.StrainCombo.get() or "").strip()
        if not crop_display or crop_display == "Select":
            # nothing selected
            return
        try:
            crop_no = int(crop_display.split("-")[0].strip())
        except Exception:
            return

        if not strain or strain == "Select":
            # require specific strain for this report
            return

        # Use LoadFlowerTrimRecords to get all records for this crop and strain
        data = LoadFlowerTrimRecords(crop_no, strain)

        # Group by (date, trimmer)
        grouped = {}
        for r in data:
            td = (r.get("TrimDate") or "").split("T", 1)[0]
            tr = (r.get("TrimmerName") or "").strip()
            key = (td, tr)
            if key not in grouped:
                grouped[key] = {"flower": 0.0, "smalls": 0.0, "hours": 0.0}
            flower_grams = float(r.get("FlowerGrams") or 0.0)
            smalls_grams = float(r.get("SmallsGrams") or 0.0)
            grouped[key]["flower"] += flower_grams
            grouped[key]["smalls"] += smalls_grams
            
            # Calculate hours from start and end time
            start_pg = r.get("StartTime")
            end_pg = r.get("EndTime")
            if start_pg and end_pg:
                try:
                    hrs = hours_between(start_pg, end_pg)
                    grouped[key]["hours"] += hrs
                except Exception:
                    pass

        # Populate tree
        self.StrainTree.delete(*self.StrainTree.get_children())
        total_flower_lbs = 0.0
        total_smalls_lbs = 0.0
        total_hours = 0.0
        total_flower_grams = 0.0
        for (date_str, trimmer), vals in sorted(grouped.items()):
            f_lbs = round(vals["flower"] * GRAMS_TO_LBS, 1)
            s_lbs = round(vals["smalls"] * GRAMS_TO_LBS, 1)
            hrs = vals["hours"]
            # Calculate grams per hour (for flower only)
            grams_per_hour = round(vals["flower"] / hrs, 2) if hrs > 0 else 0.0
            
            total_flower_lbs += f_lbs
            total_smalls_lbs += s_lbs
            total_hours += hrs
            total_flower_grams += vals["flower"]
            
            hrs_str = f"{hrs:.2f}" if hrs else ""
            gph_str = f"{grams_per_hour:.2f}" if grams_per_hour else ""
            
            self.StrainTree.insert("", "end", values=(date_str, trimmer, f"{f_lbs:.1f}" if f_lbs else "", f"{s_lbs:.1f}" if s_lbs else "", hrs_str, gph_str))

        # Calculate total grams per hour
        total_grams_per_hour = round(total_flower_grams / total_hours, 2) if total_hours > 0 else 0.0
        total_gph_str = f"{total_grams_per_hour:.2f}" if total_grams_per_hour else ""
        
        # Insert totals as a final row in the tree with the 'total' tag for styling
        self.StrainTree.insert("", "end", values=("", "TOTAL", f"{total_flower_lbs:.1f}", f"{total_smalls_lbs:.1f}", f"{total_hours:.2f}" if total_hours else "", total_gph_str), tags=("total",))
    
    def export_strain_pdf(self):
        """Export the current StrainTree contents to a portrait LETTER PDF and open it."""
        # Helper to pull rows from the strain tree
        def tv_to_table(tree, header):
            rows = [header]
            for iid in tree.get_children():
                vals = tree.item(iid, "values")
                rows.append(list(vals))
            return rows

        # Build document
        tmpdir = tempfile.gettempdir()
        pdf_path = os.path.join(tmpdir, "trimmer_strain_summary.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=LETTER, leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
        styles = getSampleStyleSheet()
        story = []

        # Title and context
        story.append(Paragraph("<b>Trimmer Strain Summary</b>", styles["Title"]))
        # Add crop/strain info if available
        crop_display = (self.CropCombo.get() or "").strip()
        strain = (self.StrainCombo.get() or "").strip()
        info_lines = []
        if crop_display:
            info_lines.append(f"Crop: {crop_display}")
        if strain:
            info_lines.append(f"Strain: {strain}")
        if info_lines:
            story.append(Paragraph(" \u2022 ".join(info_lines), styles["Normal"]))
            story.append(Spacer(1, 0.1 * inch))

        # Table from the tree
        header = ["Date", "Trimmer", "Flower (g)", "Smalls (g)", "Hours", "Grams/Hour"]
        data = tv_to_table(self.StrainTree, header)
        if len(data) <= 1:
            # nothing to export
            return

        tbl = Table(data, hAlign="CENTER")
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.black),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 12),
            ("FONTSIZE", (0,1), (-1,-1), 12),
            ("ALIGN", (0,0), (-1,0), "CENTER"),
            ("ALIGN", (0,1), (-1,-1), "LEFT"),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.15 * inch))

        doc.build(story)
        self._open_file(pdf_path)


# ======= MAIN =======
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Trimmer Strain Summary")
    root.geometry("1200x700")

    app = TrimmerStrainSummaryApp(root)
    root.mainloop()
    restart_menu()
