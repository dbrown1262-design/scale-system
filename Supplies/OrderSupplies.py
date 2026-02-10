"""OrderSupplies - Order Supplies from Vendors

Allows users to:
- Filter supplies by Vendor and/or Department
- View available supplies in a treeview
- Select a supply item and enter order quantity
- Create orders with today's date by default
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
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

APP_TITLE = "Order Supplies"
DEFAULT_FONT = ("Arial", 14)


class OrderSuppliesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("900x700")
        
        # Configure treeview style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="#dce4ee",
                       fieldbackground="#2b2b2b",
                       font=("Arial", 14),
                       rowheight=28)
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="#ffffff",
                       font=("Arial", 14, "bold"))
        style.map("Treeview",
                 background=[("selected", "#144870")])

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Row 0: Filter Section
        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0,8))
        
        ctk.CTkLabel(filter_frame, text="Vendor:", font=DEFAULT_FONT).pack(side="left", padx=(6,6))
        self.VendorCombo = ctk.CTkComboBox(filter_frame, values=[], width=200, font=DEFAULT_FONT, command=self.on_filter_changed)
        self.VendorCombo.pack(side="left", padx=(0,16))
        
        ctk.CTkLabel(filter_frame, text="Dept:", font=DEFAULT_FONT).pack(side="left", padx=(6,6))
        self.DeptCombo = ctk.CTkComboBox(filter_frame, values=[], width=200, font=DEFAULT_FONT, command=self.on_filter_changed)
        self.DeptCombo.pack(side="left", padx=(0,16))
        
        ctk.CTkButton(filter_frame, text="Refresh", width=100, font=DEFAULT_FONT, command=self.load_supplies).pack(side="left", padx=(0,8))

        # Row 1: Treeview with supplies
        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(8,8))
        
        cols = ("Vendor", "Dept", "Description", "Size")
        self.Tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        
        self.Tree.heading("Vendor", text="Vendor")
        self.Tree.heading("Dept", text="Dept")
        self.Tree.heading("Description", text="Description")
        self.Tree.heading("Size", text="Size")
        
        self.Tree.column("Vendor", width=150, anchor="w")
        self.Tree.column("Dept", width=120, anchor="w")
        self.Tree.column("Description", width=300, anchor="w")
        self.Tree.column("Size", width=150, anchor="w")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=scrollbar.set)
        
        self.Tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.Tree.bind("<<TreeviewSelect>>", self.on_supply_selected)

        # Row 2: Order Details Section
        order_frame = ctk.CTkFrame(frame)
        order_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8,8), padx=8)
        
        ctk.CTkLabel(order_frame, text="Order Details", font=("Arial", 16, "bold")).pack(pady=(8,12))
        
        details_grid = ctk.CTkFrame(order_frame, fg_color="transparent")
        details_grid.pack(fill="x", padx=12, pady=(0,12))
        
        # Vendor (read-only)
        ctk.CTkLabel(details_grid, text="Vendor:", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6), pady=6)
        self.OrderVendorLabel = ctk.CTkLabel(details_grid, text="", font=DEFAULT_FONT, anchor="w", width=280)
        self.OrderVendorLabel.grid(row=0, column=1, sticky="w", pady=6)
        
        # Description (read-only)
        ctk.CTkLabel(details_grid, text="Description:", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6), pady=6)
        self.OrderDescrLabel = ctk.CTkLabel(details_grid, text="", font=DEFAULT_FONT, anchor="w", width=280)
        self.OrderDescrLabel.grid(row=1, column=1, sticky="w", pady=6)
        
        # Size (read-only)
        ctk.CTkLabel(details_grid, text="Size:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6), pady=6)
        self.OrderSizeLabel = ctk.CTkLabel(details_grid, text="", font=DEFAULT_FONT, anchor="w", width=280)
        self.OrderSizeLabel.grid(row=2, column=1, sticky="w", pady=6)
        
        # Quantity (editable)
        ctk.CTkLabel(details_grid, text="Quantity:", font=DEFAULT_FONT).grid(row=3, column=0, sticky="e", padx=(6,6), pady=6)
        self.QtyEntry = ctk.CTkEntry(details_grid, width=280, font=DEFAULT_FONT)
        self.QtyEntry.grid(row=3, column=1, sticky="w", pady=6)
        
        # Order Date (editable, defaults to today)
        ctk.CTkLabel(details_grid, text="Order Date:", font=DEFAULT_FONT).grid(row=4, column=0, sticky="e", padx=(6,6), pady=6)
        
        date_container = ctk.CTkFrame(details_grid, fg_color="transparent")
        date_container.grid(row=4, column=1, sticky="w", pady=6)
        
        self.OrderDateEntry = DateEntry(date_container, width=25, font=("Arial", 14), date_pattern='yyyy-mm-dd',
                                        background='darkblue', foreground='white', 
                                        fieldbackground='#343638', 
                                        borderwidth=2,
                                        headersbackground='darkblue',
                                        headersforeground='white',
                                        selectbackground='darkblue',
                                        selectforeground='white',
                                        normalbackground='white',
                                        normalforeground='black',
                                        weekendbackground='white',
                                        weekendforeground='black',
                                        state='normal')
        self.OrderDateEntry.pack(side="left")
        # Additional styling for the entry widget inside DateEntry
        try:
            self.OrderDateEntry.entry.configure(bg='#343638', fg='#DCE4EE', insertbackground='#DCE4EE')
        except Exception:
            pass
        
        # Save button
        button_container = ctk.CTkFrame(order_frame, fg_color="transparent")
        button_container.pack(pady=(0,8))
        ctk.CTkButton(button_container, text="Save Order", font=DEFAULT_FONT, command=self.save_order).pack(padx=8)

        # Row 3: Status and Close
        bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(8,0))
        
        self.StatusLabel = ctk.CTkLabel(bottom_frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.pack(side="left", padx=(4,8))
        
        ctk.CTkButton(bottom_frame, text="Close", command=self._on_close, width=100, font=DEFAULT_FONT).pack(side="right", padx=(6,0))

        # Configure grid weights
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # Track selected supply
        self.selected_vendor = None
        self.selected_descr = None
        self.selected_size = None

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
            
            # Add "Any" option
            vendors_with_any = ["Any"] + [v for v in vendors if v != "Select"]
            depts_with_any = ["Any"] + [d for d in depts if d != "Select"]
            
            if vendors_with_any:
                self.VendorCombo.configure(values=vendors_with_any)
                self.VendorCombo.set("Any")
            
            if depts_with_any:
                self.DeptCombo.configure(values=depts_with_any)
                self.DeptCombo.set("Any")
            
            self.set_status("Data loaded successfully")
            self.load_supplies()
        except Exception as e:
            self.set_status(f"Load failed: {e}")

    def on_filter_changed(self, choice=None):
        """Handle filter changes"""
        self.load_supplies()

    def load_supplies(self):
        """Load supplies based on filter selections"""
        vendor = self.VendorCombo.get().strip()
        dept = self.DeptCombo.get().strip()
        
        # Convert "Any" to "Select" for the SubSupa function
        vendor_filter = "Select" if vendor == "Any" else vendor
        dept_filter = "Select" if dept == "Any" else dept
        
        try:
            # Clear treeview
            for iid in self.Tree.get_children():
                self.Tree.delete(iid)
            
            supplies = SubSupa.GetSupplies(vendor_filter, dept_filter)
            
            # Populate treeview
            for supply in supplies:
                vendor_name = supply.get("Vendor", "")
                dept_name = supply.get("Dept", "")
                descr = supply.get("Descr", "")
                size = supply.get("Size", "")
                
                self.Tree.insert('', 'end', values=(vendor_name, dept_name, descr, size))
            
            self.set_status(f"Loaded {len(supplies)} supplies")
        except Exception as e:
            self.set_status(f"Load supplies failed: {e}")
            messagebox.showerror("Load Error", f"Failed to load supplies: {e}")

    def on_supply_selected(self, event):
        """Handle supply selection in treeview"""
        selection = self.Tree.selection()
        if not selection:
            return
        
        # Get selected item values
        item = self.Tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 4:
            self.selected_vendor = values[0]
            self.selected_descr = values[2]
            self.selected_size = values[3]
            
            # Update labels
            self.OrderVendorLabel.configure(text=self.selected_vendor)
            self.OrderDescrLabel.configure(text=self.selected_descr)
            self.OrderSizeLabel.configure(text=self.selected_size)
            
            # Clear quantity
            self.QtyEntry.delete(0, "end")
            
            self.set_status(f"Selected: {self.selected_descr}")

    def save_order(self):
        """Save order to database"""
        if not self.selected_vendor or not self.selected_descr or not self.selected_size:
            messagebox.showwarning("No Selection", "Please select a supply item from the list")
            return
        
        qty_str = self.QtyEntry.get().strip()
        if not qty_str:
            messagebox.showwarning("Missing Quantity", "Please enter a quantity")
            return
        
        try:
            qty = int(qty_str)
            if qty <= 0:
                messagebox.showwarning("Invalid Quantity", "Quantity must be greater than 0")
                return
        except ValueError:
            messagebox.showwarning("Invalid Quantity", "Please enter a valid integer quantity")
            return
        
        order_date = self.OrderDateEntry.get_date().strftime('%Y-%m-%d')
        
        try:
            SubSupa.InsertOrder(self.selected_vendor, self.selected_descr, self.selected_size, qty, order_date)
            self.set_status(f"Order saved: {qty} x {self.selected_descr}")
            messagebox.showinfo("Success", f"Order created:\n{qty} x {self.selected_descr} from {self.selected_vendor}")
            
            # Clear order details
            self.QtyEntry.delete(0, "end")
            self.OrderVendorLabel.configure(text="")
            self.OrderDescrLabel.configure(text="")
            self.OrderSizeLabel.configure(text="")
            self.selected_vendor = None
            self.selected_descr = None
            self.selected_size = None
            
            # Clear treeview selection
            self.Tree.selection_remove(self.Tree.selection())
            
        except Exception as e:
            self.set_status(f"Save failed: {e}")
            messagebox.showerror("Save Error", f"Failed to save order: {e}")

    def _on_close(self):
        """Handle window close event"""
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = OrderSuppliesApp()
    app.mainloop()
    restart_menu()
