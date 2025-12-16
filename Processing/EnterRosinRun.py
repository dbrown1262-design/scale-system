import customtkinter as ctk
from tkinter import ttk, messagebox
import SubSupa
import SubScale
import SubPrintLabels
import ctypes
import os
import sys
import subprocess

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)

APP_TITLE = "Enter Rosin Run"
DEFAULT_FONT = ("Arial", 15)
POLL_INTERVAL_MS = 500


class EnterRosinRunApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("990x480")

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

        # Section 2 - Weighing
        ctk.CTkLabel(frame, text="Batch:", font=DEFAULT_FONT).grid(row=1, column=0, sticky="e", padx=(6,6), pady=8)
        self.BatchIdCombo = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT, command=lambda choice: self.OnBatchChanged())
        self.BatchIdCombo.grid(row=1, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Run No:", font=DEFAULT_FONT).grid(row=1, column=2, sticky="e", padx=(6,6), pady=8)
        self.RunNoCombo = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=140, font=DEFAULT_FONT, command=lambda choice: self.OnRunChanged())
        self.RunNoCombo.grid(row=1, column=3, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Source:", font=DEFAULT_FONT).grid(row=1, column=4, sticky="e", padx=(6,6), pady=8)
        self.SourceCombo = ctk.CTkComboBox(
            frame, values=["Select"], state="readonly", width=200, font=DEFAULT_FONT)
        self.SourceCombo.grid(row=1, column=5, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Weigh Type:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="e", padx=(3,3), pady=8)
        self.WeighTypeEntry = ctk.CTkEntry(frame, width=160, font=DEFAULT_FONT)
        self.WeighTypeEntry.grid(row=2, column=1, sticky="w", pady=8)

        ctk.CTkLabel(frame, text="Weight (g):", font=DEFAULT_FONT).grid(row=2, column=2, sticky="e", padx=(6,6), pady=8)
        self.WeightEntry = ctk.CTkEntry(frame, width=140, font=DEFAULT_FONT)
        self.WeightEntry.grid(row=2, column=3, sticky="w", pady=8)

        self.SaveButton = ctk.CTkButton(frame, text="Save", font=DEFAULT_FONT, command=self.OnSave)
        self.SaveButton.grid(row=2, column=4, sticky="w", padx=(8,0))
        # Print label for selected batch/run
        self.PrintLabelButton = ctk.CTkButton(
            frame, text="Print Label", font=DEFAULT_FONT, command=self.OnPrintLabel)
        self.PrintLabelButton.grid(row=2, column=5, sticky="w", padx=(8,0), pady=8)

        # Section 3 - Treeview
        cols = ("RunNo", "Source", "StartWeight", "EndWeight")
        self.Tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for c in cols:
            self.Tree.heading(c, text=c)
            if c == "RunNo":
                self.Tree.column(c, width=80, anchor="center")
            elif c in ("StartWeight", "EndWeight"):
                self.Tree.column(c, width=120, anchor="center")
            else:
                self.Tree.column(c, width=220, anchor="w")
        self.Tree.grid(row=3, column=0, columnspan=7, sticky="nsew", pady=(8,0))

        # status
        self.Status = ctk.CTkLabel(frame, text="", font=("Arial", 15))
        self.Status.grid(row=4, column=0, columnspan=5, sticky="w", pady=(8,0))

        # Close button
        self.CloseButton = ctk.CTkButton(frame, text="Close", font=DEFAULT_FONT, command=self.OnClose)
        self.CloseButton.grid(row=4, column=5, sticky="e", pady=(8,0))

        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(3, weight=1)

        # Section 1 - New batch (moved to bottom)
        ctk.CTkLabel(frame, text="Batch ID:", font=DEFAULT_FONT).grid(row=5, column=0, sticky="e", padx=(6,6))
        self.NewBatchIdEntry = ctk.CTkEntry(frame, width=200, font=DEFAULT_FONT)
        self.NewBatchIdEntry.grid(row=5, column=1, sticky="w", pady=6)

#        ctk.CTkLabel(frame, text="Batch Type:", font=DEFAULT_FONT).grid(row=5, column=2, sticky="e", padx=(6,6))
#        self.BatchTypeCombo = ctk.CTkComboBox(frame, values=["Rosin"], state="readonly", width=180, font=DEFAULT_FONT)
#        self.BatchTypeCombo.grid(row=5, column=3, sticky="w", pady=6)
#        self.BatchTypeCombo.set("Rosin")

        self.NewBatchButton = ctk.CTkButton(
            frame, text="Add New Batch", font=DEFAULT_FONT, command=self.OnNewBatch)
        self.NewBatchButton.grid(row=5, column=2, sticky="w", padx=(8,0))

        # polling
        self._PollId = None
        self._PrevWeight = None

        # initial loads
        self.LoadBatches()
        self.StartPolling()

        try:
            self.protocol("WM_DELETE_WINDOW", self.OnClose)
        except Exception:
            pass

    def SetStatus(self, text: str):
        try:
            self.Status.configure(text=text)
        except Exception:
            pass

    def SetBusyCursor(self):
        """Set cursor to hourglass/wait cursor using Windows API."""
        print("Setting busy cursor")
        try:
            # Windows API approach: Load and set the wait cursor
            IDC_WAIT = 32514
            hCursor = ctypes.windll.user32.LoadCursorW(0, IDC_WAIT)
            ctypes.windll.user32.SetCursor(hCursor)
            self.update()
        except Exception as e:
            print(f"SetBusyCursor error: {e}")
            pass

    def SetNormalCursor(self):
        """Restore cursor to normal using Windows API."""
        try:
            # Windows API approach: Load and set the arrow cursor
            IDC_ARROW = 32512
            hCursor = ctypes.windll.user32.LoadCursorW(0, IDC_ARROW)
            ctypes.windll.user32.SetCursor(hCursor)
            self.update()
        except Exception as e:
            print(f"SetNormalCursor error: {e}")
            pass

    # Polling
    def StartPolling(self):
        self.PollWeight()

    def PollWeight(self):
        wstr = '0'
        try:
            if SubScale is not None:
                w = SubScale.GetWeight()
                wstr = str(w)
        except Exception:
            wstr = '0'

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

    # Loads
    def LoadBatches(self):
        try:
            rows = SubSupa.GetRosinBatches() or []
            print(rows)
#            vals = ["Select", "New"]
#            vals = vals.append(rows) if rows else ["Select", "New"]
#            print(vals)
            self.BatchIdCombo.configure(values=rows)
            self.BatchIdCombo.set('Select')
            # reset downstream
            self.RunNoCombo.configure(values=['Select'])
            self.RunNoCombo.set('Select')
            self.SourceCombo.configure(values=['Select'])
            self.SourceCombo.set('Select')
            # prepare weigh type
            try:
                self.WeighTypeEntry.configure(state='normal')
                self.WeighTypeEntry.delete(0, 'end')
                self.WeighTypeEntry.configure(state='disabled')
            except Exception:
                pass
        except Exception as e:
            self.SetStatus(f"LoadBatches failed: {e}")

    def OnNewBatch(self):
        newId = (self.NewBatchIdEntry.get() or '').strip()
        btype = 'Rosin'
        if not newId:
            messagebox.showwarning('New Batch', 'Please enter a batch id')
            return
        try:
            SubSupa.NewRosinBatch(newId, btype)
            self.SetStatus(f'Inserted rosin batch {newId} ({btype})')
            self.LoadBatches()
            try:
                self.BatchIdCombo.set(newId)
            except Exception:
                pass
            try:
                self.NewBatchIdEntry.delete(0, 'end')
            except Exception:
                pass
        except Exception as e:
            self.SetStatus(f'NewRosinBatch failed: {e}')

    def OnBatchChanged(self):
        batch = (self.BatchIdCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            return
        self.SetBusyCursor()

        try:
            runNos = SubSupa.GetRosinRunNos(batch) or []
            values = [str(r) for r in runNos]
            self.RunNoCombo.configure(values=values)
            self.RunNoCombo.set('Select')
            self.SourceCombo.configure(values=['Select'])
            self.SourceCombo.set('Select')
            try:
                self.WeighTypeEntry.configure(state='normal')
                self.WeighTypeEntry.delete(0, 'end')
                self.WeighTypeEntry.configure(state='disabled')
            except Exception:
                pass
            self.LoadRuns(batch)

        except Exception as e:
            self.SetStatus(f'GetRosinRunNos failed: {e}')
        self.SetNormalCursor()

    def OnRunChanged(self):
        batch = (self.BatchIdCombo.get() or '').strip()
        runVal = (self.RunNoCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            return
        if not runVal or runVal.lower().startswith('select'):
            return
        self.SetBusyCursor()
        if runVal == 'New':
            try:
                newRun = SubSupa.GetNewRosinRunNo(batch)
            except Exception as e:
                self.SetStatus(f'GetNewRosinRunNo failed: {e}')
                self.SetNormalCursor()
                return
            try:
                SubSupa.InsertRosinRun(batch, newRun)
                self.SetStatus(f'Inserted new rosin run {newRun} for {batch}')
            except Exception as e:
                self.SetStatus(f'InsertRosinRun failed: {e}')
                self.SetNormalCursor()
                return
            source = ''
            startW = 0
            endW = 0
            self.OnBatchChanged()
            self.RunNoCombo.set(str(newRun))
        else:
            try:
                rec = SubSupa.GetRosinRunRec(batch, runVal) or {}
                source = rec.get('Source') if isinstance(rec, dict) else getattr(rec, 'Source', None)
                startW = rec.get('StartWeight') if isinstance(rec, dict) else getattr(rec, 'StartWeight', None)
                endW = rec.get('EndWeight') if isinstance(rec, dict) else getattr(rec, 'EndWeight', None)
            except Exception as e:
                self.SetStatus(f'GetRosinRunRec failed: {e}')
                self.SetNormalCursor()
                return

        # determine weigh type and source options
        if not startW or int(startW) == 0:
            # enable and set Start
            sources = SubSupa.LoadSourceCombo() or ['Select']
            self.SourceCombo.configure(values=sources)
            self.SourceCombo.set('Select')
            self.WeighTypeEntry.configure(state='normal')
            self.WeighTypeEntry.delete(0, 'end')
            self.WeighTypeEntry.insert(0, 'Start')
            self.WeighTypeEntry.configure(state='disabled')
        else:
            # set source from record and set End
            self.SourceCombo.configure(values=[source or ''])
            self.SourceCombo.set(source or '')
            self.WeighTypeEntry.configure(state='normal')
            self.WeighTypeEntry.delete(0, 'end')
            self.WeighTypeEntry.insert(0, 'End')
            self.WeighTypeEntry.configure(state='disabled')

        self.LoadRuns(batch)
        self.SetNormalCursor()

    def OnSave(self):
        batch = (self.BatchIdCombo.get() or '').strip()
        runVal = (self.RunNoCombo.get() or '').strip()
        sourceVal = (self.SourceCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            messagebox.showwarning('Select Batch', 'Please select a batch')
            return
        if not runVal or runVal.lower().startswith('select'):
            messagebox.showwarning('Select Run', 'Please select a run')
            return
        if not sourceVal or sourceVal.lower().startswith('select'):
            messagebox.showwarning('Select Source', 'Please select a source')
            return
        weighType = (self.WeighTypeEntry.get() or '').strip()
        weightVal = (self.WeightEntry.get() or '').strip()

        try:
            w = float(weightVal)
        except Exception:
            messagebox.showwarning('Weight', 'Please enter a valid numeric weight')
            return

        self.SetBusyCursor()
        try:
            if weighType.lower() == 'start':
                SubSupa.SaveRosinStartWeight(batch, runVal, sourceVal or '', w)
                self.SetStatus(f'Saved start weight for run {runVal} in {batch}')
            else:
                SubSupa.SaveRosinEndWeight(batch, runVal, w)
                self.SetStatus(f'Saved end weight for run {runVal} in {batch}')
        except Exception as e:
            self.SetStatus(f'Save failed: {e}')
            self.SetNormalCursor()
            return

        self.LoadRuns(batch)
        self.WeighTypeEntry.configure(state='normal')
        self.WeighTypeEntry.delete(0, 'end')
        self.WeighTypeEntry.configure(state='disabled')
        self.LoadBatches()
        self.SetNormalCursor()


    def OnPrintLabel(self):
        # Print a label for the currently selected rosin batch/run using SubPrintLabels.PrintLabel
        batch = (self.BatchIdCombo.get() or '').strip()
        if not batch or batch.lower().startswith('select'):
            messagebox.showwarning('Select Batch', 'Please select a batch to print')
            return
        self.SetBusyCursor()
        (BatchDate, Strain1, Strain2, Strain3, Strain4, TotalGrams) = SubSupa.GetRosinLabelData(batch)

        try:
            SubPrintLabels.PrintLabel(batch, 'Rosin', BatchDate, Strain1, Strain2, Strain3, Strain4, TotalGrams)
            self.SetStatus(f'Printed rosin label for {batch}')
        except Exception as e:
            self.SetStatus(f'Print label failed: {e}')
        self.SetNormalCursor()

    def LoadRuns(self, batchId: str):
        try:
            rows = SubSupa.GetRosinRuns(batchId) or []
        except Exception as e:
            self.SetStatus(f'GetRosinRuns failed: {e}')
            rows = []

        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        for r in rows:
            if isinstance(r, dict):
                runno = r.get('RunNo')
                source = r.get('Source')
                sw = r.get('StartWeight')
                ew = r.get('EndWeight')
            else:
                runno = getattr(r, 'RunNo', '')
                source = getattr(r, 'Source', '')
                sw = getattr(r, 'StartWeight', '')
                ew = getattr(r, 'EndWeight', '')
            vals = (str(runno or ''), str(source or ''), str(sw or ''), str(ew or ''))
            self.Tree.insert('', 'end', values=vals)

        self.SetStatus(f'Loaded {len(rows)} runs for {batchId}')


def main():
    app = EnterRosinRunApp()
    app.mainloop()
    restart_menu()


if __name__ == '__main__':
    main()
