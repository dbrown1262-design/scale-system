"""ViewSupplies - View and Filter Supply Orders

Allows users to:
- Filter supply orders by Vendor, Department, and Order Status
- View orders in a treeview
- Update receive date for orders
- Print current selection
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import SubSupa
import os
import sys
import subprocess
import tempfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "View Supply Orders"
DEFAULT_FONT = ("Arial", 14)


class ViewSuppliesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("1100x700")
        
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
        self.VendorCombo = ctk.CTkComboBox(filter_frame, values=[], width=180, font=DEFAULT_FONT, command=self.on_filter_changed)
        self.VendorCombo.pack(side="left", padx=(0,16))
        
        ctk.CTkLabel(filter_frame, text="Dept:", font=DEFAULT_FONT).pack(side="left", padx=(6,6))
        self.DeptCombo = ctk.CTkComboBox(filter_frame, values=[], width=150, font=DEFAULT_FONT, command=self.on_filter_changed)
        self.DeptCombo.pack(side="left", padx=(0,16))
        
        ctk.CTkLabel(filter_frame, text="Status:", font=DEFAULT_FONT).pack(side="left", padx=(6,6))
        self.StatusCombo = ctk.CTkComboBox(filter_frame, values=["All", "Pending", "Completed"], width=120, font=DEFAULT_FONT, command=self.on_filter_changed)
        self.StatusCombo.pack(side="left", padx=(0,16))
        self.StatusCombo.set("All")
        
        ctk.CTkButton(filter_frame, text="Refresh", width=100, font=DEFAULT_FONT, command=self.load_orders).pack(side="left", padx=(0,8))

        # Row 1: Treeview with orders
        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(8,8))
        
        cols = ("OrderID", "Vendor", "Dept", "Description", "Size", "Qty", "OrderDate", "ReceiveDate")
        self.Tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        
        self.Tree.heading("OrderID", text="Order ID")
        self.Tree.heading("Vendor", text="Vendor")
        self.Tree.heading("Dept", text="Dept")
        self.Tree.heading("Description", text="Description")
        self.Tree.heading("Size", text="Size")
        self.Tree.heading("Qty", text="Qty")
        self.Tree.heading("OrderDate", text="Order Date")
        self.Tree.heading("ReceiveDate", text="Receive Date")
        
        self.Tree.column("OrderID", width=80, anchor="center")
        self.Tree.column("Vendor", width=140, anchor="w")
        self.Tree.column("Dept", width=100, anchor="w")
        self.Tree.column("Description", width=250, anchor="w")
        self.Tree.column("Size", width=120, anchor="w")
        self.Tree.column("Qty", width=60, anchor="center")
        self.Tree.column("OrderDate", width=100, anchor="center")
        self.Tree.column("ReceiveDate", width=100, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=scrollbar.set)
        
        self.Tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.Tree.bind("<<TreeviewSelect>>", self.on_order_selected)

        # Row 2: Update Receive Date Section
        update_frame = ctk.CTkFrame(frame)
        update_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8,8), padx=8)
        
        ctk.CTkLabel(update_frame, text="Update Receive Date", font=("Arial", 16, "bold")).pack(pady=(8,12))
        
        update_grid = ctk.CTkFrame(update_frame, fg_color="transparent")
        update_grid.pack(fill="x", padx=12, pady=(0,12))
        
        # Order ID (read-only)
        ctk.CTkLabel(update_grid, text="Order ID:", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6), pady=6)
        self.UpdateOrderIDLabel = ctk.CTkLabel(update_grid, text="", font=DEFAULT_FONT, anchor="w", width=200)
        self.UpdateOrderIDLabel.grid(row=0, column=1, sticky="w", pady=6)
        
        # Description (read-only)
        ctk.CTkLabel(update_grid, text="Description:", font=DEFAULT_FONT).grid(row=0, column=2, sticky="e", padx=(16,6), pady=6)
        self.UpdateDescrLabel = ctk.CTkLabel(update_grid, text="", font=DEFAULT_FONT, anchor="w", width=300)
        self.UpdateDescrLabel.grid(row=0, column=3, sticky="w", pady=6)
        
        # Receive Date (editable)
        ctk.CTkLabel(update_grid, text="Receive Date:", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6), pady=6)
        
        date_container = ctk.CTkFrame(update_grid, fg_color="transparent")
        date_container.grid(row=1, column=1, sticky="w", pady=6)
        
        self.ReceiveDateEntry = DateEntry(date_container, width=22, font=("Arial", 14), date_pattern='yyyy-mm-dd',
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
        self.ReceiveDateEntry.pack(side="left")
        # Additional styling for the entry widget inside DateEntry
        try:
            self.ReceiveDateEntry.entry.configure(bg='#343638', fg='#DCE4EE', insertbackground='#DCE4EE')
        except Exception:
            pass
        
        # Update button
        ctk.CTkButton(update_grid, text="Update Order", font=DEFAULT_FONT, command=self.update_receive_date, width=140).grid(row=1, column=2, columnspan=2, sticky="w", padx=(16,0), pady=6)

        # Row 3: Bottom Buttons and Status
        bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(8,0))
        
        button_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_row.pack(side="left")
        
        ctk.CTkButton(button_row, text="Print", font=DEFAULT_FONT, command=self.print_orders, width=100).pack(side="left", padx=(0,8))
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self._on_close, width=100).pack(side="left", padx=(0,8))
        
        self.StatusLabel = ctk.CTkLabel(bottom_frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.pack(side="left", padx=(16,0))

        # Configure grid weights
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # Track selected order
        self.selected_order_id = None

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
            self.load_orders()
        except Exception as e:
            self.set_status(f"Load failed: {e}")

    def on_filter_changed(self, choice=None):
        """Handle filter changes"""
        self.load_orders()

    def on_order_selected(self, event):
        """Handle order selection in treeview"""
        selection = self.Tree.selection()
        if not selection:
            return
        
        # Get selected item values
        item = self.Tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 8:
            self.selected_order_id = values[0]
            descr = values[3]
            size = values[4]
            current_receive_date = values[7]
            
            # Update labels
            self.UpdateOrderIDLabel.configure(text=str(self.selected_order_id))
            self.UpdateDescrLabel.configure(text=f"{descr} - {size}")
            
            # Set date if already received
            if current_receive_date:
                try:
                    # Parse the date and set it in the DateEntry
                    date_obj = datetime.strptime(str(current_receive_date), '%Y-%m-%d')
                    self.ReceiveDateEntry.set_date(date_obj)
                except:
                    # If parsing fails, set to today
                    self.ReceiveDateEntry.set_date(datetime.now())
            else:
                # Set to today for new entries
                self.ReceiveDateEntry.set_date(datetime.now())
            
            self.set_status(f"Selected Order ID: {self.selected_order_id}")

    def update_receive_date(self):
        """Update the receive date for the selected order"""
        if not self.selected_order_id:
            messagebox.showwarning("No Selection", "Please select an order from the list")
            return
        
        receive_date = self.ReceiveDateEntry.get_date().strftime('%Y-%m-%d')
        
        try:
            SubSupa.UpdateOrder(self.selected_order_id, receive_date)
            self.set_status(f"Order {self.selected_order_id} updated with receive date: {receive_date}")
            messagebox.showinfo("Success", f"Order {self.selected_order_id} updated successfully")
            
            # Reload orders to show the update
            self.load_orders()
            
            # Clear selection
            self.UpdateOrderIDLabel.configure(text="")
            self.UpdateDescrLabel.configure(text="")
            self.selected_order_id = None
        except Exception as e:
            self.set_status(f"Update failed: {e}")
            messagebox.showerror("Update Error", f"Failed to update order: {e}")

    def load_orders(self):
        """Load orders based on filter selections"""
        vendor = self.VendorCombo.get().strip()
        dept = self.DeptCombo.get().strip()
        status = self.StatusCombo.get().strip()
        
        try:
            # Clear treeview
            for iid in self.Tree.get_children():
                self.Tree.delete(iid)
            
            # Get orders using SubSupa function
            orders = SubSupa.ViewSupplies(vendor, dept, status)
            
            # Populate treeview
            for order in orders:
                order_id = order.get("id", "")
                vendor_name = order.get("VendorName", "")
                dept_name = order.get("Dept", "")
                descr = order.get("Descr", "")
                size = order.get("Size", "")
                qty = order.get("Qty", "")
                order_date = order.get("OrderDate", "")
                receive_date = order.get("ReceiveDate", "") or ""
                
                self.Tree.insert('', 'end', values=(order_id, vendor_name, dept_name, descr, size, qty, order_date, receive_date))
            
            row_count = len(orders)
            self.set_status(f"Loaded {row_count} orders")
        except Exception as e:
            self.set_status(f"Load orders failed: {e}")
            messagebox.showerror("Load Error", f"Failed to load orders: {e}")

    def print_orders(self):
        """Print current order selection to PDF and send to printer"""
        try:
            # Get all rows from treeview
            rows = []
            for item in self.Tree.get_children():
                values = self.Tree.item(item)['values']
                rows.append(values)
            
            if not rows:
                messagebox.showinfo("No Data", "No orders to print")
                return
            
            # Create PDF
            tmpdir = tempfile.gettempdir()
            pdf_path = os.path.join(tmpdir, "supply_orders_report.pdf")
            
            # Use landscape LETTER for wider table
            doc = SimpleDocTemplate(pdf_path, pagesize=landscape(LETTER), 
                                   leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph("Supply Orders Report", styles["Title"]))
            story.append(Spacer(1, 0.1 * inch))
            
            # Date and filter information
            vendor = self.VendorCombo.get()
            dept = self.DeptCombo.get()
            status = self.StatusCombo.get()
            
            filter_text = f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            filter_text += f"<b>Vendor:</b> {vendor} | <b>Dept:</b> {dept} | <b>Status:</b> {status}"
            story.append(Paragraph(filter_text, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))
            
            # Build table data
            header = ["Order ID", "Vendor", "Dept", "Description", "Size", "Qty", "Order Date", "Receive Date"]
            table_data = [header]
            
            for row in rows:
                table_data.append([
                    str(row[0]),
                    str(row[1]),
                    str(row[2]),
                    str(row[3]),
                    str(row[4]),
                    str(row[5]),
                    str(row[6]),
                    str(row[7]) if row[7] else ""
                ])
            
            # Create table
            tbl = Table(table_data, hAlign="LEFT")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.grey),
                ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,0), 10),
                ("FONTSIZE", (0,1), (-1,-1), 9),
                ("ALIGN", (0,0), (-1,0), "CENTER"),
                ("ALIGN", (0,1), (0,-1), "CENTER"),  # Order ID center
                ("ALIGN", (5,1), (5,-1), "CENTER"),  # Qty center
                ("ALIGN", (6,1), (7,-1), "CENTER"),  # Dates center
                ("ALIGN", (1,1), (4,-1), "LEFT"),    # Other fields left
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 0.2 * inch))
            
            # Summary
            summary_text = f"<b>Total Orders:</b> {len(rows)}"
            story.append(Paragraph(summary_text, styles["Normal"]))
            
            # Build PDF
            doc.build(story)
            
            # Print the PDF
            self._print_file(pdf_path)
            
            self.set_status(f"Printed {len(rows)} orders to PDF: {pdf_path}")
            messagebox.showinfo("Print Complete", f"Report created and sent to printer:\n{pdf_path}")
        except Exception as e:
            self.set_status(f"Print failed: {e}")
            messagebox.showerror("Print Error", f"Failed to print orders: {e}")

    def _print_file(self, path):
        """Send PDF to printer"""
        if sys.platform.startswith("win"):
            try:
                os.startfile(path, "print")
            except OSError:
                # If printing fails, just open the file
                os.startfile(path)
        else:
            try:
                subprocess.run(["lpr", path], check=False)
            except FileNotFoundError:
                # If lpr not available, try to open
                if sys.platform == "darwin":
                    subprocess.run(["open", path], check=False)
                else:
                    subprocess.run(["xdg-open", path], check=False)

    def _on_close(self):
        """Handle window close event"""
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = ViewSuppliesApp()
    app.mainloop()
    restart_menu()
