"""EditSopIndex - Editor for SOP index table

Shows a Treeview of SOP files for a selected activity and allows editing
descriptions and sequence numbers via SubSopSupa.UpdateSopIndex.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import SubSopSupa
import os
import sys
import subprocess

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "Menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "Edit SOP Index"
DEFAULT_FONT = ("Arial", 15)


class EditSopIndexApp(ctk.CTk):
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

        # Activity selector
        activity_frame = ctk.CTkFrame(frame, fg_color="transparent")
        activity_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        
        ctk.CTkLabel(activity_frame, text="Activity:", font=("Arial", 15, "bold")).pack(side="left", padx=(0, 6))
        
        # Load activities from database
        try:
            activities = SubSopSupa.GetSopActivities()
        except Exception as e:
            activities = []
            
        self.activity_var = ctk.StringVar(value=activities[0] if activities else "")
        self.activity_combo = ctk.CTkComboBox(
            activity_frame, 
            values=activities if activities else ["No activities found"],
            variable=self.activity_var,
            font=DEFAULT_FONT,
            width=200,
            command=self.on_activity_change
        )
        self.activity_combo.pack(side="left", padx=6)

        # Treeview
        ctk.CTkLabel(frame, text="SOP Files", font=("Arial", 15, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 6))
        cols = ("FileName", "SeqNo", "Descr")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        self.tree.heading("FileName", text="File Name")
        self.tree.heading("SeqNo", text="Seq #")
        self.tree.heading("Descr", text="Description")
        self.tree.column("FileName", width=250, anchor="w")
        self.tree.column("SeqNo", width=80, anchor="center")
        self.tree.column("Descr", width=500, anchor="w")
        self.tree.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(6,12))
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.on_tree_select())

        # Form fields
        ctk.CTkLabel(frame, text="File Name:", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(0, 6))
        self.ent_file = ctk.CTkEntry(frame, width=250, font=DEFAULT_FONT, state="readonly")
        self.ent_file.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        ctk.CTkLabel(frame, text="Seq #:", font=DEFAULT_FONT).grid(row=3, column=2, sticky="e", padx=(0, 6))
        self.ent_seq = ctk.CTkEntry(frame, width=80, font=DEFAULT_FONT)
        self.ent_seq.grid(row=3, column=3, sticky="w", padx=6, pady=6)

        ctk.CTkLabel(frame, text="Description:", font=DEFAULT_FONT).grid(row=4, column=0, sticky="e", padx=(0, 6))
        self.ent_descr = ctk.CTkEntry(frame, width=630, font=DEFAULT_FONT)
        self.ent_descr.grid(row=4, column=1, columnspan=3, sticky="ew", padx=6, pady=6)

        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=4, pady=(12,0))
        self.btn_save = ctk.CTkButton(btn_frame, text="Save", font=DEFAULT_FONT, command=self.save_row)
        self.btn_refresh = ctk.CTkButton(btn_frame, text="Refresh", font=DEFAULT_FONT, command=self.load_rows)
        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear", font=DEFAULT_FONT, command=self.clear_form)
        self.btn_close = ctk.CTkButton(btn_frame, text="Close", font=DEFAULT_FONT, command=self.destroy)
        self.btn_save.grid(row=0, column=0, padx=6)
        self.btn_refresh.grid(row=0, column=1, padx=6)
        self.btn_clear.grid(row=0, column=2, padx=6)
        self.btn_close.grid(row=0, column=3, padx=6)

        # status
        self.status = ctk.CTkLabel(frame, text="", font=("Arial", 15))
        self.status.grid(row=6, column=0, columnspan=4, sticky="w", pady=(8,0))

        # make tree expand
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(1, weight=1)

        self.selected_file = None
        if activities:
            self.load_rows()

    def set_status(self, text: str):
        try:
            self.status.configure(text=text)
        except Exception:
            pass

    def on_activity_change(self, choice):
        """Called when activity combobox selection changes."""
        self.load_rows()

    def load_rows(self):
        activity = self.activity_var.get()
        if not activity or activity == "No activities found":
            self.set_status("No activity selected")
            return

        try:
            rows = SubSopSupa.GetSopFiles(activity) or []
        except Exception as e:
            self.set_status(f"GetSopFiles failed: {e}")
            rows = []

        # clear
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # GetSopFiles returns list of tuples: (FileName, Descr)
        # We need to get full details including SeqNo
        for filename, descr in rows:
            try:
                record = SubSopSupa.GetOneSopFile(activity, filename)
                if record:
                    seq_no = record.get('SeqNo', 99)
                    file_name = record.get('FileName', filename)
                    description = record.get('Descr', descr)
                    vals = (file_name, str(seq_no), description or '')
                    self.tree.insert('', 'end', values=vals)
            except Exception as e:
                # If GetOneSopFile fails, use what we have
                vals = (filename, '99', descr or '')
                self.tree.insert('', 'end', values=vals)

        self.set_status(f"Loaded {len(rows)} SOP files for {activity}")

    def on_tree_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        vals = self.tree.item(iid, 'values')
        if not vals:
            return

        self.selected_file = vals[0]  # Store filename

        try:
            self.ent_file.configure(state="normal")
            self.ent_file.delete(0, 'end')
            self.ent_seq.delete(0, 'end')
            self.ent_descr.delete(0, 'end')
            
            self.ent_file.insert(0, vals[0])
            self.ent_seq.insert(0, vals[1])
            self.ent_descr.insert(0, vals[2])
            
            self.ent_file.configure(state="readonly")
            self.set_status(f"Selected: {vals[0]}")
        except Exception as e:
            self.set_status(f"Error selecting row: {e}")

    def clear_form(self):
        try:
            self.selected_file = None
            self.ent_file.configure(state="normal")
            self.ent_file.delete(0, 'end')
            self.ent_seq.delete(0, 'end')
            self.ent_descr.delete(0, 'end')
            self.ent_file.configure(state="readonly")
            self.set_status("")
        except Exception:
            pass

    def save_row(self):
        if not self.selected_file:
            messagebox.showwarning("Select Row", "Please select a row to update")
            return
            
        activity = self.activity_var.get()
        if not activity or activity == "No activities found":
            messagebox.showwarning("No Activity", "Please select an activity")
            return

        file_name = self.selected_file
        seq = (self.ent_seq.get() or "").strip()
        descr = (self.ent_descr.get() or "").strip()

        try:
            seq_no = int(seq) if seq else 99
        except Exception:
            messagebox.showwarning("Seq #", "Sequence number must be an integer")
            return

        try:
            SubSopSupa.UpdateSopIndex(activity, file_name, seq_no, descr)
            self.set_status(f"Updated {file_name}")
        except Exception as e:
            self.set_status(f"UpdateSopIndex failed: {e}")
            messagebox.showerror("Update Failed", f"Failed to update: {e}")
            return
        
        self.load_rows()


def main():
    app = EditSopIndexApp()
    app.mainloop()
    restart_menu()


if __name__ == '__main__':
    main()
