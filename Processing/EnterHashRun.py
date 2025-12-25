import customtkinter as ctk
from tkinter import ttk, messagebox
import re
from datetime import datetime
import SubSupa
import SubPrintLabels
import os
import sys
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)  # this is the "scale" folder
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
import Common.SubScale as SubScale

# Connect to hardware after imports
SubScale.ConnectScales()

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "Enter Hash Run"
DEFAULT_FONT = ("Arial", 15)
POLL_INTERVAL_MS = 500


class EnterHashRunApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x520")

        # Set customtkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Configure ttk.Treeview style (still needed for treeview)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("Treeview", 
                       background="#2b2b2b",
                       foreground="#dce4ee",
                       fieldbackground="#2b2b2b",
                       borderwidth=0,
                       font=("Arial", 15))
        style.configure("Treeview.Heading", 
                       background="#1f538d",
                       foreground="#dce4ee",
                       borderwidth=1,
                       font=("Arial", 15, "bold"))
        style.map("Treeview", background=[("selected", "#144870")])

        # --- Section 2: Record start/end weights for runs ---
        ctk.CTkLabel(frame, text="Batch:", font=DEFAULT_FONT).grid(row=0, column=0, sticky="e", padx=(6,6), pady=8)
        self.BatchIdCombo = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.OnBatchChanged())
        self.BatchIdCombo.grid(row=0, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Run No:", font=DEFAULT_FONT).grid(row=0, column=2, sticky="e", padx=(6,6), pady=8)
        self.RunNoCombo = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=140, font=DEFAULT_FONT, command=lambda choice: self.OnRunChanged())
        self.RunNoCombo.grid(row=0, column=3, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Crop No:", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6), pady=8)
        self.CropNoCombo = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.OnCropChanged())
        self.CropNoCombo.grid(row=1, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Strain:", font=DEFAULT_FONT).grid(row=1, column=2, sticky="e", padx=(6,6), pady=8)
        self.StrainCombo = ctk.CTkComboBox(frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT)
        self.StrainCombo.grid(row=1, column=3, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Source:", font=DEFAULT_FONT).grid(row=1, column=4, sticky="e", padx=(6,6), pady=8)
        self.SourceCombo = ctk.CTkComboBox(
            frame, values=["Select", "Trim", "Flower", "Smalls"], state="readonly", width=160, font=DEFAULT_FONT)
        self.SourceCombo.grid(row=1, column=5, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Weigh Type:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(6,6), pady=8)
        self.WeighTypeEntry = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT)
        self.WeighTypeEntry.grid(row=2, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Weight (g):", font=DEFAULT_FONT).grid(row=2, column=2, sticky="e", padx=(6,6), pady=8)
        # WeightEntry will be updated by scale polling
        self.WeightEntry = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT)
        self.WeightEntry.grid(row=2, column=3, sticky="w", pady=8)

        self.SaveButton = ctk.CTkButton(frame, text="Save", font=DEFAULT_FONT, command=self.OnSave)
        self.SaveButton.grid(row=2, column=4, sticky="w", padx=(8,0), pady=8)
        # Print label for selected batch/run
        self.PrintLabelButton = ctk.CTkButton(frame, text="Print Label", font=DEFAULT_FONT, command=self.OnPrintLabel)
        self.PrintLabelButton.grid(row=2, column=5, sticky="w", padx=(8,0), pady=8)

        # --- Section 3: Treeview of runs ---
        cols = ("CropNo", "RunNo", "Strain", "Source", "StartWeight", "EndWeight")
        self.Tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.Tree.heading(c, text=c)
            if c in ("RunNo", "CropNo"):
                self.Tree.column(c, width=15, anchor="center")
            elif c in ("StartWeight", "EndWeight"):
                self.Tree.column(c, width=15, anchor="e")
            elif c in ("Source"):
                self.Tree.column(c, width=10, anchor="w")
            else:
                self.Tree.column(c, width=30, anchor="w")
        self.Tree.grid(row=3, column=0, columnspan=6, sticky="nsew", pady=(8,0))

        # status
        self.Status = ctk.CTkLabel(frame, text="", font=("Arial", 10))
        self.Status.grid(row=4, column=0, columnspan=5, sticky="w", pady=(8,0))

        # Close button
        self.CloseButton = ctk.CTkButton(frame, text="Close", font=DEFAULT_FONT, command=self.OnClose)
        self.CloseButton.grid(row=4, column=5, sticky="e", pady=(8,0))

        # --- Section 1: Create new batch (moved to bottom) ---
        ctk.CTkLabel(frame, text="New Batch ID:", font=DEFAULT_FONT).grid(row=5, column=0, sticky="e", padx=(6,6))
        self.NewBatchIdEntry = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT)
        self.NewBatchIdEntry.grid(row=5, column=1, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Batch Type:", font=DEFAULT_FONT).grid(row=5, column=2, sticky="e", padx=(6,6))
        # Batch type is usually "Hash" for this screen
        self.BatchTypeCombo = ctk.CTkComboBox(
            frame, values=["Hash"], state="readonly", width=200, font=DEFAULT_FONT)
        self.BatchTypeCombo.grid(row=5, column=3, sticky="w", pady=6)
        self.BatchTypeCombo.set("Hash")

        self.NewBatchButton = ctk.CTkButton(frame, text="New Batch", font=DEFAULT_FONT, command=self.OnNewBatch)
        self.NewBatchButton.grid(row=5, column=4, sticky="w", padx=(8,0))

        # layout expand
        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(3, weight=1)

        # polling state
        self._PollId = None
        self._PrevWeight = None

        # initial load
        self.LoadBatches()

        # start polling weight
        self.StartPolling()

        # ensure stop on close
        try:
            self.protocol("WM_DELETE_WINDOW", self.OnClose)
        except Exception:
            pass

    def SetStatus(self, text: str):
        try:
            self.Status.configure(text=text)
        except Exception:
            pass

    # --- Polling weight ---
    def StartPolling(self):
        self.PollWeight()

    def PollWeight(self):
        wstr = '0'
        try:
            w = SubScale.GetScoutWeight()
            wstr = str(w)
        except Exception as e:
            wstr = 'Error'
            print(f"Scale read failed: {e}")

        if wstr != self._PrevWeight:
            self._PrevWeight = wstr
            try:
                self.WeightEntry.configure(state='normal')
                self.WeightEntry.delete(0, 'end')
                self.WeightEntry.insert(0, wstr)
                self.WeightEntry.configure(state='disabled')
            except Exception:
                pass

        try:
            self._PollId = self.after(POLL_INTERVAL_MS, lambda: self.PollWeight())
        except Exception:
            self._PollId = None

    def StopPolling(self):
        try:
            if self._PollId:
                self.after_cancel(self._PollId)
                self._PollId = None
        except Exception:
            pass

    def OnClose(self):
        self.StopPolling()
        try:
            self.destroy()
        except Exception:
            pass

    # --- Batch and runs management ---
    def LoadBatches(self):
        try:
            rows = SubSupa.GetHashBatches("Hash") or []
            vals = rows if rows else ["Select"]
            self.BatchIdCombo.configure(values=vals)
            self.BatchIdCombo.set('Select')
            # reset downstream
            self.RunNoCombo.configure(values=['Select'])
            self.RunNoCombo.set('Select')
            self.CropNoCombo.configure(values=['Select'])
            self.CropNoCombo.set('Select')
            self.StrainCombo.configure(values=['Select'])
            self.StrainCombo.set('Select')
            self.SourceCombo.configure(values=['Select', 'Trim', 'Flower', 'Smalls'])
            self.SourceCombo.set('Select')
            self.WeighTypeEntry.configure(state='normal')
            self.WeighTypeEntry.delete(0, 'end')
            self.WeighTypeEntry.configure(state='disabled')
        except Exception as e:
            self.SetStatus(f"LoadBatches failed: {e}")

    def OnNewBatch(self):
        newId = (self.NewBatchIdEntry.get() or '').strip()
        btype = (self.BatchTypeCombo.get() or '').strip() or 'Hash'
        if not newId:
            messagebox.showwarning('New Batch', 'Please enter a batch id')
            return
        try:
            SubSupa.NewHashBatch(newId, btype)
            self.SetStatus(f'Inserted hash batch {newId} ({btype})')
            self.LoadBatches()
            # select new batch
            try:
                self.BatchIdCombo.set(newId)
            except Exception:
                pass
            # clear new batch entry so user can enter another
            try:
                self.NewBatchIdEntry.delete(0, 'end')
            except Exception:
                pass
        except Exception as e:
            self.SetStatus(f'NewHashBatch failed: {e}')

    def OnBatchChanged(self):
        batch = (self.BatchIdCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            return
        try:
            runNos = SubSupa.GetRunNos(batch) or []
            # include "New" option
            values = ['Select', 'New'] + [str(r) for r in runNos]
            self.RunNoCombo.configure(values=values)
            self.RunNoCombo.set('Select')
            # reset others
            self.CropNoCombo.configure(values=['Select'])
            self.CropNoCombo.set('Select')
            self.StrainCombo.configure(values=['Select'])
            self.StrainCombo.set('Select')
            self.SourceCombo.configure(values=['Select', 'Trim', 'Flower', 'Smalls'])
            self.SourceCombo.set('Select')
            self.WeighTypeEntry.configure(state='normal')
            self.WeighTypeEntry.delete(0, 'end')
            self.WeighTypeEntry.configure(state='normal')
            # load tree
            self.LoadRuns(batch)
        except Exception as e:
            self.SetStatus(f'GetRunNos failed: {e}')

    def OnRunChanged(self):
        batch = (self.BatchIdCombo.get() or '').strip()
        runVal = (self.RunNoCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            return
        if not runVal or runVal.lower().startswith('select'):
            return

        if runVal == 'New':
            try:
                newRun = SubSupa.GetNewRunNo(batch)
            except Exception as e:
                self.SetStatus(f'GetNewRunNo failed: {e}')
                return
            try:
                SubSupa.InsertHashRun(batch, newRun)
                self.SetStatus(f'Inserted new run {newRun} for {batch}')
            except Exception as e:
                self.SetStatus(f'InsertHashRun failed: {e}')
                return
            # init fields
            cropNo = 0
            strain = ''
            source = ''
            startW = 0
            endW = 0
            # refresh run list
            self.OnBatchChanged()
            # select the new run in combobox
            try:
                self.RunNoCombo.set(str(newRun))
            except Exception:
                pass
        else:
            try:
                rec = SubSupa.GetRunRec(batch, runVal) or {}
                # expected rec contains keys: CropNo, Strain, Source, StartWeight, EndWeight
                cropNo = rec.get('CropNo') if isinstance(rec, dict) else getattr(rec, 'CropNo', None)
                strain = rec.get('Strain') if isinstance(rec, dict) else getattr(rec, 'Strain', None)
                source = rec.get('Source') if isinstance(rec, dict) else getattr(rec, 'Source', None)
                startW = rec.get('StartWeight') if isinstance(rec, dict) else getattr(rec, 'StartWeight', None)
                endW = rec.get('EndWeight') if isinstance(rec, dict) else getattr(rec, 'EndWeight', None)
            except Exception as e:
                self.SetStatus(f'GetRunRec failed: {e}')
                return

        # populate crop/strain/source combos
        try:
            if not cropNo or int(cropNo) == 0:
                crops = SubSupa.LoadCrops() or ['Select']
                self.CropNoCombo.configure(values=crops)
                self.CropNoCombo.set('Select')
                self.StrainCombo.configure(values=['Select'])
                self.StrainCombo.set('Select')
                self.SourceCombo.configure(values=['Select', 'Trim', 'Flower', 'Smalls'])
                self.SourceCombo.set('Select')
            else:
                # show specific crop and strain
                try:
                    self.CropNoCombo.configure(values=[str(cropNo)])
                    self.CropNoCombo.set(str(cropNo))
                except Exception:
                    pass
                try:
                    self.StrainCombo.configure(values=[strain or ''])
                    self.StrainCombo.set(strain or '')
                except Exception:
                    pass
                try:
                    self.SourceCombo.configure(values=[source or ''])
                    self.SourceCombo.set(source or '')
                except Exception:
                    pass

        except Exception:
            pass

        # decide weigh type
        self.WeighTypeEntry.configure(state='normal')
        try:
            sw = startW or 0
            if int(sw) == 0:
                self.WeighTypeEntry.delete(0, 'end')
                self.WeighTypeEntry.insert(0, 'Start')
            else:
                self.WeighTypeEntry.delete(0, 'end')
                self.WeighTypeEntry.insert(0, 'End')
        except Exception:
            try:
                self.WeighTypeEntry.delete(0, 'end')
            except Exception:
                pass
        self.WeighTypeEntry.configure(state='disabled')

        # refresh tree for this batch
        try:
            self.LoadRuns(batch)
        except Exception:
            pass

    def OnCropChanged(self):
        try:
            token = (self.CropNoCombo.get() or '').strip()
            if not token or token.lower().startswith('select'):
                return
            try:
                crop_no = int(token.split()[0])
            except Exception:
                try:
                    crop_no = int(token)
                except Exception:
                    self.SetStatus('Cannot parse Crop number')
                    return
            strains = SubSupa.LoadStrains(crop_no) or ['Select']
            self.StrainCombo.configure(values=strains)
            self.StrainCombo.set('Select')
        except Exception as e:
            self.SetStatus(f'LoadStrains failed: {e}')

    def OnSave(self):
        batch = (self.BatchIdCombo.get() or '').strip()
        runVal = (self.RunNoCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            messagebox.showwarning('Select Batch', 'Please select a batch')
            return
        if not runVal or runVal.lower().startswith('select'):
            messagebox.showwarning('Select Run', 'Please select a run')
            return

        cropVal = (self.CropNoCombo.get() or '').strip()
        # CropNoCombo may contain "<CropNo> - <HarvestDate>"; extract the integer CropNo
        cropInt = 0
        if cropVal and not cropVal.lower().startswith('select'):
            token = cropVal.split('-')[0].strip()
            try:
                cropInt = int(token.split()[0])
            except Exception:
                try:
                    cropInt = int(token)
                except Exception:
                    cropInt = 0

        strainVal = (self.StrainCombo.get() or '').strip()
        sourceVal = (self.SourceCombo.get() or '').strip()
        weighType = (self.WeighTypeEntry.get() or '').strip()
        weightVal = (self.WeightEntry.get() or '').strip()

        try:
            w = float(weightVal)
        except Exception:
            messagebox.showwarning('Weight', 'Please enter a valid numeric weight')
            return

        try:
            if weighType.lower() == 'start':
                # SaveHashStartWeight(BatchId, RunNo, CropNo, Source, Strain, Weight)
                SubSupa.SaveHashStartWeight(batch, runVal, cropInt or 0, strainVal or '', sourceVal or '', w)
                self.SetStatus(f'Saved start weight for run {runVal} in {batch}')
            else:
                # SaveHashEndWeight(BatchId, RunNo, Weight)
                SubSupa.SaveHashEndWeight(batch, runVal, w)
                self.SetStatus(f'Saved end weight for run {runVal} in {batch}')
        except Exception as e:
            self.SetStatus(f'Save failed: {e}')
            return

        # refresh runs
        try:
            self.LoadRuns(batch)
        except Exception:
            pass

        # clear weigh type and weight so user can proceed
        try:
            self.WeighTypeEntry.configure(state='normal')
            self.WeighTypeEntry.delete(0, 'end')
            self.WeighTypeEntry.configure(state='disabled')
        except Exception:
            pass

    def OnPrintLabel(self):
        # Print a label for the currently selected batch using SubPrintLabels.PrintLabel
        batch = (self.BatchIdCombo.get() or '').strip()
        runVal = (self.RunNoCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            messagebox.showwarning('Select Batch', 'Please select a batch to print')
            return

        (BatchDate, NumStrains, Strain1, Strain2, Strain3, Strain4, TotalGrams) = SubSupa.GetHashLabelData(batch)

        try:
            SubPrintLabels.PrintLabel(batch, 'Hash', BatchDate, Strain1, Strain2, Strain3, Strain4, TotalGrams)
            self.SetStatus(f'Printed label for {batch}')
        except Exception as e:
            self.SetStatus(f'Print label failed: {e}')

    def LoadRuns(self, batchId: str):
        try:
            rows = SubSupa.GetRuns(batchId) or []
        except Exception as e:
            self.SetStatus(f'GetRuns failed: {e}')
            rows = []

        # clear tree
        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        for r in rows:
            if isinstance(r, dict):
                runno = r.get('RunNo')
                cropno = r.get('CropNo')
                strain = r.get('Strain')
                source = r.get('Source')
                sw = r.get('StartWeight')
                ew = r.get('EndWeight')
            else:
                runno = getattr(r, 'RunNo', '')
                cropno = getattr(r, 'CropNo', '')
                strain = getattr(r, 'Strain', '')
                source = getattr(r, 'Source', '')
                sw = getattr(r, 'StartWeight', '')
                ew = getattr(r, 'EndWeight', '')
            vals = (str(cropno or ''), str(runno or ''), str(strain or ''), str(source or ''), str(sw or ''), str(ew or ''))
            self.Tree.insert('', 'end', values=vals)

        self.SetStatus(f'Loaded {len(rows)} runs for {batchId}')


def main():
    app = EnterHashRunApp()
    app.mainloop()
    restart_menu()


if __name__ == '__main__':
    main()
