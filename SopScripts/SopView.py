#!/usr/bin/env python3
"""
Sops.py — SOP selector & viewer launcher.

Folder conventions:
  scale/
    Sops.py
    sop/
      Harvest/
        WeighHarvest.md
        ...
        manifest.json   (optional)
      Packaging/
      ...

Ordering + description:
  Preferred: manifest.json in each activity folder
  Optional: Supabase table (see SUPABASE_* env vars and TABLE_SCHEMA notes below)

Viewer:
  Uses scale/Common/SopViewer.py (adapter tries common class/function patterns).
"""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import Supabase SOP functions
SCALE_DIR = Path(__file__).resolve().parent.parent  # Go up to scale/ directory
#sys.path.insert(0, str(SCALE_DIR / "Common"))
from SubSopSupa import GetSopActivities, GetOneSopFile, InsertSopIndex


# ----------------------------
# Paths / Constants
# ----------------------------

SOP_ROOT = SCALE_DIR / "sop"
DEFAULT_FONT = ("Arial", 14)

# Get activity order from database
try:
    DEFAULT_ACTIVITY_ORDER = GetSopActivities()
except Exception:
    # Fallback if database is not available
    DEFAULT_ACTIVITY_ORDER = [
        "Harvest",
        "Trimmers",
        "Packaging",
        "Processing",
    ]

# Manifest filename inside each activity folder
MANIFEST_NAME = "manifest.json"

# Supabase env vars (optional)
SUPABASE_URL_ENV = "SUPABASE_URL"
SUPABASE_KEY_ENV = "SUPABASE_SERVICE_KEY"  # you said you use service key
SUPABASE_TABLE_ENV = "SOP_INDEX_TABLE"     # optional override; default below
DEFAULT_SUPABASE_TABLE = "sop_index"


# ----------------------------
# Data model
# ----------------------------

@dataclass(frozen=True)
class SopItem:
    activity: str
    title: str
    filename: str              # relative to activity folder
    description: str = ""
    sort_order: int = 9999
    enabled: bool = True

    @property
    def md_path(self) -> Path:
        return SOP_ROOT / self.activity / self.filename


# ----------------------------
# Supabase (optional)
# ----------------------------

def _supabase_available() -> bool:
    return bool(os.getenv(SUPABASE_URL_ENV)) and bool(os.getenv(SUPABASE_KEY_ENV))


def _load_from_supabase() -> Optional[List[SopItem]]:
    """
    Optional table-driven hierarchy.

    TABLE_SCHEMA suggestion (Postgres):
      create table sop_index (
        id bigserial primary key,
        activity text not null,
        title text not null,
        filename text not null,
        description text default '',
        sort_order int default 0,
        enabled boolean default true
      );

    Notes:
      - activity should match folder name under scale/sop (e.g. 'Harvest')
      - filename should be the .md file name (e.g. 'WeighHarvest.md')
    """
    if not _supabase_available():
        return None

    try:
        # Prefer supabase-py if installed
        from supabase import create_client  # type: ignore
    except Exception:
        # No client library installed on this machine
        return None

    url = os.getenv(SUPABASE_URL_ENV, "").strip()
    key = os.getenv(SUPABASE_KEY_ENV, "").strip()
    table = os.getenv(SUPABASE_TABLE_ENV, DEFAULT_SUPABASE_TABLE).strip()

    try:
        client = create_client(url, key)
        # Pull enabled rows, ordered by activity then sort_order then title
        resp = (
            client.table(table)
            .select("activity,title,filename,description,sort_order,enabled")
            .eq("enabled", True)
            .order("activity")
            .order("sort_order")
            .order("title")
            .execute()
        )
        rows = resp.data or []
        items: List[SopItem] = []
        for r in rows:
            items.append(
                SopItem(
                    activity=str(r.get("activity", "")).strip(),
                    title=str(r.get("title", "")).strip(),
                    filename=str(r.get("filename", "")).strip(),
                    description=str(r.get("description", "") or "").strip(),
                    sort_order=int(r.get("sort_order", 9999) or 9999),
                    enabled=bool(r.get("enabled", True)),
                )
            )
        # Basic sanity: only keep items that actually exist on disk
        items = [it for it in items if it.activity and it.filename and it.md_path.exists()]
        return items
    except Exception:
        # If Supabase errors out, fall back to local discovery
        return None


# ----------------------------
# Local discovery + manifest
# ----------------------------

