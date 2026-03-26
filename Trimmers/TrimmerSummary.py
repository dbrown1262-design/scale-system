import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta
from datetime import time as dt_time
import subprocess
from tkcalendar import DateEntry
from SubSupa import GetTrimSummary, GetTrimmerList, GetRatesMap
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import os, tempfile, sys
from typing import Optional

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Conversion constant
GRAMS_TO_LBS = 0.00220462262185

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


# --- time helpers ---
def pg_time_to_label(pg: Optional[str]) -> str:
    """Convert DB time 'HH:MM:SS' or 'HH:MM' to UI label 'h:mm AM/PM'"""
    if not pg:
        return ""
    try:
        t = datetime.strptime(pg, "%H:%M:%S")
    except Exception:
        try:
            t = datetime.strptime(pg, "%H:%M")
        except Exception:
            return ""
    return t.strftime("%I:%M %p").lstrip("0")


def hours_between(start_pg: Optional[str], end_pg: Optional[str]) -> float:
    """Return hours (float) between start and end DB times. Returns 0.0 if invalid."""
    if not start_pg or not end_pg:
        return 0.0
    try:
        s = datetime.strptime(start_pg, "%H:%M:%S")
    except Exception:
        try:
            s = datetime.strptime(start_pg, "%H:%M")
        except Exception:
            return 0.0
    try:
        e = datetime.strptime(end_pg, "%H:%M:%S")
    except Exception:
        try:
            e = datetime.strptime(end_pg, "%H:%M")
        except Exception:
            return 0.0
    delta = e - s
    # if negative, treat as 0
    total_seconds = max(delta.total_seconds(), 0.0)
    return round(total_seconds / 3600.0, 2)


class SummaryScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.selected_trimmer = None
        self.start_date = None
        self.create_widgets()
        self.load_trimmers()
#        self.load_data()

    def export_data_pdf(self):
        # Collect data from UI state
        start = self.date_entry.get_date()
        end = start + timedelta(days=6)
        trimmer = self.trimmer_combo.get()

        # Helper to pull a table from a Treeview
        def tv_to_table(tree, header):
            rows = [header]
            for iid in tree.get_children():
                vals = tree.item(iid, "values")
                rows.append(list(vals))
            return rows

        # Build the document
        tmpdir = tempfile.gettempdir()
        pdf_path = os.path.join(tmpdir, "trimmer_summary_report.pdf")
        # Use portrait LETTER for the report
        doc = SimpleDocTemplate(pdf_path, pagesize=LETTER, leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)

        styles = getSampleStyleSheet()
        story = []

        # Title section with separate lines
