"""Scale Menu

This module creates a simple Tkinter menu with three sections (Harvest, Trimmer, Admin)
and buttons that launch the corresponding scripts in the `Harvest` and `Trimmers` folders.

Implementation details:
- Scripts are launched as separate processes using the same Python interpreter (`sys.executable`)
  and `subprocess.Popen`. This ensures that the launched scripts run independently of the menu.
- The working directory for the launched scripts is set to the root directory of this module.
- If a script is missing, a warning dialog is shown and the status label is updated.
- If launching a script fails, an error dialog is shown and the status label is updated with the error.
- A busy overlay is displayed while launching a script to indicate to the user that the application is working.
- After launching a script, the menu window is destroyed.
"""
import time
import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import messagebox

ROOT_DIR = os.path.dirname(__file__)
DEFAULT_FONT = ("Arial", 14)


def show_busy_overlay(parent):
    overlay = ctk.CTkFrame(parent, fg_color="transparent",cursor="watch")
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    overlay.lift()            # bring on top

    # Create a container frame so the label can have a solid background if desired
    msg_frame = ctk.CTkFrame(
        overlay,
        fg_color="#222222",    # dark translucent feel
        corner_radius=10
    )
    msg_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Add the label
    label = ctk.CTkLabel(
        msg_frame,
        text="Please wait...",
        font=("Arial", 18)
    )
    label.pack(padx=20, pady=12)

    parent.update()
    return overlay

SCRIPTS = {
    "Harvest": [
        ("Weigh Plants", os.path.join("Harvest", "WeighHarvest.py")),
        ("Plant Summary", os.path.join("Harvest", "PlantWeightsSummary.py")),
        ("Weigh Bucked Totes", os.path.join("Harvest", "WeighBucked.py")),
    ],
    "Packaging": [
        ("Add Package", os.path.join("Packaging", "AddPackage.py")),
        ("Edit Package Types", os.path.join("Packaging", "EditPackageTypes.py")),
    ],
    "Trimmer": [
        ("Enter Daily Trim", os.path.join("Trimmers", "TrimmerDailyWeigh.py")),
        ("Weigh Trim Bags", os.path.join("Trimmers", "WeighTrim.py")),
        ("Weekly Trimmer Summary", os.path.join("Trimmers", "TrimmerSummary.py")),
    ],
    "Processing": [
        ("Enter Hash Run", os.path.join("Processing", "EnterHashRun.py")),
        ("Enter Rosin Run", os.path.join("Processing", "EnterRosinRun.py")),
    ],
    "Admin": [
        ("Print Plant Tags", os.path.join("Harvest", "PrintPlantTags.py")),
        ("Assign Batch IDs", os.path.join("Harvest", "AssignBatchId.py")),
        ("Edit Daily Trim", os.path.join("Trimmers", "EditDailyTrim.py")),
        ("Edit Trimmer List", os.path.join("Trimmers", "EditTrimmerList.py")),
        ("Edit Trim Rates", os.path.join("Trimmers", "EditTrimRates.py")),
        ("Scanner Setup", os.path.join("Common", "ScannerSetup.py")),],
}


def open_script(rel_path: str, status_label: ctk.CTkLabel, parent: ctk.CTk):
    """Launch the given script path (relative to ROOT_DIR) in a new process."""
    full = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(full):
        messagebox.showwarning("Missing Script", f"Script not found: {rel_path}")
        status_label.configure(text=f"Script not found: {rel_path}")
        return

    try:
        # Change cursor to waiting (watch is the hourglass/waiting cursor on Windows)
#        parent.configure(cursor="wait")
#        parent.update()
        overlay = show_busy_overlay(parent)
        # Launch with same Python interpreter
        subprocess.Popen([sys.executable, full], cwd=ROOT_DIR)
        status_label.configure(text=f"Launched {os.path.basename(rel_path)}")

        start = time.time()
        while time.time() - start < 5:
            parent.update()             # let Tk process events
            time.sleep(0.01)            # prevent CPU pegging

#        time.sleep(5)  # Give time for the new process to start
        # Change cursor back to normal
#        parent.configure(cursor="")
        overlay.destroy()
        parent.destroy()
    except Exception as e:
        # Ensure cursor is restored on error
        try:
            parent.configure(cursor="")
        except Exception:
            pass
        messagebox.showerror("Launch Failed", f"Failed to launch {rel_path}: {e}")
        status_label.configure(text=f"Launch failed: {e}")


class MenuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Scale Menu")
        self.geometry("1200x680")
        self.resizable(False, False)

        # Set customtkinter appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        header = ctk.CTkLabel(main, text="Main Menu", font=("Arial", 18, "bold"))
        # Center the header at the top
        header.grid(row=0, column=0, columnspan=3, pady=(0,12))

        self.status = ctk.CTkLabel(main, text="", font=("Arial", 16))
        self.status.grid(row=99, column=0, columnspan=3, sticky="w", pady=(12,0))

        # Layout sections: Harvest and Packaging in column 0 (rows 1 and 2), Trimmer and Processing in column 1 (rows 1 and 2), Admin in column 2
        row_col_map = {
            "Harvest": (1, 0),
            "Packaging": (2, 0),
            "Trimmer": (1, 1),
            "Processing": (2, 1),
            "Admin": (1, 2),
        }
        
        for section, items in SCRIPTS.items():
            row, col = row_col_map.get(section, (0, 0))
            # Create a frame with a label for the section
            section_frame = ctk.CTkFrame(main)
            # Admin section spans 2 rows
            rowspan = 2 if section == "Admin" else 1
            section_frame.grid(row=row, column=col, rowspan=rowspan, padx=8, pady=8, sticky="n")
            
            # Section title label
            section_label = ctk.CTkLabel(section_frame, text=section, font=("Arial", 16, "bold"))
            section_label.pack(pady=(10, 5), padx=10)
            
            # Button container
            button_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            button_frame.pack(padx=10, pady=(0, 10))
            
            for idx, (label, rel) in enumerate(items):
                btn = ctk.CTkButton(button_frame, text=label, width=260, font=DEFAULT_FONT, 
                                   command=lambda r=rel: open_script(r, self.status, self))
                btn.grid(row=idx, column=0, pady=6, padx=6)


        # Exit button
        exit_btn = ctk.CTkButton(main, text="Exit", command=self.destroy, font=DEFAULT_FONT)
        exit_btn.grid(row=100, column=2, sticky="e", pady=12)


def main():
    app = MenuApp()
    app.mainloop()


if __name__ == "__main__":
    main()
