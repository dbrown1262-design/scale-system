"""EditSupplies - Add Supplies, Vendors, and Departments

Allows users to:
- Add a new supply item with Vendor, Dept, Descr, and Size
- Add a new vendor to suppliesvendors
- Add a new department to suppliesdept
"""
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
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

APP_TITLE = "Edit Supplies"
DEFAULT_FONT = ("Arial", 14)


class EditSuppliesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("650x750")

        # Main container with scrollable frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # ========== Section 1: Add Supply Item ==========
        supply_frame = ctk.CTkFrame(main_frame)
        supply_frame.pack(fill="x", padx=8, pady=(8,12))
        
        ctk.CTkLabel(supply_frame, text="Add Supply Item", font=("Arial", 16, "bold")).pack(pady=(8,12))
        
        supply_grid = ctk.CTkFrame(supply_frame, fg_color="transparent")
        supply_grid.pack(fill="x", padx=12, pady=(0,12))
        
        # Vendor
        ctk.CTkLabel(supply_grid, text="Vendor", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.VendorCombo = ctk.CTkComboBox(supply_grid, values=[], width=280, font=DEFAULT_FONT)
        self.VendorCombo.grid(row=0, column=1, sticky="w", pady=6)
        
        # Dept
        ctk.CTkLabel(supply_grid, text="Dept", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.DeptCombo = ctk.CTkComboBox(supply_grid, values=[], width=280, font=DEFAULT_FONT)
        self.DeptCombo.grid(row=1, column=1, sticky="w", pady=6)
        
        # Descr
        ctk.CTkLabel(supply_grid, text="Description", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6))
        self.DescrEntry = ctk.CTkEntry(supply_grid, width=280, font=DEFAULT_FONT)
        self.DescrEntry.grid(row=2, column=1, sticky="w", pady=6)
        
        # Size
        ctk.CTkLabel(supply_grid, text="Size", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(6,6))
        self.SizeEntry = ctk.CTkEntry(supply_grid, width=280, font=DEFAULT_FONT)
        self.SizeEntry.grid(row=3, column=1, sticky="w", pady=6)
        
        # Button
        supply_btn_frame = ctk.CTkFrame(supply_frame, fg_color="transparent")
        supply_btn_frame.pack(pady=(0,8))
        ctk.CTkButton(supply_btn_frame, text="Add Supply", font=DEFAULT_FONT, command=self.insert_supply).pack(padx=8)

        # ========== Section 2: Add Vendor ==========
        vendor_frame = ctk.CTkFrame(main_frame)
        vendor_frame.pack(fill="x", padx=8, pady=12)
        
        ctk.CTkLabel(vendor_frame, text="Add Vendor", font=("Arial", 16, "bold")).pack(pady=(8,12))
        
        vendor_grid = ctk.CTkFrame(vendor_frame, fg_color="transparent")
        vendor_grid.pack(fill="x", padx=12, pady=(0,12))
        
        ctk.CTkLabel(vendor_grid, text="Vendor Name", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.VendorNameEntry = ctk.CTkEntry(vendor_grid, width=280, font=DEFAULT_FONT)
        self.VendorNameEntry.grid(row=0, column=1, sticky="w", pady=6)
        
        # Button
        vendor_btn_frame = ctk.CTkFrame(vendor_frame, fg_color="transparent")
        vendor_btn_frame.pack(pady=(0,8))
        ctk.CTkButton(vendor_btn_frame, text="Add Vendor", font=DEFAULT_FONT, command=self.insert_vendor).pack(padx=8)

        # ========== Section 3: Add Department ==========
        dept_frame = ctk.CTkFrame(main_frame)
        dept_frame.pack(fill="x", padx=8, pady=12)
        
        ctk.CTkLabel(dept_frame, text="Add Department", font=("Arial", 16, "bold")).pack(pady=(8,12))
        
        dept_grid = ctk.CTkFrame(dept_frame, fg_color="transparent")
        dept_grid.pack(fill="x", padx=12, pady=(0,12))
        
        ctk.CTkLabel(dept_grid, text="Department Name", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.DeptNameEntry = ctk.CTkEntry(dept_grid, width=280, font=DEFAULT_FONT)
        self.DeptNameEntry.grid(row=0, column=1, sticky="w", pady=6)
        
        # Button
        dept_btn_frame = ctk.CTkFrame(dept_frame, fg_color="transparent")
        dept_btn_frame.pack(pady=(0,8))
        ctk.CTkButton(dept_btn_frame, text="Add Department", font=DEFAULT_FONT, command=self.insert_dept).pack(padx=8)

        # ========== Bottom Buttons and Status ==========
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(12,8))
        
        button_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_row.pack()
        
        ctk.CTkButton(button_row, text="Refresh", font=DEFAULT_FONT, command=self.load_data).pack(side="left", padx=(0,8))
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self._on_close).pack(side="left", padx=(0,8))

        # Status Label
        self.StatusLabel = ctk.CTkLabel(main_frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.pack(pady=(8,0))

        # Load initial data
        self.load_data()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def set_status(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def load_data(self):
        """Load vendors and departments into combo boxes"""
        try:
            vendors = SubSupa.LoadVendors()
            depts = SubSupa.LoadDepts()
            
            if vendors:
                self.VendorCombo.configure(values=vendors)
                self.VendorCombo.set(vendors[0])
            else:
                self.VendorCombo.configure(values=["Select"])
                self.VendorCombo.set("Select")
            
            if depts:
                self.DeptCombo.configure(values=depts)
                self.DeptCombo.set(depts[0])
            else:
                self.DeptCombo.configure(values=["Select"])
                self.DeptCombo.set("Select")
            
            self.set_status("Data loaded successfully")
        except Exception as e:
            self.set_status(f"Load failed: {e}")

    def insert_supply(self):
        """Insert new supply item"""
        vendor = self.VendorCombo.get().strip()
        dept = self.DeptCombo.get().strip()
        descr = self.DescrEntry.get().strip()
        size = self.SizeEntry.get().strip()
        
        if not vendor or vendor == "Select":
            messagebox.showwarning("Missing Vendor", "Please select a vendor")
            return
        
        if not dept or dept == "Select":
            messagebox.showwarning("Missing Department", "Please select a department")
            return
        
        if not descr:
            messagebox.showwarning("Missing Description", "Please enter a description")
            return
        
        if not size:
            messagebox.showwarning("Missing Size", "Please enter a size")
            return
        
        try:
            SubSupa.InsertSupply(vendor, dept, descr, size)
            self.set_status(f"Supply '{descr}' added successfully")
            # Clear fields
            self.DescrEntry.delete(0, "end")
            self.SizeEntry.delete(0, "end")
        except Exception as e:
            self.set_status(f"Insert failed: {e}")
            messagebox.showerror("Insert Error", f"Failed to insert supply: {e}")

    def insert_vendor(self):
        """Insert new vendor"""
        vendor_name = self.VendorNameEntry.get().strip()
        
        if not vendor_name:
            messagebox.showwarning("Missing Vendor Name", "Please enter a vendor name")
            return
        
        try:
            SubSupa.InsertVendor(vendor_name)
            self.set_status(f"Vendor '{vendor_name}' added successfully")
            # Clear field and reload vendors
            self.VendorNameEntry.delete(0, "end")
            self.load_data()
        except Exception as e:
            self.set_status(f"Insert failed: {e}")
            messagebox.showerror("Insert Error", f"Failed to insert vendor: {e}")

    def insert_dept(self):
        """Insert new department"""
        dept_name = self.DeptNameEntry.get().strip()
        
        if not dept_name:
            messagebox.showwarning("Missing Department Name", "Please enter a department name")
            return
        
        try:
            SubSupa.InsertDept(dept_name)
            self.set_status(f"Department '{dept_name}' added successfully")
            # Clear field and reload departments
            self.DeptNameEntry.delete(0, "end")
            self.load_data()
        except Exception as e:
            self.set_status(f"Insert failed: {e}")
            messagebox.showerror("Insert Error", f"Failed to insert department: {e}")

    def _on_close(self):
        """Handle window close event"""
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = EditSuppliesApp()
    app.mainloop()
    restart_menu()
