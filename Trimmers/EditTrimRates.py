import customtkinter as ctk
from tkinter import ttk, messagebox
import SubSupa
from datetime import datetime
import os
import sys
import subprocess

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


class EditTrimRatesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("Edit Trim Rates")
        self.geometry("800x600")

        self.crop_no = None

        # Configure treeview style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="#dce4ee",
                       fieldbackground="#2b2b2b",
                       font=("Arial", 18),
                       rowheight=30)
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="#ffffff",
                       font=("Arial", 18, "bold"))
        style.map("Treeview",
                 background=[("selected", "#144870")])

        # Top row: crop selector
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(top, text="Crop:", font=("Arial", 14)).pack(side="left", padx=(0, 6))
        crops = SubSupa.LoadCrops()
        self.crop_combo = ctk.CTkComboBox(top, values=crops, width=300, command=self.on_crop_select)
        if crops:
            self.crop_combo.set(crops[0])
        self.crop_combo.pack(side="left")

        ctk.CTkButton(top, text="Ensure & Load", command=self.on_crop_select).pack(side="left", padx=6)

        # Treeview for strains and rates
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=6)

        columns = ("Strain", "BigsRate")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Strain", text="Strain")
        self.tree.heading("BigsRate", text="BigsRate")
        self.tree.column("Strain", width=400, anchor="w")
        self.tree.column("BigsRate", width=200, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Edit frame
        edit_frame = ctk.CTkFrame(self)
        edit_frame.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(edit_frame, text="Strain:", font=("Arial", 14)).grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.strain_label = ctk.CTkLabel(edit_frame, text="", font=("Arial", 14), width=300, anchor="w")
        self.strain_label.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(edit_frame, text="BigsRate:", font=("Arial", 14)).grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.rate_entry = ctk.CTkEntry(edit_frame, width=150)
        self.rate_entry.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        ctk.CTkButton(edit_frame, text="Update", command=self.update_rate).grid(row=0, column=4, padx=6, pady=6)

        # Bottom buttons
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=10, pady=(0, 10))
        self.status = ctk.CTkLabel(bottom, text="", font=("Arial", 12), text_color="#00aa00")
        self.status.pack(side="left", padx=(4, 8))
        ctk.CTkButton(bottom, text="Close", command=self.destroy).pack(side="right", padx=(6, 0))

    def show_status(self, text, secs=3):
        self.status.configure(text=text)
        if secs:
            self.after(secs * 1000, lambda: self.status.configure(text=""))

    def parse_crop_no(self, label: str):
        # labels are like "19 - 2023-04-12" or just a number
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
        self.show_status("Checking strains and rates...")
        self.ensure_rates_for_crop(crop_no)
        self.load_rates(crop_no)

    def ensure_rates_for_crop(self, crop_no: int):
        """Ensure a row exists in trimrates for every strain in the crop. Insert default BigsRate=0.36 where missing."""
        try:
            strains = SubSupa.LoadStrains(crop_no)
            # LoadStrains returns ["Select"] + strains
            strains = [s for s in strains if s and s != "Select"]
            for strain in strains:
                q = SubSupa.sb.schema("scale").table("trimrates").select("CropNo").eq("CropNo", crop_no).eq("Strain", strain).execute()
                exists = bool(q.data)
                if not exists:
                    SubSupa.sb.schema("scale").table("trimrates").insert({
                        "CropNo": int(crop_no),
                        "Strain": strain,
                        "BigsRate": 0.36,
                    }).execute()
        except Exception as e:
            self.show_status(f"Error ensuring rates: {e}")

    def load_rates(self, crop_no: int):
        # Clear previous rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.strain_label.configure(text="")
        self.rate_entry.delete(0, 'end')

        try:
            res = SubSupa.sb.schema("scale").table("trimrates").select("Strain,BigsRate").eq("CropNo", crop_no).order("Strain").execute()
            rows = res.data or []
            if not rows:
                self.show_status("No rates found for this crop")
                return
            
            for r in rows:
                strain = r.get("Strain") or ""
                bigs = r.get("BigsRate") or 0.0
                self.tree.insert("", "end", values=(strain, f"{float(bigs):.4f}"))
            
            self.show_status(f"Loaded {len(rows)} strains")
        except Exception as e:
            self.show_status(f"Error loading rates: {e}")

    def on_double_click(self, event):
        """Load selected row into edit fields on double-click"""
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if values:
            self.strain_label.configure(text=values[0])
            self.rate_entry.delete(0, 'end')
            self.rate_entry.insert(0, values[1])

    def update_rate(self):
        """Update the rate for the selected strain"""
        if not self.crop_no:
            messagebox.showwarning("No Crop", "Select a crop first")
            return
        
        strain = self.strain_label.cget("text")
        if not strain:
            messagebox.showwarning("No Selection", "Double-click a row to select a strain to edit")
            return
        
        rate_str = self.rate_entry.get().strip()
        try:
            rate = float(rate_str)
        except ValueError:
            messagebox.showerror("Invalid Rate", "BigsRate must be a valid number")
            return
        
        try:
            SubSupa.sb.schema("scale").table("trimrates").update({"BigsRate": rate}).eq("CropNo", self.crop_no).eq("Strain", strain).execute()
            
            # Update the treeview
            sel = self.tree.selection()
            if sel:
                self.tree.item(sel[0], values=(strain, f"{rate:.4f}"))
            
            self.show_status(f"Updated {strain} to {rate:.4f}")
            self.strain_label.configure(text="")
            self.rate_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update rate: {e}")




if __name__ == "__main__":
    app = EditTrimRatesApp()
    app.mainloop()
    restart_menu()
