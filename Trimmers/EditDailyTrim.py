# DailyTrimEditor.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date, datetime, time, timedelta
from dateutil.parser import parse as dtparse
import SubSupa
from tkcalendar import DateEntry
import os
import sys
import subprocess

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

# ---------- Helpers ----------
def AsIsoDate(s: str) -> str:
    return dtparse(s).date().isoformat()

def AsFloatOrNone(s: str):
    s = s.strip()
    return float(s) if s else None

def GenTimeLabels8To5Step15(include_blank=True):
    """
    Returns ['','8:00 AM','8:15 AM',...,'5:00 PM'] (blank first if include_blank)
    """
    start = datetime.combine(date.today(), time(8, 0))
    end   = datetime.combine(date.today(), time(17, 0))
    step  = timedelta(minutes=15)
    labels = []
    cur = start
    while cur <= end:
        labels.append(cur.strftime("%I:%M %p").lstrip("0"))
#        labels.append(cur.strftime("%-I:%M %p") if hasattr(time, "fold") else cur.strftime("%I:%M %p").lstrip("0"))
        cur += step
    return ([""] + labels) if include_blank else labels

def LabelToPgTime(label: str) -> str | None:
    """
    '1:15 PM' -> '13:15:00'; '' -> None
    """
    label = label.strip()
    if not label:
        return None
    dt = datetime.strptime(label, "%I:%M %p")
    return dt.strftime("%H:%M:%S")

def PgTimeToLabel(pg: str | None) -> str:
    """
    '13:15:00' -> '1:15 PM'; None/'' -> ''
    """
    if not pg:
        return ""
    # Accept 'HH:MM' or 'HH:MM:SS'
    try:
        t = datetime.strptime(pg, "%H:%M:%S")
    except ValueError:
        t = datetime.strptime(pg, "%H:%M")
    label = t.strftime("%I:%M %p").lstrip("0")
    return label

class DailyTrimEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("DailyTrim Viewer/Editor")
        self.geometry("1200x620")
