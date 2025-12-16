"""EditPackageTypes - simple editor for packagetypes table

Shows a Treeview of package types and allows adding/updating rows via
SubSupa.InsertPackageType and SubSupa.UpdatePackageType.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
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

APP_TITLE = "Edit Package Types"
DEFAULT_FONT = ("Arial", 15)


class EditPackageTypesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x420")

        # Set customtkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Configure ttk.Treeview style (still needed for treeview)
        style = ttk.Style(self)
        style.theme_use('clam')
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

        # Treeview
        ctk.CTkLabel(frame, text="Package Types", font=("Arial", 15, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        cols = ("TypeName", "UnitWeight", "NumUnits", "TotWeight")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            if c == "TypeName":
                self.tree.column(c, width=240, anchor="w")
            else:
                self.tree.column(c, width=120, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(6,12))
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.on_tree_select())

        # Form fields
        ctk.CTkLabel(frame, text="Type Name:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(0, 6))
        self.ent_type = ctk.CTkEntry(frame, width=300, font=DEFAULT_FONT)
        self.ent_type.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        ctk.CTkLabel(frame, text="Unit Weight:", font=DEFAULT_FONT).grid(row=2, column=2, sticky="e", padx=(0, 6))
        self.ent_unit = ctk.CTkEntry(frame, width=120, font=DEFAULT_FONT)
        self.ent_unit.grid(row=2, column=3, sticky="w", padx=6, pady=6)

        ctk.CTkLabel(frame, text="Num Units:", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(0, 6))
        self.ent_num = ctk.CTkEntry(frame, width=120, font=DEFAULT_FONT)
        self.ent_num.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        ctk.CTkLabel(frame, text="Tot Weight:", font=DEFAULT_FONT).grid(row=3, column=2, sticky="e", padx=(0, 6))
        self.ent_tot = ctk.CTkEntry(frame, width=120, font=DEFAULT_FONT)
        self.ent_tot.grid(row=3, column=3, sticky="w", padx=6, pady=6)

        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=4, pady=(12,0))
        self.btn_add = ctk.CTkButton(btn_frame, text="Add Row", font=DEFAULT_FONT, command=self.add_row)
        self.btn_update = ctk.CTkButton(btn_frame, text="Update Selected", font=DEFAULT_FONT, command=self.update_row)
        self.btn_refresh = ctk.CTkButton(btn_frame, text="Refresh", font=DEFAULT_FONT, command=self.load_rows)
        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear", font=DEFAULT_FONT, command=self.clear_form)
        self.btn_close = ctk.CTkButton(btn_frame, text="Close", font=DEFAULT_FONT, command=self.destroy)
        self.btn_add.grid(row=0, column=0, padx=6)
        self.btn_update.grid(row=0, column=1, padx=6)
        self.btn_refresh.grid(row=0, column=2, padx=6)
        self.btn_clear.grid(row=0, column=3, padx=6)
        self.btn_close.grid(row=0, column=4, padx=6)

        # status
        self.status = ctk.CTkLabel(frame, text="", font=("Arial", 15))
        self.status.grid(row=5, column=0, columnspan=4, sticky="w", pady=(8,0))

        # make tree expand
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

        self.selected_id = None
        self.load_rows()

    def set_status(self, text: str):
        try:
            self.status.configure(text=text)
        except Exception:
            pass

    def load_rows(self):
        try:
            rows = SubSupa.LoadPackageTypes() or []
        except Exception as e:
            self.set_status(f"LoadPackageTypes failed: {e}")
            rows = []

        # clear
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for r in rows:
            # r may be dict-like
            rid = r.get('id') if isinstance(r, dict) else getattr(r, 'id', None)
            t = r.get('PackageType') if isinstance(r, dict) else getattr(r, 'PackageType', '')
            uw = r.get('UnitWeight') if isinstance(r, dict) else getattr(r, 'UnitWeight', 0)
            nu = r.get('NumUnits') if isinstance(r, dict) else getattr(r, 'NumUnits', 0)
            tw = r.get('TotWeight') if isinstance(r, dict) else getattr(r, 'TotWeight', 0)
            vals = (t or '', str(uw or ''), str(nu or ''), str(tw or ''))
            # use id as iid when possible
            try:
                self.tree.insert('', 'end', iid=str(rid) if rid is not None else None, values=vals)
            except Exception:
                self.tree.insert('', 'end', values=vals)

        self.set_status(f"Loaded {len(rows)} package types")

    def on_tree_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        vals = self.tree.item(iid, 'values')
        if not vals:
            return
        # store selected id if iid is numeric
        try:
            self.selected_id = int(iid)
        except Exception:
            self.selected_id = None

        try:
            self.ent_type.delete(0, 'end')
            self.ent_unit.delete(0, 'end')
            self.ent_num.delete(0, 'end')
            self.ent_tot.delete(0, 'end')
            self.ent_type.insert(0, vals[0])
            self.ent_unit.insert(0, vals[1])
            self.ent_num.insert(0, vals[2])
            self.ent_tot.insert(0, vals[3])
            self.set_status(f"Selected row {iid}")
        except Exception:
            pass

    def clear_form(self):
        try:
            self.selected_id = None
            self.ent_type.delete(0, 'end')
            self.ent_unit.delete(0, 'end')
            self.ent_num.delete(0, 'end')
            self.ent_tot.delete(0, 'end')
            self.set_status("")
        except Exception:
            pass

    def add_row(self):
        t = (self.ent_type.get() or "").strip()
        uw = (self.ent_unit.get() or "").strip()
        nu = (self.ent_num.get() or "").strip()
        tw = (self.ent_tot.get() or "").strip()

        if not t:
            messagebox.showwarning("Type Name", "Please enter a Type Name")
            return
        try:
            uwf = float(uw) if uw else 0.0
        except Exception:
            messagebox.showwarning("Unit Weight", "Unit Weight must be a number")
            return
        try:
            nui = int(nu) if nu else 0
        except Exception:
            messagebox.showwarning("Num Units", "Num Units must be an integer")
            return
        try:
            twf = float(tw) if tw else 0.0
        except Exception:
            messagebox.showwarning("Tot Weight", "Tot Weight must be a number")
            return

        try:
            SubSupa.InsertPackageType(t, uwf, nui, twf)
            self.set_status(f"Inserted {t}")
        except Exception as e:
            self.set_status(f"InsertPackageType failed: {e}")
            return
        self.load_rows()
        self.clear_form()

    def update_row(self):
        if not self.selected_id:
            messagebox.showwarning("Select Row", "Please select a row to update")
            return
        t = (self.ent_type.get() or "").strip()
        uw = (self.ent_unit.get() or "").strip()
        nu = (self.ent_num.get() or "").strip()
        tw = (self.ent_tot.get() or "").strip()

        if not t:
            messagebox.showwarning("Type Name", "Please enter a Type Name")
            return
        try:
            uwf = float(uw) if uw else 0.0
        except Exception:
            messagebox.showwarning("Unit Weight", "Unit Weight must be a number")
            return
        try:
            nui = int(nu) if nu else 0
        except Exception:
            messagebox.showwarning("Num Units", "Num Units must be an integer")
            return
        try:
            twf = float(tw) if tw else 0.0
        except Exception:
            messagebox.showwarning("Tot Weight", "Tot Weight must be a number")
            return

        try:
            SubSupa.UpdatePackageType(self.selected_id, t, uwf, nui, twf)
            self.set_status(f"Updated id {self.selected_id}")
        except Exception as e:
            self.set_status(f"UpdatePackageType failed: {e}")
            return
        self.load_rows()


def main():
    app = EditPackageTypesApp()
    app.mainloop()
    restart_menu()


if __name__ == '__main__':
    main()
