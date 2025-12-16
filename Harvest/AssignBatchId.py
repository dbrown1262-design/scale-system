import customtkinter as ctk
from tkinter import ttk, messagebox
import SubSupa
import os
import sys
import subprocess

APP_TITLE = "Assign Batch IDs"
DEFAULT_FONT = ("Arial", 15)
BATCH_TYPES = ["Select", "Flower", "Smalls", "Hash", "Rosin"]

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


class AssignBatchIdApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("1200x600")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

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


        ctk.CTkLabel(frame, text="Crop", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6))
        self.CropCombo = ctk.CTkComboBox(frame, values=[], width=200, font=DEFAULT_FONT, command=self.OnCropSelected)
        self.CropCombo.grid(row=0, column=1, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Strain", font=DEFAULT_FONT).grid(row=0, column=2, sticky="e", padx=(6,6))
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], width=200, font=DEFAULT_FONT, command=self.OnStrainSelected)
        self.StrainCombo.grid(row=0, column=3, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Batch Type", font=DEFAULT_FONT).grid(row=0, column=4, sticky="e", padx=(6,6))
        self.BatchTypeCombo = ctk.CTkComboBox(frame, values=BATCH_TYPES, width=200, font=DEFAULT_FONT)
        self.BatchTypeCombo.grid(row=0, column=5, sticky="w", pady=6)
        self.BatchTypeCombo.set(BATCH_TYPES[0])

        ctk.CTkLabel(frame, text="Batch ID", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.BatchIdEntry = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT)
        self.BatchIdEntry.grid(row=1, column=1, sticky="w", pady=6)

        self.BtnAdd = ctk.CTkButton(frame, text="Add", font=DEFAULT_FONT, command=self.AddBatch)
        self.BtnAdd.grid(row=1, column=3, sticky="w", padx=(8,0))
        self.BtnUpdate = ctk.CTkButton(frame, text="Update Selected", font=DEFAULT_FONT, command=self.UpdateBatch)
        self.BtnUpdate.grid(row=1, column=5, sticky="w", padx=(8,0))

        # Batch tree view (shows batches for crop or for selected strain)
        ctk.CTkLabel(frame, text="Batch IDs", font=DEFAULT_FONT).grid(row=4, column=0, sticky="nw", padx=(6,6), pady=(12,0))
        self.BatchTree = ttk.Treeview(frame, columns=("BatchType","BatchId","Strain"), show="headings", height=10)
        self.BatchTree.heading("BatchType", text="Type")
        self.BatchTree.heading("BatchId", text="Batch ID")
        self.BatchTree.heading("Strain", text="Strain")
        self.BatchTree.column("BatchType", width=80, anchor="center")
        self.BatchTree.column("BatchId", width=200, anchor="w")
        self.BatchTree.column("Strain", width=200, anchor="w")
        self.BatchTree.grid(row=4, column=2, columnspan=5, sticky="w", pady=(12,0))
        # bind selection
        self.BatchTree.bind('<<TreeviewSelect>>', lambda e: self.OnTreeSelect())
        # Configure treeview row tags
        self.BatchTree.tag_configure("odd", background="#1f1f1f")
        self.BatchTree.tag_configure("even", background="#2b2b2b")

        # status and close button row
        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(row=5, column=0, columnspan=6, sticky="ew", pady=(12,0))
        
        self.StatusLabel = ctk.CTkLabel(button_row, text="", font=DEFAULT_FONT, text_color="#00aa00")
        self.StatusLabel.pack(side="left", padx=(0,20))
        
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self.destroy).pack(side="right", padx=(0,6))

        self.LoadCrops()

    def SetStatus(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def LoadCrops(self):
        try:
            crops = SubSupa.LoadCrops()
            if crops:
                self.CropCombo.configure(values=crops)
                self.CropCombo.set(crops[0])
                # pre-load strains and batch list
                self.OnCropSelected()
            else:
                self.CropCombo.configure(values=["Select"])
                self.CropCombo.set("Select")
        except Exception as e:
            self.SetStatus(f"LoadCrops failed: {e}")

    def OnCropSelected(self, val=None):
        sel = (self.CropCombo.get() or "").strip()
        if not sel or sel.lower().startswith("select"):
            self.StrainCombo.configure(values=["Select"])
            self.StrainCombo.set("Select")
            # clear tree
            for iid in self.BatchTree.get_children():
                self.BatchTree.delete(iid)
            return
        token = sel.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.SetStatus("Cannot parse Crop number")
                return
        try:
            strains = SubSupa.LoadStrains(crop_no)
            if strains:
                self.StrainCombo.configure(values=strains)
                self.StrainCombo.set(strains[0])
            else:
                self.StrainCombo.configure(values=["Select"])
                self.StrainCombo.set("Select")
            # load batch list for crop
            self.LoadBatchList(crop_no)
        except Exception as e:
            self.SetStatus(f"LoadStrains failed: {e}")

    def OnStrainSelected(self, val=None):
        # populate tree with one row per BatchType for this strain
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select") or not selStrain or selStrain.lower().startswith("select"):
            return
        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.SetStatus("Cannot parse Crop number")
                return
            # clear tree
        for iid in self.BatchTree.get_children():
            self.BatchTree.delete(iid)
        res = SubSupa.LoadOneBatch(crop_no, selStrain)
        for i, r in enumerate(res):
            bid = None
            bid = r.get('BatchId')
            bt = r.get('BatchType')
            tag = "odd" if i % 2 else "even"
            self.BatchTree.insert('', 'end', values=(bt, bid or "", selStrain), tags=(tag,))
        self.SetStatus(f"Loaded batch rows for strain {selStrain}")

    def LoadBatchList(self, crop_no: int):
        # Use SubSupa.LoadAllBatches to retrieve all batch rows for the crop and display in tree
        try:
            # clear tree
            for iid in self.BatchTree.get_children():
                self.BatchTree.delete(iid)
            rows = SubSupa.LoadAllBatches(crop_no) or []
            entries = []
            for r in rows:
                strain = r.get('Strain') if isinstance(r, dict) else getattr(r, 'Strain', '')
                btype = r.get('BatchType') if isinstance(r, dict) else getattr(r, 'BatchType', '')
                bid = r.get('BatchId') if isinstance(r, dict) else getattr(r, 'BatchId', '')
                entries.append((btype, bid or "", strain))
            # sort by strain then type
            entries.sort(key=lambda x: (x[2] or "", x[0] or ""))
            for i, e in enumerate(entries):
                tag = "odd" if i % 2 else "even"
                self.BatchTree.insert('', 'end', values=e, tags=(tag,))
            self.SetStatus(f"Loaded {len(entries)} batch ids for crop {crop_no}")
        except Exception as e:
            self.SetStatus(f"LoadBatchList failed: {e}")

    def OnTreeSelect(self):
        try:
            sel = self.BatchTree.selection()
            if not sel:
                return
            iid = sel[0]
            vals = self.BatchTree.item(iid, 'values')
            if not vals:
                return
            btype = vals[0] if len(vals) > 0 else ""
            bid = vals[1] if len(vals) > 1 else ""
            strain = vals[2] if len(vals) > 2 else ""
            try:
                self.BatchTypeCombo.set(btype)
            except Exception:
                pass
            try:
                self.BatchIdEntry.delete(0, 'end')
                self.BatchIdEntry.insert(0, bid or "")
            except Exception:
                pass
            # set strain combo to the strain from the row
            try:
                if strain:
                    self.StrainCombo.set(strain)
            except Exception:
                pass
        except Exception:
            pass

    def AddBatch(self):
        selCrop = (self.CropCombo.get() or "").strip()
        selStrain = (self.StrainCombo.get() or "").strip()
        selBatchType = (self.BatchTypeCombo.get() or "").strip()
        newBatchId = (self.BatchIdEntry.get() or "").strip()

        if not selCrop or selCrop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        if not selStrain or selStrain.lower().startswith("select"):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return
        if not selBatchType or selBatchType.lower().startswith("select"):
            messagebox.showwarning("Select Batch Type", "Please select a batch type")
            return
        if not newBatchId:
            messagebox.showwarning("Enter Batch ID", "Please enter a Batch ID")
            return

        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.SetStatus("Cannot parse Crop number")
                return

        # Insert a new BatchId (allow multiple per strain/type)
        try:
            SubSupa.InsertBatchId(crop_no, selStrain, selBatchType, newBatchId)
            self.SetStatus(f"Inserted BatchId {newBatchId}")
        except Exception as e:
            self.SetStatus(f"InsertBatchId failed: {e}")
            return

        # refresh list
        self.LoadBatchList(crop_no)

    def UpdateBatch(self):
        """Update the selected tree row's BatchId to the value in the entry.

        This updates only the specific row (via matching the old BatchId) so multiple
        BatchId rows can exist for the same crop/strain/type.
        """
        sel = self.BatchTree.selection()
        if not sel:
            messagebox.showwarning("Select Row", "Please select a batch row to update")
            return
        iid = sel[0]
        vals = self.BatchTree.item(iid, 'values')
        if not vals or len(vals) < 3:
            messagebox.showwarning("Invalid Selection", "Selected row is invalid")
            return
        old_btype = vals[0] or ""
        old_bid = vals[1] or ""
        old_strain = vals[2] or ""

        selCrop = (self.CropCombo.get() or "").strip()
        if not selCrop or selCrop.lower().startswith("select"):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return
        token = selCrop.split('-')[0].strip()
        try:
            crop_no = int(token.split()[0])
        except Exception:
            try:
                crop_no = int(token)
            except Exception:
                self.SetStatus("Cannot parse Crop number")
                return

        newBid = (self.BatchIdEntry.get() or "").strip()
        if not newBid:
            messagebox.showwarning("Enter Batch ID", "Please enter a new Batch ID")
            return

        # confirm
        resp = messagebox.askyesno("Confirm Update", f"Replace '{old_bid}' with '{newBid}' for {old_strain} {old_btype}?" )
        if not resp:
            self.SetStatus("Update cancelled")
            return

        try:
            # call new SubSupa.UpdateBatchRow to update only the selected row
            SubSupa.UpdateBatchRow(crop_no, old_strain, old_btype, old_bid, newBid)
            self.SetStatus(f"Updated BatchId {old_bid} -> {newBid}")
        except Exception as e:
            self.SetStatus(f"UpdateBatchRow failed: {e}")
            return

        # refresh
        self.LoadBatchList(crop_no)


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = AssignBatchIdApp()
    app.mainloop()
    restart_menu()