#        story.append(Paragraph("Trimmer Summary & Pay", styles["Title"]))
#        story.append(Spacer(1, 0.05 * inch))

        # Date range
        date_range = f"{start.isoformat()} To {end.isoformat()}"
        story.append(Paragraph(f"<b>Trimmer Summary From</b> {date_range}", styles["Title"]))
        story.append(Spacer(1, 0.05 * inch))

        # Trimmer (only if not All)
        if trimmer and trimmer != "All":
            story.append(Paragraph(f"<b>Trimmer:</b> {trimmer}", styles["Title"]))
            story.append(Spacer(1, 0.15 * inch))
        else:
            story.append(Spacer(1, 0.15 * inch))

        # Sections: build from per-day trees if present, otherwise fall back to legacy morning/afternoon
        sections = []
        if getattr(self, 'days_info', None):
            # days_info: list of (date_obj, tree)
            # For per-day UI trees we intentionally omit the date heading in the PDF
            for d, tree in self.days_info:
                hdr = ["Date", "Strain", "Flower (g)", "Smalls (g)", "Start Time", "End Time", "Hours"]
                sections.append((None, tree, hdr))
        else:
            # backward compatibility
            try:
                sections = [
                    ("Morning Session", self.morning_tree, ["Date", "Strain", "Flower (g)", "Smalls (g)", "Start Time", "End Time", "Hours"]),
                    ("Afternoon Session", self.afternoon_tree, ["Date", "Strain", "Flower (g)", "Smalls (g)", "Start Time", "End Time", "Hours"]),
                ]
            except Exception:
                sections = []

        # Pay section appended separately below
        for heading, tree, header in sections:
            # Only add a heading for legacy session sections; per-day sections use None
            if heading:
                story.append(Paragraph(heading, styles["Title"]))
            data = tv_to_table(tree, header)
            tbl = Table(data, hAlign="CENTER")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("TEXTCOLOR", (0,0), (-1,0), colors.black),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,0), 12),
                ("FONTSIZE", (0,1), (-1,-1), 12),
                ("ALIGN", (0,0), (-1,0), "CENTER"),
                ("ALIGN", (0,1), (-1,-1), "LEFT"),
                ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 4),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 0.2 * inch))

        # Now append the Pay — Flower (Bigs) section
        story.append(Paragraph("Pay — Flower (Bigs)", styles["Title"]))
        data = tv_to_table(self.pay_bigs_tree, ["CropNo", "Strain", "Rate", "Total Grams", "Pay"]) if getattr(self, 'pay_bigs_tree', None) else []
        if data:
            tbl = Table(data, hAlign="CENTER")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("TEXTCOLOR", (0,0), (-1,0), colors.black),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,0), 12),
                ("FONTSIZE", (0,1), (-1,-1), 12),
                ("ALIGN", (0,0), (-1,0), "CENTER"),
                ("ALIGN", (0,1), (-1,-1), "LEFT"),
                ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 4),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 0.2 * inch))

        doc.build(story)
        self._open_file(pdf_path)

    def _open_file(self, path):
        # Open the file with the default app on each OS
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)

    def _print_file(self, path):
        # Optional: print the PDF (not used by export_data_pdf, but handy)
        if sys.platform.startswith("win"):
            try:
                os.startfile(path, "print")  # type: ignore[attr-defined]
            except OSError:
                self._open_file(path)
        else:
            try:
                subprocess.run(["lpr", path], check=False)
            except FileNotFoundError:
                self._open_file(path)


    def create_widgets(self):
        # Main title
        title = ctk.CTkLabel(self, text="Trimmer Summary", font=("Arial", 22, "bold"))
        title.pack(pady=(10, 6))

        # Configure treeview style for dark theme
        style = ttk.Style()
        try:
            try:
                # Use clam theme for dark mode
                style.theme_use("clam")
            except Exception:
                pass
            # Create a larger Treeview style for row detail readability with dark theme
            style.configure("Large.Treeview", 
                           background="#2b2b2b",
                           foreground="#dce4ee",
                           fieldbackground="#2b2b2b",
                           font=("Arial", 18), 
                           rowheight=36)
            style.configure("Large.Treeview.Heading", 
                           background="#1f538d",
                           foreground="#ffffff",
                           font=("Arial", 18, "bold"))
            style.map("Large.Treeview",
                     background=[("selected", "#144870")])
        except Exception:
            pass

        # Filter row
        filter_row = ctk.CTkFrame(self)
        filter_row.pack(fill="x", padx=10, pady=(0, 8))

        # Trimmer selection
        ctk.CTkLabel(filter_row, text="Trimmer:", font=("Arial", 14)).pack(side="left", padx=(0, 6))
        self.trimmer_combo = ctk.CTkComboBox(
            filter_row,
            values=["All"],
            width=200,
            font=("Arial", 14),
            command=self.on_trimmer_change
        )
        self.trimmer_combo.set("All")
        self.trimmer_combo.pack(side="left", padx=(0, 10))

        # Date selection (weekly start)
        ctk.CTkLabel(filter_row, text="Start Date:", font=("Arial", 14)).pack(side="left")
        self.date_entry = DateEntry(filter_row, width=12, font=("Arial", 13), date_pattern="yyyy-mm-dd",
                                     background='#343638', foreground='#DCE4EE', 
                                     fieldbackground='#343638', borderwidth=2)
        self.date_entry.set_date(datetime.now().date())
        self.date_entry.pack(side="left", padx=(5, 10))
        # Style the entry widget inside DateEntry
        try:
            self.date_entry.entry.configure(bg='#343638', fg='#DCE4EE', insertbackground='#DCE4EE')
        except Exception:
            pass

        refresh_btn = ctk.CTkButton(filter_row, text="Load Week", command=self.load_data, width=110)
        refresh_btn.pack(side="left", padx=4)

        # Export report PDF button
        ctk.CTkButton(filter_row, text="Export Report PDF", width=150, command=self.export_data_pdf).pack(side="left", padx=4)
        
        # Close button
        ctk.CTkButton(filter_row, text="Close", width=100, command=lambda: self.master.destroy()).pack(side="left", padx=4)

        # Per-day summary container (one box per day in the selected week)
        self.days_frame = ctk.CTkFrame(self)
        self.days_frame.pack(fill="both", expand=True, padx=10, pady=(6, 0))
        # days_info will hold tuples (date_obj, treeview)
        self.days_info = []

        # --- Grand Total section ---
        grand_total_frame = ctk.CTkFrame(self)
        grand_total_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        ctk.CTkLabel(grand_total_frame, text="Week Grand Total:", font=("Arial", 16, "bold")).pack(side="left", padx=(10, 20))
        ctk.CTkLabel(grand_total_frame, text="Flower:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 5))
        self.grand_total_flower_label = ctk.CTkLabel(grand_total_frame, text="0.00 g", font=("Arial", 14))
        self.grand_total_flower_label.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(grand_total_frame, text="Smalls:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 5))
        self.grand_total_smalls_label = ctk.CTkLabel(grand_total_frame, text="0.00 g", font=("Arial", 14))
        self.grand_total_smalls_label.pack(side="left", padx=(0, 10))

        # --- Pay sections ---
        pay_label = ctk.CTkLabel(self, text="Pay Summary", font=("Arial", 18, "bold"))
        pay_label.pack(pady=(16, 0))

        # Pay — Flower (Bigs)
        pay_bigs_label = ctk.CTkLabel(self, text="Pay — Flower (Bigs)", font=("Arial", 16, "bold"))
        pay_bigs_label.pack(pady=(8, 0))
        # Create the pay tree
        self.pay_bigs_tree = self.create_pay_treeview(master=self)
        self.pay_bigs_tree.pack(padx=10, pady=5, fill="x")

    def create_treeview(self, master=None, show_headings=True):
        # Extended columns: include Start/End/Hours (Hours computed for Flower rows only)
        cols = ("Date", "Strain", "Flower (g)", "Smalls (g)", "Start Time", "End Time", "Hours")
        # Always use "headings" to ensure consistent column alignment
        tree = ttk.Treeview(master or self, style="Large.Treeview", columns=cols, show="headings", height=7)
        for col in cols:
            # Show empty text for headings if show_headings is False (hides duplicate headers visually)
            heading_text = col if show_headings else ""
            tree.heading(col, text=heading_text)
            if col in ("Date", "Strain"):
                anchor = "w"
            elif col in ("Start Time", "End Time"):
                anchor = "center"
            else:
                anchor = "e"
            # set reasonable widths per column
            if col == "Strain":
                width = 250
            elif col == "Date":
                width = 160
            elif col in ("Start Time", "End Time"):
                width = 110
            elif col == "Hours":
                width = 90
            else:
                width = 130
            tree.column(col, anchor=anchor, width=width, stretch=False)
        style = ttk.Style()
        tree.tag_configure("odd", background="#1f1f1f", foreground="#dce4ee")
        tree.tag_configure("even", background="#2b2b2b", foreground="#dce4ee")
        tree.tag_configure("total", background="#1f538d", foreground="#ffffff", font=("Arial", 14, "bold"))
        return tree
    
    def create_pay_treeview(self, master=None):
        cols = ("CropNo", "Strain", "Rate", "Total Grams", "Pay")
        tree = ttk.Treeview(master or self, style="Large.Treeview", columns=cols, show="headings", height=7)
        widths = {"CropNo": 90, "Strain": 250, "Rate": 110, "Total Grams": 120, "Pay": 120}
        aligns = {"CropNo": "center", "Strain": "w", "Rate": "e", "Total Grams": "e", "Pay": "e"}
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=widths[c], anchor=aligns[c], stretch=False)

        style = ttk.Style()
        tree.tag_configure("odd", background="#1f1f1f", foreground="#dce4ee")
        tree.tag_configure("even", background="#2b2b2b", foreground="#dce4ee")
        tree.tag_configure("total", background="#1f538d", foreground="#ffffff", font=("Arial", 14, "bold"))
        return tree

    def _create_total_tree(self) -> ttk.Treeview:
        cols = ("Total Grams", "Total Pay")
        tree = ttk.Treeview(self, style="Large.Treeview", columns=cols, show="headings", height=1)
        tree.heading("Total Grams", text="Total Grams")
        tree.heading("Total Pay", text="Total Pay")
        tree.column("Total Grams", width=180, anchor="e", stretch=False)
        tree.column("Total Pay", width=180, anchor="e", stretch=False)
        style = ttk.Style()
        tree.tag_configure("total", background="#1f538d", foreground="#ffffff", font=("Arial", 14, "bold"))
        return tree






    def build_pay_aggregates(self, rows):
        """
        From raw rows (already filtered by date + trimmer), build dict:
        bigs[(CropNo, Strain)] -> total flower grams
        """
        bigs = {}
        for r in rows:
            crop = int(r.get("CropNo") or 0)
            strain = (r.get("Strain") or "").strip()
            flower_grams = float(r.get("FlowerGrams") or 0)
            key = (crop, strain)
            bigs[key] = bigs.get(key, 0.0) + flower_grams
        return bigs

    def insert_pay_table(self, tree, grams_map, rate_type, rates_map, lunch_count=0):
        """
        rate_type: 'bigs' or 'smalls'
        grams_map: dict[(CropNo, Strain)] -> grams
        rates_map: dict[(CropNo, Strain)] -> {'bigs': rate, 'smalls': rate}
        """
        tree.delete(*tree.get_children())
        total_pay = 0.0
        total_grams = 0.0
        # Sorted display by CropNo then Strain
        items = sorted(grams_map.items(), key=lambda kv: (kv[0][0], kv[0][1]))
        for i, (key, grams) in enumerate(items):
            crop, strain = key
            # rates_map now maps (CropNo, Strain) -> BigsRate (float)
            # only bigs/pay is supported here, so read the float directly
            rate = float(rates_map.get(key, 0.0))
            pay = round(grams * rate, 2)
            total_pay += pay
            total_grams += grams
            tag = "odd" if i % 2 else "even"
            tree.insert(
                "",
                "end",
                values=(crop, strain, f"{rate:.4f}", f"{grams:.2f}", f"{pay:.2f}"),
                tags=(tag,),
            )

        # Insert Lunch row (one per day with >=6 hours)
        if lunch_count and lunch_count > 0:
            lunch_pay = round(lunch_count * 20.0, 2)
            # choose tag based on current number of data rows
            tag = "odd" if (len(items) % 2) else "even"
            tree.insert(
                "",
                "end",
                values=("", "Lunch", f"{20.00:.2f}", "", f"{lunch_pay:.2f}"),
                tags=(tag,),
            )
            total_pay += lunch_pay

        # Totals row
        tree.insert(
            "",
            "end",
            values=("", "TOTAL", "", f"{total_grams:.2f}", f"{total_pay:.2f}"),
            tags=("total",),
        )

    def _insert_total_pay(self, total_grams: float, total_pay: float):
        self.total_pay_tree.delete(*self.total_pay_tree.get_children())
        self.total_pay_tree.insert("", "end", values=(f"{total_grams:.2f}", f"{total_pay:.2f}"), tags=("total",))

    def load_trimmers(self):
        try:
            trimmers = GetTrimmerList()
            values = ["All"] + trimmers
            self.trimmer_combo.configure(values=values)
            if self.trimmer_combo.get() not in values:
                self.trimmer_combo.set("All")
        except Exception:
            self.trimmer_combo.configure(values=["All"])
            self.trimmer_combo.set("All")
    

    def insert_day_summary(self, tree, rows):
        """Populate a per-day tree. Display each row with FlowerGrams and SmallsGrams."""
        # Clear existing rows
        tree.delete(*tree.get_children())

        total_flower = 0.0
        total_smalls = 0.0
        total_hours = 0.0

        # Sort rows for stable display: by TrimDate, CropNo, Strain
        def _row_key(r):
            td = (r.get("TrimDate") or "")
            crop = int(r.get("CropNo") or 0)
            strain = (r.get("Strain") or "")
            ampm = (r.get("AmPm") or "")
            return (td, crop, strain, ampm)

        for i, r in enumerate(sorted(rows, key=_row_key)):
            flower_val = float(r.get("FlowerGrams") or 0)
            smalls_val = float(r.get("SmallsGrams") or 0)

            start_pg = r.get("StartTime")
            end_pg = r.get("EndTime")
            start_label = pg_time_to_label(start_pg)
            end_label = pg_time_to_label(end_pg)

            hrs = 0.0
            if start_pg and end_pg:
                try:
                    hrs = hours_between(start_pg, end_pg)
                except Exception:
                    hrs = 0.0

            total_flower += flower_val
            total_smalls += smalls_val
            total_hours += hrs

            hrs_str = f"{hrs:.2f}" if hrs else ""
            tag = "odd" if i % 2 else "even"

            # Display: Date, Strain, Flower (g), Smalls (g), Start Time, End Time, Hours
            date_str = (r.get("TrimDate") or "").split("T", 1)[0]
            tree.insert("", "end", values=(date_str, r.get("Strain") or "", f"{flower_val:.2f}" if flower_val else "", f"{smalls_val:.2f}" if smalls_val else "", start_label, end_label, hrs_str), tags=(tag,))

        # Totals row for the day
        tree.insert("", "end", values=("", "TOTAL", round(total_flower, 2), round(total_smalls, 2), "", "", f"{total_hours:.2f}"), tags=("total",))

    def on_trimmer_change(self, _value):
        val = self.trimmer_combo.get().strip()
        self.selected_trimmer = None if val == "All" else val
#        self.load_data()

    def load_data(self):
        start = self.date_entry.get_date()
        end = start + timedelta(days=6)
        self.start_date = start

        data = GetTrimSummary(trimmer_name=self.selected_trimmer, start_date=start, end_date=end)

        # Clear any previous day widgets
        for child in list(self.days_frame.children.values()):
            try:
                child.destroy()
            except Exception:
                pass
        self.days_info = []

        # For each day in the week, create a tree and populate with that day's rows
        lunch_count = 0
        first_tree_created = False
        for d_off in range(7):
            d = start + timedelta(days=d_off)
            iso = d.isoformat()
            # Filter rows for this date (TrimDate may include a time portion)
            rows_for_day = [r for r in data if (r.get('TrimDate') or '').startswith(iso)]

            # compute total hours for the day from all rows that have start & end
            day_total_hours = 0.0
            for r in rows_for_day:
                st = r.get('StartTime')
                en = r.get('EndTime')
                if st and en:
                    try:
                        day_total_hours += hours_between(st, en)
                    except Exception:
                        pass

            # Lunch counter: add one if total day hours >= 6
            try:
                if day_total_hours >= 6.0:
                    lunch_count += 1
            except Exception:
                pass

            # skip creating a box for days with zero total hours
            if not day_total_hours:
                continue

            # Per-day frame
            day_frame = ctk.CTkFrame(self.days_frame)
            day_frame.pack(fill="x", pady=(4, 8))

            # pack the ttk tree inside a regular frame (works with CTk)
            tree_widget_parent = ttk.Frame(day_frame)
            tree_widget_parent.pack(fill="x", padx=6)
            # Only show headings for the first treeview
            show_headings = not first_tree_created
            tree = self.create_treeview(master=tree_widget_parent, show_headings=show_headings)
            first_tree_created = True
            # Compute how many rows we'll display: one per DB row + 1 TOTAL row
            data_rows = len(rows_for_day)
            # Ensure at least 1 visible data row; add 1 for the TOTAL row. Cap to avoid extremely tall widgets.
            rows_to_show = min(max(data_rows, 1) + 1, 20)
            try:
                tree.configure(height=rows_to_show)
            except Exception:
                # older ttk widgets may not support configure; ignore in that case
                pass
            tree.pack(fill="x", padx=0, pady=0)

            # store and populate
            self.days_info.append((d, tree))
            self.insert_day_summary(tree, rows_for_day)

        # Calculate grand totals across all data
        grand_total_flower = sum(float(r.get("FlowerGrams") or 0) for r in data)
        grand_total_smalls = sum(float(r.get("SmallsGrams") or 0) for r in data)
        
        # Update grand total labels
        self.grand_total_flower_label.configure(text=f"{grand_total_flower:.2f} g")
        self.grand_total_smalls_label.configure(text=f"{grand_total_smalls:.2f} g")

        # Pay tables
        rates_map = GetRatesMap()
        bigs_map = self.build_pay_aggregates(data)
        # pass lunch_count so insert_pay_table can add Lunch rows and include them in totals
        self.insert_pay_table(self.pay_bigs_tree, bigs_map, "bigs", rates_map, lunch_count=lunch_count)

        # Compute overall totals (bigs + smalls)
        total_grams_bigs = sum(bigs_map.values())

        def _sum_pay(grams_map, rate_key):
            # rate_key is ignored because we only return bigs rates from GetRatesMap
            total = 0.0
            for (crop, strain), grams in grams_map.items():
                rate = float(rates_map.get((crop, strain), 0.0))
                total += grams * rate
            return total


        total_pay_bigs = _sum_pay(bigs_map, "bigs")


    def insert_summary(self, tree, rows):
        tree.delete(*tree.get_children())
        grouped = {}

        # We'll also accumulate total hours across displayed groups
        total_hours = 0.0

        for row in rows:
            date_str = row.get("TrimDate", "")
            if "T" in date_str:
                date_str = date_str.split("T", 1)[0]
            strain = row.get("Strain") or ""
            flower_grams = float(row.get("FlowerGrams") or 0)
            smalls_grams = float(row.get("SmallsGrams") or 0)

            key = (date_str, strain)
            if key not in grouped:
                grouped[key] = {"flower": 0.0, "smalls": 0.0, "start_times": [], "end_times": []}
            
            grouped[key]["flower"] += flower_grams
            grouped[key]["smalls"] += smalls_grams
            
            # collect start/end times if present
            st = row.get("StartTime")
            en = row.get("EndTime")
            if st:
                grouped[key]["start_times"].append(st)
            if en:
                grouped[key]["end_times"].append(en)

        total_flower = 0.0
        total_smalls = 0.0
        for i, (key, vals) in enumerate(sorted(grouped.items())):
            date, strain = key
            f, s = round(vals["flower"], 2), round(vals["smalls"], 2)
            total_flower += f
            total_smalls += s

            # Determine Start/End from all rows in this group (earliest start, latest end)
            start_label = ""
            end_label = ""
            hrs = 0.0
            if vals.get("start_times") and vals.get("end_times"):
                try:
                    start_min = min(vals["start_times"])
                    end_max = max(vals["end_times"])
                    start_label = pg_time_to_label(start_min)
                    end_label = pg_time_to_label(end_max)
                    hrs = hours_between(start_min, end_max)
                except Exception:
                    start_label = ""
                    end_label = ""
                    hrs = 0.0

            total_hours += hrs
            hrs_str = f"{hrs:.2f}" if hrs else ""

            tag = "odd" if i % 2 else "even"
            tree.insert("", "end", values=(date, strain, f, s, start_label, end_label, hrs_str), tags=(tag,))

        # Insert TOTAL row including total hours
        tree.insert("", "end", values=("", "TOTAL", round(total_flower, 2), round(total_smalls, 2), "", "", f"{total_hours:.2f}"), tags=("total",))


# ======= MAIN =======
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Trimmer Summary & Pay – Week View")
    root.geometry("900x900")

    app = SummaryScreen(root)
    root.mainloop()
    restart_menu()
