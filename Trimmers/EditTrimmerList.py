# trimmer_maint.py
# GUI to maintain trimmer table: id, TrimmerName, TrimmerStat (Active/Inactive)
# Requires: pip install customtkinter
# Assumes SubSupa.py exposes: get_trimmers(), add_trimmer(trimmer_name, trimmer_stat), update_trimmer(row_id, trimmer_name, trimmer_stat)

import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys
import subprocess

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

# ---- SubSupa integration (expected interface) -------------------------------
# Expected in SubSupa.py:
#   def get_trimmers():
#       # return list[dict]: [{"id": 1, "TrimmerName": "Alice", "TrimmerStat": "Active"}, ...]
#       ...
#   def add_trimmer(trimmer_name: str, trimmer_stat: str) -> dict:
#       # insert and return new row dict (with id)
#       ...
#   def update_trimmer(row_id: int, trimmer_name: str, trimmer_stat: str) -> dict:
#       # update and return updated row dict
#       ...
from SubSupa import GetTrimmers, AddTrimmer, UpdateTrimmer  # <-- adjust if your names differ

# ---- GUI --------------------------------------------------------------------
class TrimmerMaintApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("Trimmer Maintenance")
        self.geometry("700x420")

        # state
        self.selected_id = None
        self.name_var = ctk.StringVar()
        self.stat_var = ctk.StringVar(value="Active")  # default
        self.search_var = ctk.StringVar()

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

        # layout
        self._build_header()
        self._build_table()
        self._build_form()
        self._build_buttons()

        # initial load
        self.refresh_table()

    def _build_header(self):
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=10, pady=(10, 6))

        title_lbl = ctk.CTkLabel(header, text="Trimmer Maintenance", font=("Arial", 18, "bold"))
        title_lbl.pack(side="left")

        # optional quick-filter
        search_entry = ctk.CTkEntry(header, placeholder_text="Filter by name...", textvariable=self.search_var, width=220)
        search_entry.pack(side="right", padx=(6, 0))
        search_entry.bind("<KeyRelease>", lambda _e: self.apply_filter())

    def _build_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=6)

        columns = ("id", "TrimmerName", "TrimmerStat")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("id", text="ID")
        self.tree.heading("TrimmerName", text="Trimmer Name")
        self.tree.heading("TrimmerStat", text="Status")
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("TrimmerName", width=320, anchor="w")
        self.tree.column("TrimmerStat", width=120, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=10, pady=(6, 6))

        # Trimmer Name
        name_lbl = ctk.CTkLabel(form, text="Trimmer Name:")
        name_lbl.grid(row=0, column=0, sticky="e", padx=(6, 6), pady=6)
        name_entry = ctk.CTkEntry(form, textvariable=self.name_var, width=320)
        name_entry.grid(row=0, column=1, sticky="w", padx=(0, 18), pady=6)

        # Trimmer Status
        stat_lbl = ctk.CTkLabel(form, text="Status:")
        stat_lbl.grid(row=0, column=2, sticky="e", padx=(6, 6), pady=6)
        self.stat_menu = ctk.CTkOptionMenu(form, values=["Active", "Inactive"], variable=self.stat_var, width=160)
        self.stat_menu.grid(row=0, column=3, sticky="w", padx=(0, 6), pady=6)

        # Selected ID (read-only display)
        self.id_label = ctk.CTkLabel(form, text="ID: —")
        self.id_label.grid(row=0, column=4, sticky="w", padx=(12, 6), pady=6)

        # make columns stretch nicely
        form.grid_columnconfigure(1, weight=1)

    def _build_buttons(self):
        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=10, pady=(0, 10))

        add_btn = ctk.CTkButton(btns, text="Add New", command=self.on_add, width=110)
        add_btn.pack(side="left")

        save_btn = ctk.CTkButton(btns, text="Save Changes", command=self.on_save, width=130)
        save_btn.pack(side="left", padx=(8, 0))

        clear_btn = ctk.CTkButton(btns, text="Clear Form", command=self.clear_form, width=110)
        clear_btn.pack(side="left", padx=(8, 0))

        refresh_btn = ctk.CTkButton(btns, text="Refresh", command=self.refresh_table, width=100)
        refresh_btn.pack(side="right")

        close_btn = ctk.CTkButton(btns, text="Close", command=self.destroy, width=100)
        close_btn.pack(side="right", padx=(0, 8))

    # --- data ops -------------------------------------------------------------

    def refresh_table(self):
        """Reload rows from DB into tree."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            rows = GetTrimmers()  # <-- SubSupa call
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to load trimmers:\n{ex}")
            return

        # Expecting keys: id, TrimmerName, TrimmerStat
        for row in rows or []:
            row_id = row.get("id")
            name = row.get("TrimmerName") or ""
            stat = row.get("TrimmerStat") or ""
            self.tree.insert("", "end", iid=str(row_id), values=(row_id, name, stat))

        self.apply_filter()

    def apply_filter(self):
        """Filter visible rows by name substring (case-insensitive)."""
        filter_text = (self.search_var.get() or "").strip().lower()
        for iid in self.tree.get_children():
            values = self.tree.item(iid, "values")
            name = (values[1] or "").lower()
            # Treeview doesn't support hide/show; rebuild quickly by simple rule:
            # We'll delete non-matching and re-insert on demand if filter cleared.
            # For simplicity here, just gray out non-matching (disabled look).
            # Alternative: rebuild list from cached rows.
            tags = ()
            if filter_text and filter_text not in name:
                tags = ("dim",)
            self.tree.item(iid, tags=tags)
        
        self.tree.tag_configure("dim", foreground="#666666")

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.stat_var.set("Active")
        self.id_label.configure(text="ID: —")
        self.tree.selection_remove(self.tree.selection())

    def on_row_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        values = self.tree.item(iid, "values")
        # values: (id, TrimmerName, TrimmerStat)
        self.selected_id = int(values[0])
        self.name_var.set(values[1])
        self.stat_var.set(values[2] if values[2] in ("Active", "Inactive") else "Active")
        self.id_label.configure(text=f"ID: {self.selected_id}")

    def on_add(self):
        trimmer_name = (self.name_var.get() or "").strip()
        trimmer_stat = self.stat_var.get() or "Active"

        if not trimmer_name:
            messagebox.showwarning("Missing Name", "Please enter a trimmer name.")
            return
        if trimmer_stat not in ("Active", "Inactive"):
            messagebox.showwarning("Invalid Status", "Status must be Active or Inactive.")
            return

        try:
            new_row = AddTrimmer(trimmer_name, trimmer_stat)  # <-- SubSupa call
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to add trimmer:\n{ex}")
            return

        # If API returns new row with id, insert; else refresh
        if isinstance(new_row, dict) and "id" in new_row:
            self.tree.insert(
                "",
                "end",
                iid=str(new_row["id"]),
                values=(new_row["id"], new_row.get("TrimmerName", trimmer_name), new_row.get("TrimmerStat", trimmer_stat)),
            )
        else:
            self.refresh_table()

        self.clear_form()
        messagebox.showinfo("Added", "New trimmer added.")

    def on_save(self):
        if self.selected_id is None:
            messagebox.showwarning("No Row Selected", "Select a row to edit, or use Add New.")
            return

        trimmer_name = (self.name_var.get() or "").strip()
        trimmer_stat = self.stat_var.get() or "Active"

        if not trimmer_name:
            messagebox.showwarning("Missing Name", "Please enter a trimmer name.")
            return
        if trimmer_stat not in ("Active", "Inactive"):
            messagebox.showwarning("Invalid Status", "Status must be Active or Inactive.")
            return

        try:
            updated = UpdateTrimmer(self.selected_id, trimmer_name, trimmer_stat)  # <-- SubSupa call
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to save changes:\n{ex}")
            return

        # Update the tree row
        self.tree.item(str(self.selected_id), values=(self.selected_id, trimmer_name, trimmer_stat))
        messagebox.showinfo("Saved", "Changes saved.")

if __name__ == "__main__":
    app = TrimmerMaintApp()
    app.mainloop()
    restart_menu()