#        self.sb = SubSupa.get_client()
        self.current_row = None
        self._time_labels = GenTimeLabels8To5Step15(include_blank=True)
        
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
        
        self.build_ui()
        self.load_rows()

    def build_ui(self):
        # Filters
        f = ctk.CTkFrame(self)
        f.pack(fill="x", padx=8, pady=8)
        default_font = ctk.CTkFont(size=22)

        ctk.CTkLabel(f, text="Trim Date:", font=default_font).grid(row=0, column=0, padx=6, pady=6)
        self.date_entry = DateEntry(f, width=12, date_pattern="yyyy-mm-dd", font=default_font)
        self.date_entry.set_date(date.today())
        self.date_entry.grid(row=0, column=1, padx=6, pady=6)
        ctk.CTkLabel(f, text="Trimmer:", font=default_font).grid(row=0, column=2, padx=6, pady=6)
        self.var_trimmer = ctk.StringVar()
        # Populate trimmer list with 'Select' as first entry
        try:
            trimmers = SubSupa.GetTrimmerList() or []
        except Exception:
            trimmers = []
        values = ["Select"] + (trimmers if isinstance(trimmers, list) else list(trimmers))
        self.trimmer_combo = ctk.CTkComboBox(f, variable=self.var_trimmer, values=values, font=default_font, width=150, state="readonly")
        self.trimmer_combo.set("Select")
        self.trimmer_combo.grid(row=0, column=3, padx=6, pady=6)
        ctk.CTkLabel(f, text="AM/PM:", font=default_font).grid(row=0, column=4, padx=6, pady=6)
        self.var_ampm = ctk.StringVar()
        self.ampm_combo = ctk.CTkComboBox(f, variable=self.var_ampm,
                     values=["", "Morning", "Afternoon"], font=default_font, width=120, state="readonly")
        self.ampm_combo.grid(row=0, column=5, padx=6, pady=6)
        ctk.CTkButton(f, text="Load", command=self.load_rows, font=default_font).grid(row=0, column=6, padx=6, pady=6)
        ctk.CTkButton(f, text="Close", command=self.destroy, font=default_font).grid(row=0, column=7, padx=6, pady=6)

        # Table
        cols = ["TrimmerName", "TrimDate", "CropNo", "Strain",
                "TrimType", "AmPm", "Grams", "StartTime", "EndTime"]
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        headings = {
            "TrimmerName": "Trimmer",
            "TrimDate": "Trim Date",
            "CropNo": "Crop #",
            "Strain": "Strain",
            "TrimType": "Type",
            "AmPm": "AM/PM",
            "Grams": "Grams",
            "StartTime": "Start Time",
            "EndTime": "End Time",
        }
        widths = {
            "TrimmerName": 150, "TrimDate": 110, "CropNo": 70, "Strain": 180,
            "TrimType": 90, "AmPm": 100, "Grams": 90, "StartTime": 110, "EndTime": 110
        }
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="center")

        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Edit controls
        ef = ctk.CTkFrame(self)
        ef.pack(fill="x", padx=8, pady=8)
        self.lbl_key = ctk.CTkLabel(ef, text="", font=default_font, text_color="#888888")
        self.lbl_key.grid(row=0, column=0, columnspan=8, sticky="w", padx=6, pady=(6,12))

        ctk.CTkLabel(ef, text="Grams:", font=default_font).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.var_grams = ctk.StringVar()
        ctk.CTkEntry(ef, textvariable=self.var_grams, width=100, font=default_font).grid(row=1, column=1, sticky="w", padx=(6,18), pady=6)

        ctk.CTkLabel(ef, text="Start Time:", font=default_font).grid(row=1, column=2, sticky="e", padx=6, pady=6)
        self.var_start = ctk.StringVar()
        self.cmb_start = ctk.CTkComboBox(ef, variable=self.var_start, width=120,
                                      values=self._time_labels, state="readonly", font=default_font)
        self.cmb_start.grid(row=1, column=3, sticky="w", padx=(6,18), pady=6)

        ctk.CTkLabel(ef, text="End Time:", font=default_font).grid(row=1, column=4, sticky="e", padx=6, pady=6)
        self.var_end = ctk.StringVar()
        self.cmb_end = ctk.CTkComboBox(ef, variable=self.var_end, width=120,
                                    values=self._time_labels, state="readonly", font=default_font)
        self.cmb_end.grid(row=1, column=5, sticky="w", padx=(6,18), pady=6)

        ctk.CTkButton(ef, text="Save", command=self.save_changes, font=default_font).grid(row=1, column=6, padx=6, pady=6)
        ctk.CTkButton(ef, text="Clear", command=self.clear_selection, font=default_font).grid(row=1, column=7, padx=6, pady=6)
        # Status label (in-window messages)
        self.status_label = ctk.CTkLabel(self, text="", font=default_font, text_color="#00aa00")
        self.status_label.pack(fill="x", padx=10, pady=(4, 8))

    def show_status(self, message: str, level: str = "info", duration: int = 4000):
        """Show a non-modal status message inside the window for `duration` ms.

        level: 'info'|'warning'|'error'
        """
        color = "#00aa00" if level == "info" else ("#ff8800" if level == "warning" else "#ff4444")
        try:
            self.status_label.configure(text=message, text_color=color)
            # clear after duration
            if duration and duration > 0:
                self.after_cancel(getattr(self, "_status_after_id", "")) if getattr(self, "_status_after_id", "") else None
                self._status_after_id = self.after(duration, lambda: self.status_label.configure(text=""))
        except Exception:
            # fallback to messagebox if anything goes wrong
            if level == "warning":
                messagebox.showwarning("Warning", message)
            elif level == "error":
                messagebox.showerror("Error", message)
            else:
                messagebox.showinfo("Info", message)

    def load_rows(self):
        # Ensure a valid trimmer is selected
        trimmer = self.trimmer_combo.get().strip()
        if trimmer == "" or trimmer == "Select":
            self.show_status("Please choose a Trimmer before loading.", level="warning")
            return

        try:
            start_date = self.date_entry.get_date()
        except Exception:
            self.show_status("Invalid date (try YYYY-MM-DD).", level="error")
            return

        # Clear tree
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Aggregate rows for selected date + next 6 days
        all_rows = []
        for d_off in range(7):
            d = start_date + timedelta(days=d_off)
            iso = d.isoformat()
            try:
                res = SubSupa.SelectDailytrim(
                    trim_date=iso,
                    trimmer=trimmer,
                    ampm=self.var_ampm.get().strip()
                )
            except Exception:
                # continue to next day if one day fails
                continue
            if res and getattr(res, 'data', None):
                all_rows.extend(res.data or [])

        # Sort rows by TrimDate then TrimmerName then Strain
        def _sort_key(r):
            return (r.get('TrimDate') or '', r.get('TrimmerName') or '', r.get('Strain') or '')

        for r in sorted(all_rows, key=_sort_key):
            # Show Start/End as labels in the grid for readability
            start_label = PgTimeToLabel(r.get("StartTime"))
            end_label = PgTimeToLabel(r.get("EndTime"))
            vals = [
                r.get("TrimmerName") or "",
                r.get("TrimDate") or "",
                r.get("CropNo") or "",
                r.get("Strain") or "",
                r.get("TrimType") or "",
                r.get("AmPm") or "",
                r.get("Grams") or "",
                start_label,
                end_label,
            ]
            self.tree.insert("", "end", values=vals)

        # Show status with date range and count
        end_date = start_date + timedelta(days=6)
        self.show_status(f"Loaded {len(all_rows)} rows for {start_date.isoformat()} to {end_date.isoformat()}")

        self.clear_selection()

    def on_select(self, _evt):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        cols = list(self.tree["columns"])
        self.current_row = dict(zip(cols, vals))

        # Key banner
        self.lbl_key.config(
            text=f"Trimmer={self.current_row['TrimmerName']} | Date={self.current_row['TrimDate']} | "
                 f"CropNo={self.current_row['CropNo']} | Strain={self.current_row['Strain']} | "
                 f"Type={self.current_row['TrimType']} | AmPm={self.current_row['AmPm']}"
        )

        # Populate editors
        self.var_grams.set(self.current_row["Grams"] or "")
        self.var_start.set(self.current_row["StartTime"] or "")
        self.var_end.set(self.current_row["EndTime"] or "")

    def clear_selection(self):
        self.tree.selection_remove(self.tree.selection())
        self.current_row = None
        self.lbl_key.configure(text="")
        self.var_grams.set("")
        self.var_start.set("")
        self.var_end.set("")

    def save_changes(self):
        if not self.current_row:
            self.show_status("No row selected.", level="info")
            return

        # Validate/convert
        try:
            grams = AsFloatOrNone(self.var_grams.get())
        except ValueError:
            self.show_status("Grams must be numeric.", level="error")
            return

        start_pg = LabelToPgTime(self.var_start.get())
        end_pg   = LabelToPgTime(self.var_end.get())

        # Build update + match
        new_vals = {"Grams": grams, "StartTime": start_pg, "EndTime": end_pg}
        match = {
            "TrimmerName": self.current_row["TrimmerName"],
            "TrimDate": self.current_row["TrimDate"],
            "CropNo": self.current_row["CropNo"],
            "Strain": self.current_row["Strain"],
            "TrimType": self.current_row["TrimType"],
            "AmPm": self.current_row["AmPm"],
        }

        # Indicate busy cursor while saving (hourglass/watch) and ensure restoration
        try:
            try:
                # set hourglass/wait cursor for whole window
                try:
                    self.configure(cursor="watch")
                except Exception:
                    # fallback cursor name (platform differences)
                    try:
                        self.configure(cursor="wait")
                    except Exception:
                        pass
                # ensure UI updates so cursor change appears immediately
                self.update_idletasks()

                self.show_status("Saving...", level="info", duration=0)
                SubSupa.UpdateDailytrim(match, new_vals)
            except Exception as e:
                self.show_status(f"Update failed: {e}", level="error")
                return
            finally:
                # restore cursor
                try:
                    self.configure(cursor="")
                except Exception:
                    try:
                        self.configure(cursor="arrow")
                    except Exception:
                        pass
                self.update_idletasks()

            # reload and report success
            self.load_rows()
            self.show_status("Row updated successfully.", level="info")
        finally:
            # Ensure any temporary status auto-clears shortly after completion
            try:
                # clear the 'Saving...' message after a short delay if it remained
                self.after(1200, lambda: self.status_label.configure(text=""))
            except Exception:
                pass

if __name__ == "__main__":
    app = DailyTrimEditor()
    app.mainloop()
    restart_menu()