def _list_activity_folders() -> List[str]:
    if not SOP_ROOT.exists():
        return []
    acts = [p.name for p in SOP_ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")]
    # Apply preferred ordering
    ordered: List[str] = []
    for a in DEFAULT_ACTIVITY_ORDER:
        if a in acts:
            ordered.append(a)
    for a in sorted(acts):
        if a not in ordered:
            ordered.append(a)
    return ordered


def _load_manifest(activity: str) -> Optional[List[SopItem]]:
    """
    Manifest format (scale/sop/<Activity>/manifest.json):

    {
      "activity": "Harvest",
      "sops": [
        {
          "title": "Weigh Plants (Wet & Dry)",
          "filename": "WeighHarvest.md",
          "description": "Use Ohaus Ranger + app to weigh plants; print labels; save to Supabase.",
          "sort_order": 10,
          "enabled": true
        }
      ]
    }
    """
    act_dir = SOP_ROOT / activity
    mf = act_dir / MANIFEST_NAME
    if not mf.exists():
        return None

    try:
        data = json.loads(mf.read_text(encoding="utf-8"))
        sops = data.get("sops", [])
        items: List[SopItem] = []
        for s in sops:
            item = SopItem(
                activity=activity,
                title=str(s.get("title", "")).strip(),
                filename=str(s.get("filename", "")).strip(),
                description=str(s.get("description", "") or "").strip(),
                sort_order=int(s.get("sort_order", 9999) or 9999),
                enabled=bool(s.get("enabled", True)),
            )
            # Only list enabled + existing files
            if item.enabled and item.title and item.filename and item.md_path.exists():
                items.append(item)
        items.sort(key=lambda x: (x.sort_order, x.title.lower()))
        return items
    except Exception:
        return None


def _discover_md_files(activity: str) -> List[SopItem]:
    """
    Fallback if no manifest + no Supabase:
      - list *.md in the activity folder
      - Check database for each file; insert if missing
      - title defaults to filename without extension
      - description from database
      - sort_order from database
    """
    act_dir = SOP_ROOT / activity
    if not act_dir.exists():
        return []

    md_files = sorted([p for p in act_dir.glob("*.md") if p.is_file()])
    items: List[SopItem] = []
    for idx, p in enumerate(md_files):
        # Check if file exists in database
        try:
            print(f"Checking SOP file in DB: Activity={activity}, FileName={p.name}")   
            db_record = GetOneSopFile(activity, p.name)
#            print(f"DB record: {db_record}")
            if db_record is None:
                # File not in database, insert it
                InsertSopIndex(activity, 99, p.name, "")
                # Use default values
                items.append(
                    SopItem(
                        activity=activity,
                        title=p.stem.replace("_", " ").strip(),
                        filename=p.name,
                        description="",
                        sort_order=99,
                        enabled=True,
                    )
                )
            else:
                # Use values from database
                items.append(
                    SopItem(
                        activity=activity,
                        title=db_record.get("Descr", "") or p.stem.replace("_", " ").strip(),
                        filename=p.name,
                        description=db_record.get("Descr", "") or "",
                        sort_order=int(db_record.get("SeqNo", 99) or 99),
                        enabled=True,
                    )
                )
        except Exception:
            # If database call fails, use defaults
            items.append(
                SopItem(
                    activity=activity,
                    title=p.stem.replace("_", " ").strip(),
                    filename=p.name,
                    description="",
                    sort_order=idx,
                    enabled=True,
                )
            )
    # Sort by sort_order then title
    items.sort(key=lambda x: (x.sort_order, x.title.lower()))
    return items


def load_sop_index() -> Tuple[List[str], Dict[str, List[SopItem]]]:
    """
    Returns:
      activities: list of activity names
      by_activity: mapping activity -> list of SopItem (sorted)
    """
    # 1) Try Supabase index
    supa_items = _load_from_supabase()
    if supa_items:
        by: Dict[str, List[SopItem]] = {}
        for it in supa_items:
            by.setdefault(it.activity, []).append(it)
        # sort within activities
        for a in by:
            by[a].sort(key=lambda x: (x.sort_order, x.title.lower()))
        activities = _list_activity_folders()
        # Keep only activities with at least one SOP from the table
        activities = [a for a in activities if a in by]
        # Add any activities from Supabase that aren't present as folders (rare), but keep them too
        for a in sorted(by.keys()):
            if a not in activities:
                activities.append(a)
        return activities, by

    # 2) Local manifests / discovery
    activities = _list_activity_folders()
    by_activity: Dict[str, List[SopItem]] = {}
    for a in activities:
        items = _load_manifest(a)
        if items is None:
            items = _discover_md_files(a)
        by_activity[a] = items
    return activities, by_activity


# ----------------------------
# SopViewer adapter
# ----------------------------

def open_sop_in_viewer(md_path: Path, title: Optional[str] = None) -> None:
    """
    Launch Common/SopViewer.py as a subprocess to display the SOP.
    """
    import subprocess
    
    viewer_py = SCALE_DIR / "common" / "SopViewer.py"
    
    if not viewer_py.exists():
        raise RuntimeError(f"SopViewer.py not found at: {viewer_py}")
    
    # Launch separate process (non-blocking)
    subprocess.Popen(
        [sys.executable, str(viewer_py), str(md_path)],
        cwd=str(SCALE_DIR),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
    )


# ----------------------------
# UI (CustomTkinter)
# ----------------------------

class SopViewApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SOPs")
        self.geometry("400x680")
        self.resizable(False, False)

        # Set customtkinter appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Load data
        self.activities, self.by_activity = load_sop_index()

        if not self.activities:
            raise RuntimeError(f"No activities found. Expected folders under: {SOP_ROOT}")

        self.current_activity = ctk.StringVar(value=self.activities[0])
        self.setup_ui()

    def get_items_for_activity(self, act: str) -> List[SopItem]:
        return self.by_activity.get(act, [])

    def refresh_list(self, *_args) -> None:
        self.sop_list.delete(0, "end")

        act = self.current_activity.get()
        items = self.get_items_for_activity(act)
        for it in items:
            self.sop_list.insert("end", it.title)

    def open_selected(self) -> None:
        act = self.current_activity.get()
        items = self.get_items_for_activity(act)
        sel = self.sop_list.curselection()
        if not sel:
            return
        it = items[int(sel[0])]
        if not it.md_path.exists():
            messagebox.showwarning("Missing File", f"File not found:\n{it.md_path}")
            return
        open_sop_in_viewer(it.md_path, title=it.title)

    def setup_ui(self) -> None:
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        # Header
        header = ctk.CTkLabel(main, text="Standard Operating Procedures", font=("Arial", 18, "bold"))
        header.grid(row=0, column=0, pady=(0, 12))

        # Configure grid
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # Content frame
        content = ctk.CTkFrame(main)
        content.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        # Activity selector + list
        ctk.CTkLabel(content, text="Activity", font=("Arial", 16, "bold")).pack(
            padx=12, pady=(12, 6), anchor="w"
        )
        activity_menu = ctk.CTkOptionMenu(
            content, 
            values=self.activities, 
            variable=self.current_activity, 
            command=lambda _: self.refresh_list(),
            font=DEFAULT_FONT
        )
        activity_menu.pack(padx=12, pady=(0, 12), fill="x")

        ctk.CTkLabel(content, text="SOPs", font=("Arial", 16, "bold")).pack(
            padx=12, pady=(6, 6), anchor="w"
        )

        # CTkScrollableFrame for SOP list
        list_frame = ctk.CTkScrollableFrame(content, height=450, width=300)
        list_frame.pack(padx=12, pady=(0, 12), fill="both", expand=True)
        
        self.sop_list = CTkListbox(list_frame, on_click_opens=True)
        self.sop_list.bind("<<ListboxSelect>>", lambda e: self.open_selected())

        # Exit button
        exit_btn = ctk.CTkButton(main, text="Exit", command=self.destroy, font=DEFAULT_FONT)
        exit_btn.grid(row=99, column=0, sticky="e", pady=12)

        self.refresh_list()


class CTkListbox:
    """Custom listbox implementation using CTk widgets."""
    def __init__(self, parent, on_click_opens=False):
        self.parent = parent
        self.buttons = []
        self.selected_idx = None
        self.on_select_callback = None
        self.on_click_opens = on_click_opens
        
    def delete(self, start, end):
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []
        self.selected_idx = None
        
    def insert(self, pos, text):
        idx = len(self.buttons)
        btn = ctk.CTkButton(
            self.parent,
            text=text,
            anchor="w",
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            font=DEFAULT_FONT,
            command=lambda i=idx: self._on_click(i)
        )
        btn.pack(fill="x", padx=2, pady=1)
        self.buttons.append(btn)
        
    def _on_click(self, idx):
        # Update selection
        if self.selected_idx is not None and self.selected_idx < len(self.buttons):
            self.buttons[self.selected_idx].configure(fg_color="transparent")
        self.selected_idx = idx
        self.buttons[idx].configure(fg_color=("gray75", "gray35"))
        if self.on_select_callback:
            self.on_select_callback(None)
            
    def curselection(self):
        if self.selected_idx is not None:
            return (self.selected_idx,)
        return ()
        
    def bind(self, event, callback):
        if event == "<<ListboxSelect>>":
            self.on_select_callback = callback


# ----------------------------
# Main
# ----------------------------

def main():
    app = SopViewApp()
    app.mainloop()


if __name__ == "__main__":
    main()
