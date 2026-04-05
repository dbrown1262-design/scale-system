"""PrintBuckedReport - Generate Metrc Entry Report for Bucked Totes

Generate a report of bucked totes for a date range to facilitate Metrc data entry.
Includes employee signature lines for "Entered By" and "Checked By".
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import tempfile
import os
import sys
import subprocess
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

import SubSupa

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

def launch_sop():
    # PrintBuckedReport.py is in scale/Harvest/
    this_file = Path(__file__).resolve()
    scale_root = this_file.parents[1]  # .../scale
    sop_md = scale_root / "sop" / "Harvest" / "WeighBucked.md"  # Using WeighBucked SOP
    viewer_py = scale_root / "common" / "SopViewer.py"

    # Launch separate process (non-blocking)
    if sop_md.exists():
        subprocess.Popen(
            [sys.executable, str(viewer_py), str(sop_md)],
            cwd=str(scale_root),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
        )

APP_TITLE = "Print Bucked Report"
DEFAULT_FONT = ("Arial", 14)


class PrintBuckedReportApp(ctk.CTk):
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
                       font=("Arial", 16),
                       rowheight=28)
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="#ffffff",
                       font=("Arial", 16, "bold"))
        style.map("Treeview",
                 background=[("selected", "#144870")])

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Filter inputs
        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,8))
        
        ctk.CTkLabel(filter_frame, text="Crop No:", font=DEFAULT_FONT).pack(side="left", padx=(6,6))
        self.CropNoCombo = ctk.CTkComboBox(filter_frame, values=["All"], state="readonly", width=160, font=DEFAULT_FONT)
        self.CropNoCombo.pack(side="left", padx=(0,16))
        self.CropNoCombo.set("All")
        
        ctk.CTkButton(filter_frame, text="Refresh", width=100, font=DEFAULT_FONT, command=self.load_data).pack(side="left", padx=(0,8))
        
        # Load crop list
        self.load_crops()

        # Treeview with tote data
        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(8,8))
        
        cols = ("CropNo", "Strain", "ToteType", "ToteNo", "Weight", "BuckDate")
        self.Tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        
        self.Tree.heading("CropNo", text="Crop No")
        self.Tree.heading("Strain", text="Strain")
        self.Tree.heading("ToteType", text="Tote Type")
        self.Tree.heading("ToteNo", text="Tote No")
        self.Tree.heading("Weight", text="Weight (g)")
        self.Tree.heading("BuckDate", text="Buck Date")
        
        self.Tree.column("CropNo", width=80, anchor="center")
        self.Tree.column("Strain", width=150, anchor="w")
        self.Tree.column("ToteType", width=90, anchor="center")
        self.Tree.column("ToteNo", width=80, anchor="center")
        self.Tree.column("Weight", width=100, anchor="center")
        self.Tree.column("BuckDate", width=120, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=scrollbar.set)
        
        self.Tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom buttons and status
        bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8,0))
        
        button_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_row.pack(side="left")
        
        ctk.CTkButton(button_row, text="Print Report", font=DEFAULT_FONT, command=self.print_report, width=120).pack(side="left", padx=(0,8))
        ctk.CTkButton(button_row, text="Close", font=DEFAULT_FONT, command=self.on_close, width=100).pack(side="left", padx=(0,8))
        
        self.StatusLabel = ctk.CTkLabel(bottom_frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.StatusLabel.pack(side="left", padx=(16,0))

        # Configure grid weights
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        try:
            self.protocol("WM_DELETE_WINDOW", self.on_close)
        except Exception:
            pass

    def set_status(self, text: str):
        try:
            self.StatusLabel.configure(text=text)
        except Exception:
            pass

    def load_crops(self):
        """Load crop numbers into combo box"""
        try:
            crops = SubSupa.LoadCrops() or []
            crop_values = ["All"] + crops
            self.CropNoCombo.configure(values=crop_values)
        except Exception as e:
            self.set_status(f"Load crops failed: {e}")

    def load_data(self):
        """Load tote data based on CropNo"""
        crop_filter = self.CropNoCombo.get().strip()
        
        # Convert crop to number or None
        crop_no = None
        if crop_filter and crop_filter != "All":
            try:
                # Extract crop number from format "123" or "123 - 2024-01-01"
                crop_no = int(crop_filter.split()[0])
            except (ValueError, IndexError):
                pass
        
        try:
            # Clear treeview
            for iid in self.Tree.get_children():
                self.Tree.delete(iid)
            
            # Load data from database
            totes = SubSupa.LoadToteReport(crop_no)
            
            # Populate treeview
            for tote in totes:
                crop_no = tote.get("CropNo", "")
                strain = tote.get("Strain", "")
                tote_type = tote.get("ToteType", "")
                tote_no = tote.get("ToteNo", "")
                weight = tote.get("Weight", "")
                buck_date = tote.get("BuckDate", "")
                
                # Format date if it's a datetime string
                if buck_date and len(buck_date) > 10:
                    buck_date = buck_date[:10]
                
                self.Tree.insert('', 'end', values=(crop_no, strain, tote_type, tote_no, weight, buck_date))
            
            row_count = len(totes)
            filter_desc = f"Crop: {crop_filter}"
            self.set_status(f"Loaded {row_count} totes ({filter_desc})")
        except Exception as e:
            self.set_status(f"Load failed: {e}")
            messagebox.showerror("Load Error", f"Failed to load data: {e}")

    def print_report(self):
        """Generate and print PDF report"""
        try:
            # Get all rows from treeview
            rows = []
            for item in self.Tree.get_children():
                values = self.Tree.item(item)['values']
                rows.append(values)
            
            if not rows:
                messagebox.showinfo("No Data", "No totes to print")
                return
            
            # Get filter info for header
            crop_filter = self.CropNoCombo.get().strip()
            
            # Create PDF
            tmpdir = tempfile.gettempdir()
            pdf_path = os.path.join(tmpdir, "bucked_totes_report.pdf")
            
            doc = SimpleDocTemplate(pdf_path, pagesize=LETTER, 
                                   leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph("Bucked Totes Report - Metrc Entry", styles["Title"]))
            story.append(Spacer(1, 0.1 * inch))
            
            # Filter and report info
            report_info = f"<b>Filter:</b> Crop: {crop_filter} | "
            report_info += f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(report_info, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))
            
            # Build table data
            header = ["Crop No", "Strain", "Tote Type", "Tote No", "Weight (g)", "Buck Date"]
            table_data = [header]
            
            # Group by crop and strain for easier data entry
            for row in rows:
                table_data.append([
                    str(row[0]),
                    str(row[1]),
                    str(row[2]),
                    str(row[3]),
                    str(row[4]),
                    str(row[5])
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
                ("ALIGN", (0,1), (0,-1), "CENTER"),  # Crop No center
                ("ALIGN", (2,1), (2,-1), "CENTER"),  # Tote Type center
                ("ALIGN", (3,1), (3,-1), "CENTER"),  # Tote No center
                ("ALIGN", (4,1), (4,-1), "CENTER"),  # Weight center
                ("ALIGN", (5,1), (5,-1), "CENTER"),  # Buck Date center
                ("ALIGN", (1,1), (1,-1), "LEFT"),    # Strain left
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 0.3 * inch))
            
            # Summary
            summary_text = f"<b>Total Totes:</b> {len(rows)}"
            story.append(Paragraph(summary_text, styles["Normal"]))
            story.append(Spacer(1, 0.4 * inch))
            
            # Employee signature lines
            signature_data = [
                ["Entered By: _______________________________", "Date: _______________"],
                ["", ""],
                ["Checked By: _______________________________", "Date: _______________"]
            ]
            sig_table = Table(signature_data, colWidths=[4.5*inch, 2*inch])
            sig_table.setStyle(TableStyle([
                ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
                ("FONTSIZE", (0,0), (-1,-1), 11),
                ("ALIGN", (0,0), (0,-1), "LEFT"),
                ("ALIGN", (1,0), (1,-1), "LEFT"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("TOPPADDING", (0,0), (-1,-1), 8),
            ]))
            story.append(sig_table)
            
            # Build PDF
            doc.build(story)
            
            # Print the PDF
            self._print_file(pdf_path)
            
            self.set_status(f"Printed {len(rows)} totes to PDF: {pdf_path}")
            messagebox.showinfo("Print Complete", f"Report created and sent to printer:\n{pdf_path}")
        except Exception as e:
            self.set_status(f"Print failed: {e}")
            messagebox.showerror("Print Error", f"Failed to print report: {e}")

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

    def on_close(self):
        """Handle window close event"""
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = PrintBuckedReportApp()
    app.mainloop()
    restart_menu()
