"""EditMetrcType - Edit Metrc Tag Types

Allows users to:
- View all Metrc tag types in a treeview
- Add new Metrc tag types with scanned or manually entered IDs
- Update existing Metrc tag types
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from pathlib import Path
import SubSupa
import os
import sys
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # this is the "scale" folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
import Common.SubReadQRCode as SubReadQRCode

# Connect scanner
ScannerConnected = SubReadQRCode.ConnectScanner()
print(ScannerConnected)
# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

def launch_sop():
    # EditMetrcType.py is in scale/Harvest/
    this_file = Path(__file__).resolve()
    scale_root = this_file.parents[1]  # .../scale
    sop_md = scale_root / "sop" / "Harvest" / "EditMetrcType.md"
    viewer_py = scale_root / "common" / "SopViewer.py"

    # Launch separate process (non-blocking)
    if sop_md.exists():
        subprocess.Popen(
            [sys.executable, str(viewer_py), str(sop_md)],
            cwd=str(scale_root),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
        )

APP_TITLE = "Edit Metrc Tag Types"
DEFAULT_FONT = ("Arial", 14)
POLL_INTERVAL_MS = 500


class EditMetrcTypeApp(ctk.CTk):
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
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("700x550")

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

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Header
        header_label = ctk.CTkLabel(frame, text="Metrc Tag Type Management", font=("Arial", 16, "bold"))
        header_label.grid(row=0, column=0, columnspan=4, pady=(0, 12))

        # Input fields
        ctk.CTkLabel(frame, text="Metrc ID", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6))
        self.MetrcIdEntry = ctk.CTkEntry(frame, width=280, font=DEFAULT_FONT)
        self.MetrcIdEntry.grid(row=1, column=1, columnspan=2, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Type", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6))
        self.TypeCombo = ctk.CTkComboBox(frame, values=["Select", "Dist", "Proc", "Cult", "Plant"], 
                                         width=280, font=DEFAULT_FONT)
        self.TypeCombo.grid(row=2, column=1, columnspan=2, sticky="w", pady=6)
        self.TypeCombo.set("Select")

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(12,0))
        
        self.BtnAdd = ctk.CTkButton(button_frame, text="Add", font=DEFAULT_FONT, command=self.add_type)
        self.BtnAdd.pack(side="left", padx=(0,8))
        
        self.BtnUpdate = ctk.CTkButton(button_frame, text="Update", font=DEFAULT_FONT, command=self.update_type)
        self.BtnUpdate.pack(side="left", padx=(0,8))
        
        self.BtnRefresh = ctk.CTkButton(button_frame, text="Refresh", font=DEFAULT_FONT, command=self.load_types)
        self.BtnRefresh.pack(side="left", padx=(0,8))
        
        self.BtnClear = ctk.CTkButton(button_frame, text="Clear", font=DEFAULT_FONT, command=self.clear_fields)
        self.BtnClear.pack(side="left", padx=(0,8))
        
        ctk.CTkButton(button_frame, text="Close", font=DEFAULT_FONT, command=self._on_close).pack(side="left", padx=(0,8))

        # Treeview for displaying tag types
        ctk.CTkLabel(frame, text="Tag Types", font=DEFAULT_FONT).grid(row=4, column=0, sticky="nw", padx=(6,6), pady=(12,0))
        
        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.grid(row=4, column=1, columnspan=3, sticky="nsew", pady=(12,0))
        
        self.Tree = ttk.Treeview(tree_frame, columns=("MetrcId", "Type"), show="headings", height=15)
        self.Tree.heading("MetrcId", text="Metrc ID")
        self.Tree.heading("Type", text="Type")
        self.Tree.column("MetrcId", width=400, anchor="w")
        self.Tree.column("Type", width=150, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=scrollbar.set)
        
        self.Tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.Tree.bind('<<TreeviewSelect>>', lambda e: self.on_tree_select())

        # Configure grid weights
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Status Label
        self.StatusLabel = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.grid(row=5, column=0, columnspan=4, sticky="w", pady=(8,0))

        # Track selected item
        self.selected_metrc_id = None

        # Check QR status initially
        self.check_qr_status()

        # Load initial data
        self.load_types()

        # Start polling for QR codes
        self._poll_id = None
        self._prev_qr_status = None
        self._status_check_counter = 0
        self.start_polling()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def set_status(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def check_qr_status(self):
        """Check if QR reader is connected and update status label."""
        try:
            if ScannerConnected and hasattr(SubReadQRCode, 'QrReader') and SubReadQRCode.QrReader:
                self.QrStatusLabel.configure(text="QR: Connected", text_color="#00aa00")
            else:
                self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
        except Exception:
            self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")

    def load_types(self):
        """Load all Metrc tag types into the treeview"""
        try:
            # Clear existing items
            for item in self.Tree.get_children():
                self.Tree.delete(item)
            
            # Load data from database
            types = SubSupa.LoadMetrcTypes()
            
            # Populate treeview
            for idx, row in enumerate(types):
                metrc_id = row.get("MetrcId", "")
                metrc_type = row.get("MetrcType", "")
                self.Tree.insert("", "end", values=(metrc_id, metrc_type))
            
            self.set_status(f"Loaded {len(types)} tag types")
        except Exception as e:
            self.set_status(f"Load failed: {e}")
            messagebox.showerror("Load Error", f"Failed to load tag types: {e}")

    def on_tree_select(self):
        """Handle treeview row selection"""
        try:
            selection = self.Tree.selection()
            if selection:
                item = self.Tree.item(selection[0])
                values = item['values']
                if values:
                    metrc_id = values[0]
                    metrc_type = values[1]
                    
                    self.selected_metrc_id = metrc_id
                    
                    # Populate fields
                    self.MetrcIdEntry.delete(0, 'end')
                    self.MetrcIdEntry.insert(0, metrc_id)
                    self.TypeCombo.set(metrc_type)
                    
                    self.set_status(f"Selected: {metrc_id}")
        except Exception as e:
            self.set_status(f"Selection error: {e}")

    def clear_fields(self):
        """Clear all input fields"""
        self.MetrcIdEntry.delete(0, 'end')
        self.TypeCombo.set("Select")
        self.selected_metrc_id = None
        self.set_status("Fields cleared")

    def add_type(self):
        """Add a new Metrc tag type"""
        metrc_id = self.MetrcIdEntry.get().strip()
#        metrc_id = metrc[:-9]
        metrc_type = self.TypeCombo.get().strip()
        
        if not metrc_id:
            messagebox.showwarning("Missing ID", "Please scan or enter a Metrc ID")
            return
        
        if not metrc_type or metrc_type == "Select":
            messagebox.showwarning("Missing Type", "Please select a type")
            return
        
        try:
            SubSupa.InsertMetrcType(metrc_id, metrc_type)
            self.set_status(f"Added: {metrc_id} as {metrc_type}")
            self.load_types()  # Refresh the list
            self.clear_fields()
        except Exception as e:
            self.set_status(f"Add failed: {e}")
            messagebox.showerror("Add Error", f"Failed to add tag type: {e}")

    def update_type(self):
        """Update existing Metrc tag type"""
        if not self.selected_metrc_id:
            messagebox.showwarning("No Selection", "Please select a tag type from the list")
            return
        
        metrc_type = self.TypeCombo.get().strip()
        
        if not metrc_type or metrc_type == "Select":
            messagebox.showwarning("Missing Type", "Please select a type")
            return
        
        try:
            SubSupa.UpdateMetrcType(self.selected_metrc_id, metrc_type)
            self.set_status(f"Updated: {self.selected_metrc_id} to {metrc_type}")
            self.load_types()  # Refresh the list
            self.clear_fields()
        except Exception as e:
            self.set_status(f"Update failed: {e}")
            messagebox.showerror("Update Error", f"Failed to update tag type: {e}")

    # ---- Polling ----
    def start_polling(self):
        self.poll_qr()

    def poll_qr(self):
        """Poll for QR codes if scanner is connected"""
        if ScannerConnected:
            try:
                if hasattr(SubReadQRCode, 'QrReader'):
                    qr_code, tag_type = SubReadQRCode.CheckMetricQr()
                    if qr_code and qr_code != "none":
                        # Update MetrcId entry
                        metrc_id = qr_code[:-9]
                        self.MetrcIdEntry.delete(0, 'end')
                        self.MetrcIdEntry.insert(0, metrc_id)
                        self.set_status(f"Scanned: {qr_code}")
            except Exception:
                pass
        
        # Periodically check QR status (every 20 polls = ~10 seconds)
        self._status_check_counter += 1
        if self._status_check_counter >= 20:
            self._status_check_counter = 0
            try:
                qr_available = ScannerConnected and hasattr(SubReadQRCode, 'QrReader') and SubReadQRCode.QrReader is not None
                if qr_available != self._prev_qr_status:
                    self._prev_qr_status = qr_available
                    if qr_available:
                        self.QrStatusLabel.configure(text="QR: Connected", text_color="#00aa00")
                    else:
                        self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
            except Exception:
                if self._prev_qr_status is not False:
                    self._prev_qr_status = False
                    self.QrStatusLabel.configure(text="QR: Not Found", text_color="#ff4444")
        
        try:
            self._poll_id = self.after(POLL_INTERVAL_MS, self.poll_qr)
        except Exception:
            self._poll_id = None

    def stop_polling(self):
        try:
            if self._poll_id:
                self.after_cancel(self._poll_id)
                self._poll_id = None
        except Exception:
            pass

    def _on_close(self):
        """Handle window close event"""
        try:
            self.stop_polling()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = EditMetrcTypeApp()
    app.mainloop()
    restart_menu()
