"""AddPackage - enter packaging activity

UI flow:
 - Select Crop (SubSupa.LoadCrops)
 - Select Strain (SubSupa.LoadStrains)
 - Select Type (Flower, Jars, PreRolls, Trim, Hash, Rosin)
 - Enter Metrc ID (via QR scanner or manual entry)
 - Enter Quantity, Save -> uses SubSupa.GetPackageWeight and SubSupa.InsertPackage
 - Shows existing packages for Type via SubSupa.GetPackages
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import re
from datetime import datetime
from pathlib import Path
import SubSupa
import SubPrintLabels
import os
import sys
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Common'))
import SubReadQRCode

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

def launch_sop():
    # AddPackage.py is in scale/Packaging/
    this_file = Path(__file__).resolve()
    scale_root = this_file.parents[1]  # .../scale
    sop_md = scale_root / "sop" / "Packaging" / "AddPackage.md"
    viewer_py = scale_root / "common" / "SopViewer.py"

    # Launch separate process (non-blocking)
    subprocess.Popen(
        [sys.executable, str(viewer_py), str(sop_md)],
        cwd=str(scale_root),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
    )

APP_TITLE = "Add Package"
DEFAULT_FONT = ("Arial", 15)


class AddPackageApp(ctk.CTk):
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
        
        # QR scanner status indicator
        self.QrStatusLabel = ctk.CTkLabel(menu_bar, text="QR: Checking...", font=("Arial", 12), 
                                          text_color="#ff8800", corner_radius=6, 
                                          fg_color="#2b2b2b", padx=10, pady=5)
        self.QrStatusLabel.pack(side="right", padx=6, pady=4)
        
        self.title(APP_TITLE)
        self.geometry("1100x520")

        # Set customtkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Configure ttk.Treeview style (still needed for treeview)
        style = ttk.Style(self)
        style.theme_use('clam')
        # Dark theme colors to match CTk
        style.configure("Treeview", 
                       background="#2b2b2b",
                       foreground="#dce4ee",
                       fieldbackground="#2b2b2b",
                       borderwidth=0,
                       font=("Arial", 12))
        style.configure("Treeview.Heading", 
                       background="#1f538d",
                       foreground="#dce4ee",
                       borderwidth=1,
                       font=("Arial", 12, "bold"))
        style.map("Treeview", background=[("selected", "#144870")])

        # Row 0: header
        ctk.CTkLabel(frame, text="Enter Packaging Activity", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        # Row 1: Crop, Strain, Type
        ctk.CTkLabel(frame, text="Crop:", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6), pady=8)
        self.cmb_crop = ctk.CTkComboBox(
            frame, values=["Loading..."], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.on_crop_selected())
        self.cmb_crop.grid(row=1, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Strain:", font=DEFAULT_FONT).grid(row=1, column=2, sticky="e", padx=(6,6), pady=8)
        self.cmb_strain = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.on_strain_selected())
        self.cmb_strain.grid(row=1, column=3, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Type:", font=DEFAULT_FONT).grid(row=1, column=4, sticky="e", padx=(6,6), pady=8)
        self.cmb_type = ctk.CTkComboBox(
            frame, values=["Select","Flower", "Jars", "PreRolls", "Trim", "Hash", "Rosin"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.load_cases())
        self.cmb_type.grid(row=1, column=5, sticky="w", pady=8)
        self.cmb_type.set("Select")

        # Row 2: Type and Metrc ID

        ctk.CTkLabel(frame, text="Case No:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6), pady=8)
        self.cmb_caseno = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.on_case_selected())
        self.cmb_caseno.grid(row=2, column=1, sticky="w", pady=8)
        self.cmb_caseno.set("Select")

        ctk.CTkLabel(frame, text="Metrc ID:", font=DEFAULT_FONT).grid(row=2, column=2, sticky="e", padx=(6,6), pady=8)
        self.ent_metrc = ctk.CTkEntry(frame, width=220, font=DEFAULT_FONT)
        self.ent_metrc.grid(row=2, column=3, sticky="w", pady=8)
        self.ent_metrc.bind('<Return>', lambda e: self.on_metrc_entered())

        ctk.CTkLabel(frame, text="Quantity:", font=DEFAULT_FONT).grid(row=2, column=4, sticky="e", padx=(6,6), pady=8)
        self.ent_qty = ctk.CTkEntry(frame, width=140, font=DEFAULT_FONT)
        self.ent_qty.grid(row=2, column=5, sticky="w", pady=8)

        # Buttons
        self.btn_save = ctk.CTkButton(frame, text="Save", font=DEFAULT_FONT, command=self.on_save)
        self.btn_save.grid(row=3, column=5, sticky="e", pady=(6,12))
        self.btn_refresh = ctk.CTkButton(frame, text="Refresh Lists", font=DEFAULT_FONT, command=self.load_crops)
        self.btn_refresh.grid(row=3, column=1, sticky="e", pady=(6,12))
        self.btn_print = ctk.CTkButton(frame, text="Print Label", font=DEFAULT_FONT, command=self.on_print_label)
        self.btn_print.grid(row=3, column=3, sticky="w", pady=(6,12))

        # Treeview for existing packages (ttk.Treeview kept as CTk doesn't have native treeview)
        cols = ("Crop", "Strain", "Type", "Case", "MetrcID", "Units", "Weight", "PackDate")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            if c == "Crop":
                self.tree.column(c, width=40, anchor="center")
            elif c == "Case":
                self.tree.column(c, width=40, anchor="center")
            elif c == "Type":
                self.tree.column(c, width=110, anchor="w")
            elif c in ("Units", "Weight"):
                self.tree.column(c, width=50, anchor="e")
            elif c == "PackDate":
                self.tree.column(c, width=100, anchor="center")
            else:
                self.tree.column(c, width=200, anchor="w")
        self.tree.grid(row=4, column=0, columnspan=6, sticky="nsew", pady=(6,0))

        # configure a tag for the totals row (slightly emphasized)
        try:
            self.tree.tag_configure('total', background='#1f538d', foreground='#ffffff', font=("Arial", 12, "bold"))
        except Exception:
            pass

        # status
        self.status = ctk.CTkLabel(frame, text="", font=("Arial", 10))
        self.status.grid(row=5, column=0, columnspan=5, sticky="w", pady=(8,0))

        # Close button
        self.btn_close = ctk.CTkButton(frame, text="Close", font=DEFAULT_FONT, command=self.destroy)
        self.btn_close.grid(row=5, column=5, sticky="e", pady=(8,0))

        # make tree expand
        frame.rowconfigure(4, weight=1)
        frame.columnconfigure(3, weight=1)

        # Initialize QR scanner
        SubReadQRCode.ConnectScanner()

        # Start checking for QR codes
        self.check_qr_code()
        
        # Initialize QR status tracking and start periodic status checks
        self.PrevQrStatus = None
        self.check_qr_status()
        self.schedule_qr_status_check()

        # initial load
        self.load_crops()

    def set_status(self, text: str):
        self.status.configure(text=text)

    def load_crops(self):
        try:
            crops = SubSupa.LoadCrops() or []
            self.cmb_crop.configure(values=crops)
            self.cmb_crop.set('Select')
            # Reset downstream combos
            self.cmb_strain.configure(values=['Select'])
            self.cmb_strain.set('Select')
            self.cmb_type.set('Select')
            self.cmb_caseno.configure(values=['Select'])
            self.cmb_caseno.set('Select')
            self.ent_metrc.delete(0, 'end')
        except Exception as e:
            self.set_status(f"LoadCrops failed: {e}")

    def on_crop_selected(self):
        crop_display = (self.cmb_crop.get() or '').strip()
        if not crop_display or crop_display.lower().startswith('select'):
            return
        token = crop_display.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status('Cannot parse Crop number')
                return
        try:
            strains = SubSupa.LoadStrains(crop_no) or ['Select']
            self.cmb_strain.configure(values=strains)
            self.cmb_strain.set('Select')
        except Exception as e:
            self.set_status(f"LoadStrains failed: {e}")

    def on_strain_selected(self):
        crop_display = (self.cmb_crop.get() or '').strip()
        strain = (self.cmb_strain.get() or '').strip()
        if not crop_display or crop_display.lower().startswith('select') or not strain or strain.lower().startswith('select'):
            return
        token = crop_display.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status('Cannot parse Crop number')
                return
        # Load packages for the selected crop and strain
        self.load_packages(crop_no, strain)

    def load_cases(self):
        """Load cases based on selected crop, strain, and type; populate Metrc ID if available"""
        crop_display = (self.cmb_crop.get() or '').strip()
        strain = (self.cmb_strain.get() or '').strip()
        ptype = (self.cmb_type.get() or '').strip()
        
        if not crop_display or crop_display.lower().startswith('select'):
            self.set_status('Please select a crop first')
            return
        if not strain or strain.lower().startswith('select'):
            self.set_status('Please select a strain first')
            return
        if not ptype or ptype.lower().startswith('select'):
            return
        
        # Parse crop number
        token = crop_display.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status('Cannot parse Crop number')
                return
        
        try:
            # LoadCases returns (cases, metrcid) - list of cases and metrc id
            result = SubSupa.LoadCases(crop_no, strain, ptype)
            if result:
                cases, metrcid = result
                cases = cases or ['Select']
                self.cmb_caseno.configure(values=cases)
                self.cmb_caseno.set('Select')
                
                # If metrcid is not None, populate the Metrc ID entry
                if metrcid:
                    self.ent_metrc.delete(0, 'end')
                    self.ent_metrc.insert(0, metrcid)
                    self.set_status(f"Type selected: {ptype}, Metrc ID: {metrcid}")
                else:
                    self.set_status(f"Type selected: {ptype}")
            else:
                self.cmb_caseno.configure(values=['Select'])
                self.cmb_caseno.set('Select')
                self.set_status(f"Type selected: {ptype}")
        except Exception as e:
            self.set_status(f"LoadCases failed: {e}")

    def on_case_selected(self):
        """Called when Case No is selected - populate Metrc ID if available"""
        case_display = (self.cmb_caseno.get() or '').strip()
        if not case_display or case_display.lower().startswith('select'):
            return
        
        # Try to get metrc from the case selection
        # Assuming the case may have format like "CaseNo (MetrcID)" or just "CaseNo"
        try:
            parts = re.split(r"\s*\(", case_display)
            case_no = parts[0].strip()
            metrc = ''
            if len(parts) > 1:
                metrc = parts[1].rstrip(') ').strip()
            
            # If metrc is not None/empty, populate the Metrc ID entry
            if metrc:
                self.ent_metrc.delete(0, 'end')
                self.ent_metrc.insert(0, metrc)
                self.set_status(f"Case {case_no} selected, Metrc ID: {metrc}")
            else:
                self.set_status(f"Case {case_no} selected")
        except Exception as e:
            self.set_status(f"Error processing case selection: {e}")

    def on_type_selected(self):
        """Called when Type is selected - just updates status"""
        ptype = (self.cmb_type.get() or '').strip()
        self.set_status(f"Type selected: {ptype}")

    def on_metrc_entered(self):
        """Called when Metrc ID is entered or scanned"""
        metrc_id = (self.ent_metrc.get() or '').strip()
        ptype = (self.cmb_type.get() or '').strip()
#        if metrc_id and ptype:
#            self.load_packages(metrc_id, ptype)

    def check_qr_code(self):
        """Periodically check for QR code scans"""
        qr_code = SubReadQRCode.CheckQr()
        if qr_code and qr_code != "none":
            # QR code scanned, populate Metrc ID field
            self.ent_metrc.delete(0, 'end')
            self.ent_metrc.insert(0, qr_code)
            self.on_metrc_entered()
        # Check again in 100ms
        self.after(100, self.check_qr_code)
    
    def check_qr_status(self):
        """Check QR scanner status"""
        try:
            qr_available = hasattr(SubReadQRCode, 'QrReader') and SubReadQRCode.QrReader is not None
            if qr_available != self.PrevQrStatus:
                self.PrevQrStatus = qr_available
                if qr_available:
                    self.QrStatusLabel.configure(text="QR: Connected", text_color="#00aa00")
                else:
                    self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
        except Exception:
            if self.PrevQrStatus is not False:
                self.PrevQrStatus = False
                self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
    
    def schedule_qr_status_check(self):
        """Schedule periodic QR status checks every 10 seconds"""
        self.check_qr_status()
        try:
            self.after(10000, self.schedule_qr_status_check)
        except Exception:
            pass

    def load_packages(self, crop_no: int, strain: str):
        try:
            rows = SubSupa.GetPackages(crop_no, strain) or []
        except Exception as e:
            self.set_status(f"GetPackages failed: {e}")
            rows = []

        # clear tree
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for r in rows:
            if isinstance(r, dict):
                crop = r.get('CropNo', '')
                strain_val = r.get('Strain', '')
                case = r.get('CaseNo', '')
                metrc = r.get('MetrcID', '')
                ptype = r.get('PackageType', '')
                qty = r.get('TotUnits', '')
                wt = r.get('TotWeight', '')
                pdate = r.get('PackDate', '')
                # Format date if it's a datetime string
                if pdate and len(str(pdate)) > 10:
                    pdate = str(pdate)[:10]  # Take just the date part
            else:
                # best effort for object-like rows
                crop = getattr(r, 'CropNo', '')
                strain_val = getattr(r, 'Strain', '')
                case = getattr(r, 'CaseNo', '')
                metrc = getattr(r, 'MetrcID', '')
                ptype = getattr(r, 'PackageType', '')
                qty = getattr(r, 'TotUnits', '')
                wt = getattr(r, 'TotWeight', '')
                pdate = getattr(r, 'PackDate', '')
                if pdate and len(str(pdate)) > 10:
                    pdate = str(pdate)[:10]

            vals = (str(crop), str(strain_val), str(ptype), str(case), str(metrc), str(qty), str(wt), str(pdate))
            self.tree.insert('', 'end', values=vals)

        # insert a totals row
        total_qty = 0
        total_wt = 0
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, 'values') or ()
            try:
                q = int(vals[5]) if len(vals) > 5 and vals[5] not in (None, '') else 0
            except Exception:
                q = 0
            try:
                w = int(vals[6]) if len(vals) > 6 and vals[6] not in (None, '') else 0
            except Exception:
                w = 0.0
            total_qty += q
            total_wt += w

        # append totals row with a tag
        total_vals = ('', '', '', 'TOTAL', '', str(total_qty), f"{total_wt}", '')
        self.tree.insert('', 'end', values=total_vals, tags=('total',))

        self.set_status(f"Loaded {len(rows)} package rows for Crop {crop_no}, {strain} — Total: {total_qty} units, {total_wt:.2f} g")

    def on_print_label(self):
        """Print label for selected package from treeview"""
        # Get selected item from treeview
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('No Selection', 'Please select a package from the list to print')
            return
        
        # Get the first selected item
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        # Check if this is the totals row
        if values and values[3] == 'TOTAL':
            messagebox.showwarning('Invalid Selection', 'Cannot print label for totals row')
            return
        
        # Extract values from treeview (Crop, Strain, Case, MetrcID, Type, Units, Weight, PackDate)
        if len(values) < 8:
            messagebox.showwarning('Invalid Data', 'Selected row does not have complete data')
            return
        
        crop_no = values[0]
        strain = values[1]
        package_type = values[2]
        case_no = values[3]
        metrc_id = values[4]
        
        # Parse crop_no and case_no to integers
        try:
            crop_no_int = int(crop_no)
        except Exception:
            messagebox.showwarning('Invalid Crop', 'Cannot parse crop number')
            return
        
        try:
            case_no_int = int(case_no)
        except Exception:
            messagebox.showwarning('Invalid Case', case_no)
            return
        
        # Get the full package data using GetOnePackage
        try:
            package_data = SubSupa.GetOnePackage(crop_no_int, strain, package_type, case_no_int)
            if not package_data or len(package_data) == 0:
                messagebox.showwarning('No Data', 'Could not retrieve package data from database')
                return
            
            pkg = package_data[0]
            tot_units = pkg.get('TotUnits', '')
            tot_weight = pkg.get('TotWeight', '')
            pack_date = pkg.get('PackDate', '')
            
            # Get HarvestDate from scalecrops table
            harvest_date = SubSupa.GetHarvestDate(crop_no_int)
            if not harvest_date:
                harvest_date = pack_date  # Use pack date as fallback
            
            # Print the label
            SubPrintLabels.PrintPackageLabel(strain, harvest_date, package_type, case_no, metrc_id, tot_units, tot_weight)
            self.set_status(f'Label printed for {package_type} - Case {case_no}')
            
        except Exception as e:
            self.set_status(f"Print failed: {e}")
            messagebox.showerror('Print Error', f'Failed to print label: {e}')

    def on_save(self):
        self.set_status('Saving package...')

        crop_display = (self.cmb_crop.get() or '').strip()
        strain = (self.cmb_strain.get() or '').strip()
        case_no = (self.cmb_caseno.get() or '').strip()
        metrc_id = (self.ent_metrc.get() or '').strip()
        pkgtype = (self.cmb_type.get() or '').strip()
        qtys = (self.ent_qty.get() or '').strip()
        
        # Validate crop selection
        if not crop_display or crop_display.lower().startswith('select'):
            messagebox.showwarning('Select Crop', 'Please select a crop')
            return
        
        # Validate strain selection
        if not strain or strain.lower().startswith('select'):
            messagebox.showwarning('Select Strain', 'Please select a strain')
            return
        
        # Parse crop number
        token = crop_display.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.set_status('Cannot parse Crop number')
                messagebox.showwarning('Crop Error', 'Cannot parse crop number')
                return

        # Validate case selection
        if case_no.lower().startswith('new'):
            case_no = SubSupa.GetNewCaseNo(crop_no, strain, pkgtype)

        if not case_no or case_no.lower().startswith('select'):
            messagebox.showwarning('Select Case', 'Please select a case')
            return
        
        # Validate Metrc ID
        if not metrc_id:
            messagebox.showwarning('Metrc ID', 'Please enter or scan a Metrc ID')
            return
        
        # Validate type
        if not pkgtype or pkgtype.lower().startswith('select'):
            messagebox.showwarning('Select Type', 'Please select a type')
            return
        
        # Validate quantity
        try:
            qty = int(qtys)
            if qty <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning('Quantity', 'Please enter a positive integer quantity')
            return

        # get unit weight
        try:
            unit_weight = SubSupa.GetPackageWeight(pkgtype)
        except Exception as e:
            self.set_status(f"GetPackageWeight failed: {e}")
            return
        if unit_weight is None:
            messagebox.showwarning('Unit Weight', f'No unit weight found for {pkgtype}')
            return
        try:
            unit_w = float(unit_weight)
        except Exception:
            messagebox.showwarning('Unit Weight', 'Invalid unit weight returned from DB')
            return

        tot_weight = unit_w * qty
        self.set_status('Inserting package...')
        try:
            # InsertPackage(CropNo, Strain, CaseNo, MetrcID, PackageType, TotUnits, TotWeight, PackDate)
            SubSupa.InsertPackage(crop_no, strain, case_no, metrc_id, pkgtype, qty, tot_weight, datetime.now().isoformat())
            self.set_status(f'Inserted {qty} x {pkgtype} ({tot_weight} g) for Case {case_no}, Metrc {metrc_id}')
        except Exception as e:
            self.set_status(f"InsertPackage failed: {e}")
            messagebox.showerror('Insert Failed', f"Failed to insert package: {e}")
            return

        # refresh tree with crop_no and strain
        self.load_packages(crop_no, strain)
        # clear metrc and quantity so user can start a new entry
        try:
            self.ent_metrc.delete(0, 'end')
        except Exception:
            pass
        try:
            self.ent_qty.delete(0, 'end')
        except Exception:
            pass


def main():
    app = AddPackageApp()
    app.mainloop()


if __name__ == '__main__':
    main()
    restart_menu()
