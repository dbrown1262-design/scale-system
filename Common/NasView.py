"""NasView - NAS Monitor Status Viewer

Displays:
- Current NAS status from nasstat (row 1)
- Log entries from naslog filtered by date range
"""
import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime, date, timedelta
import pytz
import os
import sys
import subprocess
from supabase import create_client, Client

supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase: Client = create_client(supabase_url, supabase_key)
sb = supabase.schema("scale")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "NAS Monitor Status"
DEFAULT_FONT = ("Arial", 14)


class NasViewApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_TITLE)
        self.geometry("900x600")

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
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # Row 0: Current status
        status_frame = ctk.CTkFrame(frame)
        status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(status_frame, text="Current Status:", font=("Arial", 14, "bold")).pack(side="left", padx=(10, 8))
        self.StatusLabel = ctk.CTkLabel(status_frame, text="Loading...", font=("Arial", 14, "bold"), text_color="#aaaaaa")
        self.StatusLabel.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(status_frame, text="As of:", font=DEFAULT_FONT).pack(side="left", padx=(0, 6))
        self.StatDateLabel = ctk.CTkLabel(status_frame, text="", font=DEFAULT_FONT)
        self.StatDateLabel.pack(side="left")

        # Row 1: Date filter controls
        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ctk.CTkLabel(filter_frame, text="Start Date:", font=DEFAULT_FONT).pack(side="left", padx=(6, 6))
        self.StartDate = DateEntry(filter_frame, font=("Arial", 13), date_pattern="yyyy-mm-dd",
                                   width=12, background="#1f538d", foreground="white", borderwidth=2)
        self.StartDate.set_date(date.today() - timedelta(days=1))
        self.StartDate.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filter_frame, text="End Date:", font=DEFAULT_FONT).pack(side="left", padx=(0, 6))
        self.EndDate = DateEntry(filter_frame, font=("Arial", 13), date_pattern="yyyy-mm-dd",
                                 width=12, background="#1f538d", foreground="white", borderwidth=2)
        self.EndDate.set_date(date.today())
        self.EndDate.pack(side="left", padx=(0, 16))

        ctk.CTkButton(filter_frame, text="Refresh", width=100, font=DEFAULT_FONT, command=self.load_data).pack(side="left", padx=(0, 8))
        ctk.CTkButton(filter_frame, text="Close", width=100, font=DEFAULT_FONT, command=self.on_close).pack(side="left")

        # Row 2: Log treeview
        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        cols = ("Timestamp", "Status", "Description")
        self.Tree = ttk.Treeview(tree_frame, columns=cols, show="headings")

        self.Tree.heading("Timestamp", text="Timestamp")
        self.Tree.heading("Status", text="Status")
        self.Tree.heading("Description", text="Description")

        self.Tree.column("Timestamp", width=150, anchor="w")
        self.Tree.column("Status", width=60, anchor="center")
        self.Tree.column("Description", width=660, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(yscrollcommand=scrollbar.set)

        self.Tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.load_data()

    def load_data(self):
        self.load_status()
        self.load_log()

    def load_status(self):
        try:
            res = sb.table("nasstat").select("statdate, status").eq("id", 1).execute()
            if res.data:
                row = res.data[0]
                status = row.get("status", "")
                statdate = row.get("statdate", "")
                print(f"Loaded NAS status: {status} as of {statdate}")
                color = "#44cc44" if status == "ok" else "#cc4444"
                self.StatusLabel.configure(text=status.upper(), text_color=color)
                if statdate:
                    try:
                        dt = datetime.fromisoformat(statdate)
                        if dt.tzinfo is None:
                            dt = pytz.utc.localize(dt)
                        dt = dt.astimezone(pytz.timezone("America/New_York"))
                        self.StatDateLabel.configure(text=dt.strftime("%Y-%m-%d %H:%M:%S"))
                    except Exception as e:
                        print(f"statdate conversion error: {e}")
                        self.StatDateLabel.configure(text=statdate)
            else:
                self.StatusLabel.configure(text="No data", text_color="#aaaaaa")
        except Exception as e:
            self.StatusLabel.configure(text=f"Error: {e}", text_color="#cc4444")

    def load_log(self):
        self.Tree.delete(*self.Tree.get_children())
        try:
            start = self.StartDate.get_date().isoformat()
            end_dt = datetime.combine(self.EndDate.get_date() + timedelta(days=1), datetime.min.time())
            end = end_dt.isoformat()

            res = (sb.table("naslog")
                   .select("created_at, status, logdesc")
                   .gte("created_at", start)
                   .lt("created_at", end)
                   .order("created_at", desc=True)
                   .execute())

            for row in res.data or []:
                created_at = row.get("created_at", "")
                try:
                    dt = datetime.fromisoformat(created_at)
                    if dt.tzinfo is None:
                        dt = pytz.utc.localize(dt)
                    dt = dt.astimezone(pytz.timezone("America/New_York"))
                    ts = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    ts = created_at
                self.Tree.insert("", "end", values=(ts, row.get("status", ""), row.get("logdesc", "")))
        except Exception as e:
            self.Tree.insert("", "end", values=("Error", "", str(e)))

    def on_close(self):
        self.destroy()
        restart_menu()


if __name__ == "__main__":
    app = NasViewApp()
    app.mainloop()
