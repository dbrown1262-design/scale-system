"""HarvestSummary - Harvest Summary Report

Display a comprehensive harvest summary showing wet/dry weights and bucked breakdown
by strain for a selected crop.
"""
import customtkinter as ctk
from tkinter import ttk
from pathlib import Path
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

APP_TITLE = "Harvest Summary Report"
DEFAULT_FONT = ("Arial", 14)


class HarvestSummaryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("1000x700")

        # Configure treeview style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="#dce4ee",
                       fieldbackground="#2b2b2b",
                       font=("Arial", 16),
                       rowheight=28)
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="#ffffff",
                       font=("Arial", 16, "bold"))
        style.map("Treeview",
                 background=[("selected", "#144870")])

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Header controls
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,12))
        
        ctk.CTkLabel(header_frame, text="Crop:", font=DEFAULT_FONT).pack(side="left", padx=(6,6))
        self.CropCombo = ctk.CTkComboBox(header_frame, values=[], width=250, font=DEFAULT_FONT, command=self.onCropSelected)
        self.CropCombo.pack(side="left", padx=(0,16))
        
        ctk.CTkButton(header_frame, text="Refresh", width=100, font=DEFAULT_FONT, command=self.loadSummary).pack(side="left", padx=(0,16))
        ctk.CTkButton(header_frame, text="Close", width=100, font=DEFAULT_FONT, command=self.onClose).pack(side="left")

        # Treeview with summary data
        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(0,8))
        
        cols = ("Strain", "WetLbs", "DryLbs", "DryPct", "FlowerLbs", "FlowerPct", 
                "SmallsLbs", "SmallsPct", "TrimLbs", "TrimPct", "StemsLbs", "StemsPct")
        self.Tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        
        # Configure columns
        self.Tree.heading("Strain", text="Strain")
        self.Tree.heading("WetLbs", text="Wet ")
        self.Tree.heading("DryLbs", text="Dry ")
        self.Tree.heading("DryPct", text="%")
        self.Tree.heading("FlowerLbs", text="Flower")
        self.Tree.heading("FlowerPct", text="%")
        self.Tree.heading("SmallsLbs", text="Smalls")
        self.Tree.heading("SmallsPct", text="%")
        self.Tree.heading("TrimLbs", text="Trim")
        self.Tree.heading("TrimPct", text="%")
        self.Tree.heading("StemsLbs", text="Stems")
        self.Tree.heading("StemsPct", text=" %")
        
        self.Tree.column("Strain", width=150, anchor="w")
        self.Tree.column("WetLbs", width=90, anchor="e")
        self.Tree.column("DryLbs", width=90, anchor="e")
        self.Tree.column("DryPct", width=80, anchor="e")
        self.Tree.column("FlowerLbs", width=100, anchor="e")
        self.Tree.column("FlowerPct", width=90, anchor="e")
        self.Tree.column("SmallsLbs", width=100, anchor="e")
        self.Tree.column("SmallsPct", width=90, anchor="e")
        self.Tree.column("TrimLbs", width=90, anchor="e")
        self.Tree.column("TrimPct", width=80, anchor="e")
        self.Tree.column("StemsLbs", width=90, anchor="e")
        self.Tree.column("StemsPct", width=80, anchor="e")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=scrollbar.set)
        
        self.Tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Status label
        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8,0))

        # Configure grid weights
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # Load crops
        self.loadCrops()

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
            else:
                self.CropCombo.configure(values=["Select"])
                self.CropCombo.set("Select")
        except Exception as e:
            self.setStatus(f"LoadCrops failed: {e}")

    def onCropSelected(self, val=None):
        self.loadSummary()

    def loadSummary(self):
        selCrop = (self.CropCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select"):
            return
        
        # Parse crop number
        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.setStatus("Cannot parse Crop number")
                return
        
        # Clear treeview
        for iid in self.Tree.get_children():
            self.Tree.delete(iid)
        
        try:
            # Get strain weights
            strain_weights = SubSupa.GetStrainWeights(crop_no)
            
            if not strain_weights:
                self.setStatus(f"No data found for crop {crop_no}")
                return
            
            # Initialize totals
            total_wet = 0
            total_dry = 0
            total_flower = 0
            total_smalls = 0
            total_trim = 0
            total_stems = 0
            
            # Process each strain
            for strain_data in strain_weights:
                strain = strain_data.get("strain", "")
                wet_lbs = strain_data.get("wet_lbs", 0)
                dry_lbs = strain_data.get("dry_lbs", 0)
                
                # Calculate dry percentage
                dry_pct = round((dry_lbs / wet_lbs * 100), 1) if wet_lbs > 0 else 0
                
                # Get bucked summary for this strain
                bucked = SubSupa.GetBuckedSummary(crop_no, strain)
                
                # Extract weights for each type
                flower_lbs = 0
                smalls_lbs = 0
                trim_lbs = 0
                
                for item in bucked:
                    tote_type = item.get("ToteType", "")
                    weight = item.get("Weight", 0)
                    
                    if tote_type == "Flower":
                        flower_lbs = weight
                    elif tote_type == "Smalls":
                        smalls_lbs = weight
                    elif tote_type == "Trim":
                        trim_lbs = weight
                
                # Calculate stems
                stems_lbs = round(dry_lbs - flower_lbs - smalls_lbs - trim_lbs, 1)
                
                # Calculate percentages
                flower_pct = round((flower_lbs / dry_lbs * 100), 1) if dry_lbs > 0 else 0
                smalls_pct = round((smalls_lbs / dry_lbs * 100), 1) if dry_lbs > 0 else 0
                trim_pct = round((trim_lbs / dry_lbs * 100), 1) if dry_lbs > 0 else 0
                stems_pct = round((stems_lbs / dry_lbs * 100), 1) if dry_lbs > 0 else 0
                
                # Add to totals
                total_wet += wet_lbs
                total_dry += dry_lbs
                total_flower += flower_lbs
                total_smalls += smalls_lbs
                total_trim += trim_lbs
                total_stems += stems_lbs
                
                # Insert row
                self.Tree.insert('', 'end', values=(
                    strain,
                    wet_lbs,
                    dry_lbs,
                    f"{dry_pct}%",
                    flower_lbs,
                    f"{flower_pct}%",
                    smalls_lbs,
                    f"{smalls_pct}%",
                    trim_lbs,
                    f"{trim_pct}%",
                    stems_lbs,
                    f"{stems_pct}%"
                ))
            
            # Insert total row
            total_dry_pct = round((total_dry / total_wet * 100), 1) if total_wet > 0 else 0
            total_flower_pct = round((total_flower / total_dry * 100), 1) if total_dry > 0 else 0
            total_smalls_pct = round((total_smalls / total_dry * 100), 1) if total_dry > 0 else 0
            total_trim_pct = round((total_trim / total_dry * 100), 1) if total_dry > 0 else 0
            total_stems_pct = round((total_stems / total_dry * 100), 1) if total_dry > 0 else 0
            
            self.Tree.insert('', 'end', values=(
                "TOTAL",
                round(total_wet, 1),
                round(total_dry, 1),
                f"{total_dry_pct}%",
                round(total_flower, 1),
                f"{total_flower_pct}%",
                round(total_smalls, 1),
                f"{total_smalls_pct}%",
                round(total_trim, 1),
                f"{total_trim_pct}%",
                round(total_stems, 1),
                f"{total_stems_pct}%"
            ), tags=('total',))
            
            # Configure total row style
            self.Tree.tag_configure('total', background='#1f538d', font=("Arial", 16, "bold"))
            
            self.setStatus(f"Loaded {len(strain_weights)} strains for crop {crop_no}")
        except Exception as e:
            self.setStatus(f"Load failed: {e}")
            import traceback
            traceback.print_exc()

    def onClose(self):
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = HarvestSummaryApp()
    app.mainloop()
    restart_menu()
