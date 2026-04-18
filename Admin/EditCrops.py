"""EditCrops - Edit or Add Crops in the scalecrops table

Allows users to:
- Select an existing crop to edit HarvestDate and CropStat
- Add a new crop with a HarvestDate and CropStat
"""
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
import SubSupa
import os
import subprocess
import sys

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

def launch_sop():
    # EditCrops.py is in scale/Harvest/
    this_file = Path(__file__).resolve()
    scale_root = this_file.parents[1]  # .../scale
    sop_md = scale_root / "sop" / "Harvest" / "EditCrops.md"
    viewer_py = scale_root / "common" / "SopViewer.py"

    # Launch separate process (non-blocking)
    if sop_md.exists():
        subprocess.Popen(
            [sys.executable, str(viewer_py), str(sop_md)],
            cwd=str(scale_root),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
        )

APP_TITLE = "Edit Crops"
DEFAULT_FONT = ("Arial", 14)


class EditCropsApp(ctk.CTk):
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
        self.geometry("600x300")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Crop Selection
        ctk.CTkLabel(frame, text="Crop", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.CropCombo = ctk.CTkComboBox(frame, values=[], width=280, font=DEFAULT_FONT, command=self.on_crop_selected)
        self.CropCombo.grid(row=0, column=1, sticky="w", pady=6)

        # Harvest Date
        ctk.CTkLabel(frame, text="Harvest Date", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.HarvestDateEntry = ctk.CTkEntry(frame, width=280, font=DEFAULT_FONT)
        self.HarvestDateEntry.grid(row=1, column=1, sticky="w", pady=6)

        # Crop Status
        ctk.CTkLabel(frame, text="Crop Status", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6))
        self.CropStatCombo = ctk.CTkComboBox(frame, values=["Active", "Inactive"], width=280, font=DEFAULT_FONT)
        self.CropStatCombo.grid(row=2, column=1, sticky="w", pady=6)
        self.CropStatCombo.set("Active")

        # Buttons
        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12,0))
        
        self.BtnUpdate = ctk.CTkButton(button_row, text="Update", font=DEFAULT_FONT, command=self.update_crop)
        self.BtnUpdate.pack(side="left", padx=(0,8))
        
        self.BtnInsert = ctk.CTkButton(button_row, text="Insert", font=DEFAULT_FONT, command=self.insert_crop)
        self.BtnInsert.pack(side="left", padx=(0,8))
        
        self.BtnRefresh = ctk.CTkButton(button_row, text="Refresh", font=DEFAULT_FONT, command=self.load_crops)
        self.BtnRefresh.pack(side="left", padx=(0,8))
        
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self._on_close).pack(side="left", padx=(0,8))

        # Status Label
        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8,0))

        # Track current mode
        self.current_mode = None  # 'edit' or 'new'
        self.current_crop_no = None

        # Load initial data
        self.load_crops()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def set_status(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def load_crops(self):
        """Load all crops (Active and Inactive) into combo box"""
        try:
            crops = SubSupa.LoadAllCrops()
            if crops:
                self.CropCombo.configure(values=crops)
                self.CropCombo.set(crops[0])
            else:
                self.CropCombo.configure(values=["Select", "New Crop"])
                self.CropCombo.set("Select")
            self.set_status("Crops loaded")
        except Exception as e:
            self.set_status(f"LoadAllCrops failed: {e}")

    def on_crop_selected(self, val=None):
        """Handle crop selection"""
        sel = (self.CropCombo.get() or "").strip()
        
        if not sel or sel.lower() == "select":
            self.clear_fields()
            self.current_mode = None
            self.current_crop_no = None
            self.BtnUpdate.configure(state="disabled")
            self.BtnInsert.configure(state="disabled")
            self.set_status("Please select a crop or 'New Crop'")
            return
        
        if sel == "New Crop":
            self.clear_fields()
            self.current_mode = "new"
            self.current_crop_no = None
            self.CropStatCombo.set("Active")
            self.BtnUpdate.configure(state="disabled")
            self.BtnInsert.configure(state="normal")
            self.set_status("Enter new crop details and click Insert")
            return
        
        # Parse crop number from selection (e.g., "19 - 2025-11-15 (Active)")
        token = sel.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status("Cannot parse Crop number")
                return
        
        # Load crop data
        try:
            crop_data = SubSupa.GetCropData(crop_no)
            if crop_data:
                self.current_mode = "edit"
                self.current_crop_no = crop_no
                
                harvest_date = crop_data.get("HarvestDate", "")
                crop_stat = crop_data.get("CropStat", "Active")
                
                self.HarvestDateEntry.delete(0, "end")
                self.HarvestDateEntry.insert(0, harvest_date if harvest_date else "")
                
                self.CropStatCombo.set(crop_stat if crop_stat else "Active")
                
                self.BtnUpdate.configure(state="normal")
                self.BtnInsert.configure(state="disabled")
                self.set_status(f"Crop {crop_no} loaded - modify and click Update")
            else:
                self.set_status(f"No data found for Crop {crop_no}")
                self.clear_fields()
        except Exception as e:
            self.set_status(f"Error loading crop data: {e}")

    def clear_fields(self):
        """Clear all entry fields"""
        self.HarvestDateEntry.delete(0, "end")
        self.CropStatCombo.set("Active")

    def update_crop(self):
        """Update existing crop"""
        if self.current_mode != "edit" or self.current_crop_no is None:
            messagebox.showwarning("No Crop Selected", "Please select an existing crop to update")
            return
        
        harvest_date = self.HarvestDateEntry.get().strip()
        crop_stat = self.CropStatCombo.get().strip()
        
        if not harvest_date:
            messagebox.showwarning("Missing Date", "Please enter a Harvest Date")
            return
        
        # Validate date format (basic check)
        try:
            datetime.strptime(harvest_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter date in YYYY-MM-DD format")
            return
        
        try:
            SubSupa.UpdateCrop(self.current_crop_no, harvest_date, crop_stat)
            self.set_status(f"Crop {self.current_crop_no} updated successfully")
            self.load_crops()  # Refresh the list
        except Exception as e:
            self.set_status(f"Update failed: {e}")
            messagebox.showerror("Update Error", f"Failed to update crop: {e}")

    def insert_crop(self):
        """Insert new crop"""
        if self.current_mode != "new":
            messagebox.showwarning("Wrong Mode", "Please select 'New Crop' to insert")
            return
        
        harvest_date = self.HarvestDateEntry.get().strip()
        crop_stat = self.CropStatCombo.get().strip()
        
        if not harvest_date:
            messagebox.showwarning("Missing Date", "Please enter a Harvest Date")
            return
        
        # Validate date format (basic check)
        try:
            datetime.strptime(harvest_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter date in YYYY-MM-DD format")
            return
        
        # Get next crop number
        try:
            # Get the highest existing CropNo and add 1
            crops_list = SubSupa.LoadAllCrops()
            max_crop_no = 0
            for crop in crops_list:
                if crop not in ["Select", "New Crop"]:
                    token = crop.split('-')[0].strip()
                    try:
                        crop_no = int(token.split()[0])
                        if crop_no > max_crop_no:
                            max_crop_no = crop_no
                    except:
                        pass
            
            new_crop_no = max_crop_no + 1
            
            SubSupa.InsertCrop(new_crop_no, harvest_date, crop_stat)
            self.set_status(f"Crop {new_crop_no} inserted successfully")
            self.load_crops()  # Refresh the list
            self.clear_fields()
        except Exception as e:
            self.set_status(f"Insert failed: {e}")
            messagebox.showerror("Insert Error", f"Failed to insert crop: {e}")

    def _on_close(self):
        """Handle window close event"""
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = EditCropsApp()
    app.mainloop()
    restart_menu()
