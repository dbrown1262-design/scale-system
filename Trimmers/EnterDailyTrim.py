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

APP_TITLE = "Enter Daily Trim"
DEFAULT_FONT = ("Arial", 18)


class EnterDailyTrimApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(APP_TITLE)
        self.geometry("1200x600")
        
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

        # Row 0: CropNo, Strain, TrimmerName
        ctk.CTkLabel(frame, text="Crop No:", font=("Arial", 18)).grid(row=0, column=0, sticky="e", padx=(6,6), pady=8)
        self.CropNoCombo = ctk.CTkComboBox(frame, values=["Select"], state="readonly", width=200, font=("Arial", 18), command=self.OnCropChanged)
        self.CropNoCombo.grid(row=0, column=1, sticky="w", pady=8)
        self.CropNoCombo.set("Select")

        ctk.CTkLabel(frame, text="Strain:", font=("Arial", 18)).grid(row=0, column=2, sticky="e", padx=(6,6), pady=8)
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], state="readonly", width=200, font=("Arial", 18), command=lambda choice: self.OnFilterChanged())
        self.StrainCombo.grid(row=0, column=3, sticky="w", pady=8)
        self.StrainCombo.set("Select")

        ctk.CTkLabel(frame, text="Trimmer:", font=("Arial", 18)).grid(row=0, column=4, sticky="e", padx=(6,6), pady=8)
        self.TrimmerNameCombo = ctk.CTkComboBox(frame, values=["Select"], state="readonly", width=200, font=("Arial", 18), command=lambda choice: self.OnFilterChanged())
        self.TrimmerNameCombo.grid(row=0, column=5, sticky="w", pady=8)
        self.TrimmerNameCombo.set("Select")

        # Row 1: TrimDate and entry fields
        ctk.CTkLabel(frame, text="Trim Date:", font=("Arial", 18)).grid(row=1, column=0, sticky="e", padx=(6,6), pady=8)
        self.TrimDateEntry = DateEntry(frame, width=18, font=("Arial", 18), date_pattern='yyyy-mm-dd',
                                        background='#343638', foreground='#DCE4EE', 
                                        fieldbackground='#343638', borderwidth=2)
        self.TrimDateEntry.grid(row=1, column=1, sticky="w", pady=8)
        # Additional styling for the entry widget inside DateEntry
        try:
            self.TrimDateEntry.entry.configure(bg='#343638', fg='#DCE4EE', insertbackground='#DCE4EE')
        except Exception:
            pass
        self.TrimDateEntry.bind("<<DateEntrySelected>>", lambda e: self.OnFilterChanged())

        ctk.CTkLabel(frame, text="AM Flower:", font=DEFAULT_FONT).grid(row=1, column=2, sticky="e", padx=(6,6), pady=8)
        self.AmFlowerEntry = ctk.CTkEntry(frame, width=120)
        self.AmFlowerEntry.grid(row=1, column=3, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="AM Smalls:", font=DEFAULT_FONT).grid(row=1, column=4, sticky="e", padx=(6,6), pady=8)
        self.AmSmallsEntry = ctk.CTkEntry(frame, width=120)
        self.AmSmallsEntry.grid(row=1, column=5, sticky="w", pady=8)

        # Row 2: PM entries and Save button
        ctk.CTkLabel(frame, text="PM Flower:", font=DEFAULT_FONT).grid(row=2, column=2, sticky="e", padx=(6,6), pady=8)
        self.PmFlowerEntry = ctk.CTkEntry(frame, width=120)
        self.PmFlowerEntry.grid(row=2, column=3, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="PM Smalls:", font=DEFAULT_FONT).grid(row=2, column=4, sticky="e", padx=(6,6), pady=8)
        self.PmSmallsEntry = ctk.CTkEntry(frame, width=120)
        self.PmSmallsEntry.grid(row=2, column=5, sticky="w", pady=8)

        self.SaveButton = ctk.CTkButton(frame, text="Save", command=self.OnSave)
        self.SaveButton.grid(row=2, column=6, sticky="w", padx=(8,0), pady=8)

        # Row 3: Treeview
        cols = ("TrimmerName", "TrimDate", "CropNo", "Strain", "AmPm", "FlowerGrams", "SmallsGrams")
        self.Tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.Tree.heading(c, text=c)
            if c in ("CropNo", "FlowerGrams", "SmallsGrams"):
                self.Tree.column(c, width=80, anchor="center")
            elif c in ("TrimType", "AmPm"):
                self.Tree.column(c, width=100, anchor="center")
            else:
                self.Tree.column(c, width=150, anchor="w")
        self.Tree.grid(row=3, column=0, columnspan=7, sticky="nsew", pady=(8,0))

        # Status and Close button
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=7, sticky="ew", pady=(8,0))
        
        self.Status = ctk.CTkLabel(button_frame, text="", font=("Arial", 12), text_color="#00aa00")
        self.Status.pack(side="left", padx=(4,8))
        
        ctk.CTkButton(button_frame, text="Close", command=self.destroy, width=100).pack(side="right", padx=(6,0))

        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(3, weight=1)

        # Load initial data
        self.LoadCrops()
        self.LoadTrimmers()

    def SetStatus(self, text: str):
        try:
            self.Status.configure(text=text)
        except Exception:
            pass

    def LoadCrops(self):
        try:
            crops = SubSupa.LoadCrops() or []
            self.CropNoCombo.configure(values=crops)
            self.CropNoCombo.set('Select')
        except Exception as e:
            self.SetStatus(f"LoadCrops failed: {e}")

    def LoadTrimmers(self):
        try:
            trimmers = SubSupa.LoadTrimmers() or []
            self.TrimmerNameCombo.configure(values=trimmers)
            self.TrimmerNameCombo.set('Select')
        except Exception as e:
            self.SetStatus(f"LoadTrimmers failed: {e}")

    def OnCropChanged(self, choice=None):
        crop_val = (self.CropNoCombo.get() or '').strip()
        if not crop_val or crop_val.lower().startswith('select'):
            return
        
        # Parse CropNo from format "CropNo - Date"
        try:
            crop_no = int(crop_val.split('-')[0].strip())
        except Exception:
            self.SetStatus(f"Could not parse CropNo from '{crop_val}'")
            return

        try:
            strains = SubSupa.LoadStrains(crop_no) or []
            self.StrainCombo.configure(values=strains)
            self.StrainCombo.set('Select')
        except Exception as e:
            self.SetStatus(f"LoadStrains failed: {e}")

        self.OnFilterChanged()

    def OnFilterChanged(self):
        trimmer = (self.TrimmerNameCombo.get() or '').strip()
        if not trimmer or trimmer.lower().startswith('select'):
            return

        trim_date = self.TrimDateEntry.get_date().strftime('%Y-%m-%d')
        
        crop_val = (self.CropNoCombo.get() or '').strip()
        if not crop_val or crop_val.lower().startswith('select'):
            crop_no = None
        else:
            try:
                crop_no = int(crop_val.split('-')[0].strip())
            except Exception:
                crop_no = None

        strain = (self.StrainCombo.get() or '').strip()
        if not strain or strain.lower().startswith('select'):
            strain = None

        self.LoadTreeview(trimmer, trim_date, crop_no, strain)

    def LoadTreeview(self, trimmer_name: str, trim_date: str, crop_no=None, strain=None):
        try:
            rows = SubSupa.GetOneTrimDay(trimmer_name, trim_date, crop_no, strain) or []
        except Exception as e:
            self.SetStatus(f"GetOneTrimDay failed: {e}")
            rows = []

        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        for r in rows:
            if isinstance(r, dict):
                vals = (
                    str(r.get('TrimmerName', '')),
                    str(r.get('TrimDate', '')),
                    str(r.get('CropNo', '')),
                    str(r.get('Strain', '')),
                    str(r.get('AmPm', '')),
                    str(r.get('FlowerGrams', '')),
                    str(r.get('SmallsGrams', ''))
                )
            else:
                vals = (
                    str(getattr(r, 'TrimmerName', '')),
                    str(getattr(r, 'TrimDate', '')),
                    str(getattr(r, 'CropNo', '')),
                    str(getattr(r, 'Strain', '')),
                    str(getattr(r, 'AmPm', '')),
                    str(getattr(r, 'FlowerGrams', '')),
                    str(getattr(r, 'SmallsGrams', ''))
                )
            self.Tree.insert('', 'end', values=vals)

        self.SetStatus(f"Loaded {len(rows)} trim records")

    def OnSave(self):
        trimmer = (self.TrimmerNameCombo.get() or '').strip()
        if not trimmer or trimmer.lower().startswith('select'):
            messagebox.showwarning("Select Trimmer", "Please select a trimmer")
            return

        trim_date = self.TrimDateEntry.get_date().strftime('%Y-%m-%d')

        crop_val = (self.CropNoCombo.get() or '').strip()
        if not crop_val or crop_val.lower().startswith('select'):
            messagebox.showwarning("Select Crop", "Please select a crop")
            return

        try:
            crop_no = int(crop_val.split('-')[0].strip())
        except Exception:
            messagebox.showwarning("Invalid Crop", "Could not parse CropNo")
            return

        strain = (self.StrainCombo.get() or '').strip()
        if not strain or strain.lower().startswith('select'):
            messagebox.showwarning("Select Strain", "Please select a strain")
            return

        # Save AM Flower and smalls
        try:
            am_flower = float(self.AmFlowerEntry.get() or '0')
            am_smalls = float(self.AmSmallsEntry.get() or '0')
            if am_flower > 0 or am_smalls > 0:
                SubSupa.UpdateDailyTrim(trimmer, trim_date, crop_no, strain, am_flower, am_smalls, "Morning")
        except ValueError:
            pass
        except Exception as e:
            self.SetStatus(f"Save AM Flower failed: {e}")

        # Save PM Flower and smalls
        try:
            pm_flower = float(self.PmFlowerEntry.get() or '0')
            pm_smalls = float(self.PmSmallsEntry.get() or '0')
            if pm_flower > 0 or pm_smalls > 0:
                SubSupa.UpdateDailyTrim(trimmer, trim_date, crop_no, strain, pm_flower, pm_smalls, "Afternoon")
        except ValueError:
            pass
        except Exception as e:
            self.SetStatus(f"Save PM Flower failed: {e}")

        self.SetStatus("Saved daily trim records")
        
        # Clear entries
        self.AmFlowerEntry.delete(0, 'end')
        self.PmFlowerEntry.delete(0, 'end')
        self.AmSmallsEntry.delete(0, 'end')
        self.PmSmallsEntry.delete(0, 'end')

        # Reload treeview
        self.LoadTreeview(trimmer, trim_date, crop_no, strain)


def main():
    app = EnterDailyTrimApp()
    app.mainloop()
    restart_menu()


if __name__ == '__main__':
    main()
