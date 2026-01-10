#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import customtkinter as ctk
    USE_CTK = True
except Exception:
    USE_CTK = False


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp1252", errors="replace")


def open_default(path: Path):
    # Windows + mac + linux
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", str(path)])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        messagebox.showerror("Open failed", str(e))


def main():
    if len(sys.argv) < 2:
        print("Usage: SopViewer.py <path-to-md>")
        raise SystemExit(2)

    md_path = Path(sys.argv[1]).expanduser().resolve()
    title = md_path.stem.replace("_", " ")

    if USE_CTK:
        ctk.set_appearance_mode("System")
        root = ctk.CTk()
        root.title(f"SOP — {title}")
        root.geometry("900x750")

#        top = ctk.CTkFrame(root)
#        top.pack(fill="x", padx=10, pady=(10, 0))

#        lbl = ctk.CTkLabel(top, text=str(md_path), anchor="w")
#        lbl.pack(side="left", fill="x", expand=True, padx=(8, 8), pady=8)

#        btn_open = ctk.CTkButton(top, text="Open file", command=lambda: open_default(md_path))
#        btn_open.pack(side="right", padx=(0, 8), pady=8)

        box = ctk.CTkTextbox(root, wrap="word")
        box.pack(fill="both", expand=True, padx=10, pady=10)

        if md_path.exists():
            box.insert("1.0", read_text(md_path))
        else:
            box.insert("1.0", f"Missing SOP file:\n{md_path}")

        box.configure(state="disabled")
        root.mainloop()

    else:
        root = tk.Tk()
        root.title(f"SOP — {title}")
        root.geometry("900x750")

        frm = ttk.Frame(root)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        header = ttk.Frame(frm)
        header.pack(fill="x")

        ttk.Label(header, text=str(md_path)).pack(side="left", fill="x", expand=True)
        ttk.Button(header, text="Open file", command=lambda: open_default(md_path)).pack(side="right")

        txt = tk.Text(frm, wrap="word")
        txt.pack(fill="both", expand=True, pady=(10, 0))

        if md_path.exists():
            txt.insert("1.0", read_text(md_path))
        else:
            txt.insert("1.0", f"Missing SOP file:\n{md_path}")

        txt.configure(state="disabled")
        root.mainloop()


if __name__ == "__main__":
    main()
