"""AddPackage - enter packaging activity

UI flow:
 - Select Crop (SubSupa.LoadCrops)
 - Select Strain (SubSupa.LoadStrains)
 - Select Trim Type (SubSupa.LoadTrimTypes)
 - Select Batch (SubSupa.LoadBatches)
 - Select Package Type (SubSupa.LoadPackageTypes)
 - Enter Quantity, Save -> uses SubSupa.GetPackageWeight and SubSupa.InsertPackage
 - Shows existing packages for Batch+PackageType via SubSupa.GetPackages
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import re
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


APP_TITLE = "Add Package"
DEFAULT_FONT = ("Arial", 15)


class AddPackageApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x520")

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
                       font=("Arial", 15))
        style.configure("Treeview.Heading", 
                       background="#1f538d",
                       foreground="#dce4ee",
                       borderwidth=1,
                       font=("Arial", 15, "bold"))
        style.map("Treeview", background=[("selected", "#144870")])

        # Row 0: header
        ctk.CTkLabel(frame, text="Enter Packaging Activity", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        # Row 1: Crop
        ctk.CTkLabel(frame, text="Crop:", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6), pady=8)
        self.cmb_crop = ctk.CTkComboBox(
            frame, values=["Loading..."], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.on_crop_selected())
        self.cmb_crop.grid(row=1, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Strain:", font=DEFAULT_FONT).grid(row=1, column=2, sticky="e", padx=(6,6), pady=8)
        self.cmb_strain = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.on_strain_selected())
        self.cmb_strain.grid(row=1, column=3, sticky="w", pady=8)

    # (no trim-type selection needed for packaging flow)

        # Row 2: Batch
        ctk.CTkLabel(frame, text="Batch:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6), pady=8)
        self.cmb_batch = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.on_batch_selected())
        self.cmb_batch.grid(row=2, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Package Type:", font=DEFAULT_FONT).grid(row=2, column=2, sticky="e", padx=(6,6), pady=8)
        # package type is derived from BatchType and shown read-only
        self.ent_pkgtype = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT, state="disabled")
        self.ent_pkgtype.grid(row=2, column=3, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Quantity:", font=DEFAULT_FONT).grid(row=2, column=4, sticky="e", padx=(6,6), pady=8)
        self.ent_qty = ctk.CTkEntry(frame, width=140, font=DEFAULT_FONT)
        self.ent_qty.grid(row=2, column=5, sticky="w", pady=8)

        # Buttons
        self.btn_save = ctk.CTkButton(frame, text="Save", font=DEFAULT_FONT, command=self.on_save)
        self.btn_save.grid(row=3, column=5, sticky="e", pady=(6,12))
        self.btn_refresh = ctk.CTkButton(frame, text="Refresh Lists", font=DEFAULT_FONT, command=self.load_crops)
        self.btn_refresh.grid(row=3, column=1, sticky="e", pady=(6,12))

        # Treeview for existing packages (ttk.Treeview kept as CTk doesn't have native treeview)
        cols = ("BatchId", "Strain", "PackageType", "Quantity", "Weight")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            if c == "BatchId":
                self.tree.column(c, width=140, anchor="w")
            elif c in ("Quantity", "Weight"):
                self.tree.column(c, width=100, anchor="center")
            else:
                self.tree.column(c, width=140, anchor="w")
        self.tree.grid(row=4, column=0, columnspan=6, sticky="nsew", pady=(6,0))

        # configure a tag for the totals row (slightly emphasized)
        try:
            self.tree.tag_configure('total', background='#1f538d', foreground='#ffffff', font=("Arial", 15, "bold"))
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

        # initial load
        self.load_crops()

    def set_status(self, text: str):
        try:
            self.status.configure(text=text)
        except Exception:
            pass

    def load_crops(self):
        try:
            crops = SubSupa.LoadCrops() or []
            self.cmb_crop.configure(values=crops)
            self.cmb_crop.set('Select')
            # Reset downstream combos
            self.cmb_strain.configure(values=['Select'])
            self.cmb_strain.set('Select')
            self.cmb_batch.configure(values=['Select'])
            self.cmb_batch.set('Select')
            try:
                self.ent_pkgtype.configure(state='normal')
                self.ent_pkgtype.delete(0, 'end')
                self.ent_pkgtype.configure(state='disabled')
            except Exception:
                pass
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
        try:
            batches = SubSupa.LoadBatches(crop_no, strain) or ['Select']
            self.cmb_batch.configure(values=batches)
            self.cmb_batch.set('Select')
        except Exception as e:
            self.set_status(f"LoadBatches failed: {e}")

    # trim-type selection not used in packaging flow

    def on_batch_selected(self):
        batch_display = (self.cmb_batch.get() or '').strip()
        if not batch_display or batch_display.lower().startswith('select'):
            return
        # extract BatchId and BatchType from display like 'BATCHID (BatchType)'
        parts = re.split(r"\s*\(", batch_display)
        batch_id = parts[0].strip()
        batch_type = ''
        if len(parts) > 1:
            batch_type = parts[1].rstrip(') ').strip()

        # determine package type from batch type
        pkgtype = ''
        if batch_type.lower() == 'flower':
            pkgtype = 'Jars'
        elif batch_type.lower() == 'smalls':
            pkgtype = 'PreRoll'
        else:
            pkgtype = ''

        # show package type in disabled entry
        try:
            self.ent_pkgtype.configure(state='normal')
            self.ent_pkgtype.delete(0, 'end')
            self.ent_pkgtype.insert(0, pkgtype)
            self.ent_pkgtype.configure(state='disabled')
        except Exception:
            pass

        # clear tree if no pkgtype
        if not pkgtype:
            for iid in self.tree.get_children():
                self.tree.delete(iid)
            self.set_status('Unknown BatchType; package type not set')
            return

        self.load_packages(batch_id, pkgtype)

    # package type is determined from batch; no pkgtype selection handler

    def load_packages(self, batch_id: str, pkgtype: str):
        try:
            rows = SubSupa.GetPackages(batch_id, pkgtype) or []
        except Exception as e:
            self.set_status(f"GetPackages failed: {e}")
            rows = []

        # clear tree
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for r in rows:
            # r may include nested batchtable mapping
            if isinstance(r, dict):
                bid = r.get('BatchId')
                ptype = r.get('PackageType')
                unitw = r.get('UnitWeight')
                qty = r.get('TotUnits')
                wt = r.get('TotWeight')
                bt = r.get('batchtable') or {}
                strain = bt.get('Strain')
            else:
                # best effort for object-like rows
                bid = getattr(r, 'BatchId', None)
                ptype = getattr(r, 'PackageType', None)
                unitw = getattr(r, 'UnitWeight', None)
                qty = getattr(r, 'TotUnits', None)
                wt = getattr(r, 'TotWeight', None)
                bt = getattr(r, 'batchtable', None) or {}
                strain = bt.get('Strain') if isinstance(bt, dict) else None

            vals = (bid or '', strain or '', ptype or '', str(qty or ''), str(wt or ''))
            self.tree.insert('', 'end', values=vals)

        # insert a totals row
        total_qty = 0
        total_wt = 0.0
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, 'values') or ()
            try:
                q = int(vals[3]) if len(vals) > 3 and vals[3] not in (None, '') else 0
            except Exception:
                q = 0
            try:
                w = float(vals[4]) if len(vals) > 4 and vals[4] not in (None, '') else 0.0
            except Exception:
                w = 0.0
            total_qty += q
            total_wt += w

        # append totals row with a tag
        total_vals = ('', 'TOTAL', '', str(total_qty), f"{total_wt:.2f}")
        self.tree.insert('', 'end', values=total_vals, tags=('total',))

        self.set_status(f"Loaded {len(rows)} package rows for {batch_id} / {pkgtype} — Total: {total_qty} units, {total_wt:.2f} g")

    def on_save(self):
        batch_display = (self.cmb_batch.get() or '').strip()
        # package type is shown in the read-only entry
        pkgtype = (self.ent_pkgtype.get() or '').strip()
        qtys = (self.ent_qty.get() or '').strip()
        if not batch_display or batch_display.lower().startswith('select'):
            messagebox.showwarning('Select Batch', 'Please select a batch')
            return
        if not pkgtype or pkgtype.lower().startswith('select'):
            messagebox.showwarning('Select Package Type', 'Please select a package type')
            return
        try:
            qty = int(qtys)
            if qty <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning('Quantity', 'Please enter a positive integer quantity')
            return

        batch_id = re.split(r"\s*\(", batch_display)[0].strip()

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

        try:
            # pass UnitWeight, TotUnits and TotWeight, and PackDate (ISO) when inserting
            SubSupa.InsertPackage(batch_id, pkgtype, unit_w, qty, tot_weight, datetime.now().isoformat())
            self.set_status(f'Inserted {qty} x {pkgtype} ({tot_weight} g) for {batch_id}')
        except Exception as e:
            self.set_status(f"InsertPackage failed: {e}")
            return

        # refresh tree
        self.load_packages(batch_id, pkgtype)
        # reset package/batch combos and clear quantity so user can start a new entry
        # clear the read-only package-type entry
        try:
            self.ent_pkgtype.configure(state='normal')
            self.ent_pkgtype.delete(0, 'end')
            self.ent_pkgtype.insert(0, '')
            self.ent_pkgtype.configure(state='disabled')
        except Exception:
            pass
        try:
            self.cmb_batch.set('Select')
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
