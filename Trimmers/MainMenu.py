# menu.py
import customtkinter as ctk
import subprocess
import sys
from pathlib import Path

# Optional: set global theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

APP_ROOT = Path(__file__).resolve().parent

def launch_script(script_name):
    """
    Launch a Python script as a separate process.
    (Use this for independent GUI windows)
    """
    script_path = APP_ROOT / script_name
    subprocess.Popen([sys.executable, str(script_path)], shell=True)

def exit_app():
    app.destroy()

# -----------------------------
# GUI setup
# -----------------------------
app = ctk.CTk()
app.title("Trim Processing Menu")
app.geometry("640x420")

title = ctk.CTkLabel(app, text="Trim Processing System", font=("Arial", 24, "bold"))
title.pack(pady=(12, 8))

content = ctk.CTkFrame(app)
content.pack(fill="both", expand=True, padx=12, pady=8)

# Processing Section
proc_frame = ctk.CTkFrame(content)
proc_frame.pack(fill="x", pady=(6, 8))
proc_label = ctk.CTkLabel(proc_frame, text="Processing", font=("Arial", 18, "bold"))
proc_label.pack(anchor="w", padx=6, pady=(4, 6))

btn_frame_proc = ctk.CTkFrame(proc_frame)
btn_frame_proc.pack(anchor="w", padx=6, pady=(0, 6))
ctk.CTkButton(btn_frame_proc, text="Trimmer Daily Weigh", width=220, height=36,
              command=lambda: launch_script("TrimmerDailyWeigh.py")).pack(side="left", padx=6)
ctk.CTkButton(btn_frame_proc, text="Trimmer Summary", width=220, height=36,
              command=lambda: launch_script("TrimmerSummary.py")).pack(side="left", padx=6)

# Maintenance Section
maint_frame = ctk.CTkFrame(content)
maint_frame.pack(fill="x", pady=(6, 8))
maint_label = ctk.CTkLabel(maint_frame, text="Maintenance", font=("Arial", 18, "bold"))
maint_label.pack(anchor="w", padx=6, pady=(4, 6))

btn_frame_maint = ctk.CTkFrame(maint_frame)
btn_frame_maint.pack(anchor="w", padx=6, pady=(0, 6))
ctk.CTkButton(btn_frame_maint, text="Edit Trimmer List", width=200, height=34,
              command=lambda: launch_script("EditTrimmerList.py")).pack(side="left", padx=6)
ctk.CTkButton(btn_frame_maint, text="Edit Trim Rates", width=200, height=34,
              command=lambda: launch_script("EditTrimRates.py")).pack(side="left", padx=6)
ctk.CTkButton(btn_frame_maint, text="Edit Daily Trim", width=200, height=34,
              command=lambda: launch_script("EditDailyTrim.py")).pack(side="left", padx=6)

# Exit button
btn_exit = ctk.CTkButton(app, text="Exit", width=120, height=36, fg_color="gray",
                         hover_color="#5a5a5a", command=exit_app)
btn_exit.pack(pady=(6, 12))

footer = ctk.CTkLabel(app, text="© 2025 ADK Processing", font=("Arial", 12))
footer.pack(side="bottom", pady=6)

app.mainloop()
