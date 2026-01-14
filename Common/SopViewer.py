#!/usr/bin/env python3
import sys
import os
import tempfile
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Renders markdown -> html
from markdown_it import MarkdownIt

# Displays html inside tkinter
from tkinterweb import HtmlFrame


CSS = """
<style>
  body {
    font-family: Segoe UI, Arial, sans-serif;
    line-height: 1.45;
    margin: 18px 22px;
    color: #eaeaea;
    background: #1e1e1e;
  }
  h1, h2, h3, h4 { color: #ffffff; margin-top: 1.2em; margin-bottom: 0.5em; }
  h1 { font-size: 24px; border-bottom: 1px solid #444; padding-bottom: 8px; }
  h2 { font-size: 20px; border-bottom: 1px solid #333; padding-bottom: 6px; }
  h3 { font-size: 16px; }
  p { margin: 0.55em 0; }
  h2 + ul, h2 + ol { margin-top: 0.2em; }
  ul, ol { margin: 0.4em 0 0.8em 1.3em; padding-left: 1.5em; }
  li { margin: 0; padding: 0; }
  code {
    font-family: Consolas, "Cascadia Mono", monospace;
    background: #2a2a2a;
    padding: 1px 5px;
    border-radius: 6px;
  }
  pre code {
    display: block;
    padding: 12px;
    overflow-x: auto;
    border-radius: 10px;
  }
  blockquote {
    margin: 0.8em 0;
    padding: 0.5em 1em;
    border-left: 4px solid #555;
    background: #232323;
  }
  a { color: #8ab4f8; text-decoration: none; }
  a:hover { text-decoration: underline; }

  table {
    border-collapse: collapse;
    margin: 0.8em 0;
    width: 100%;
  }
  th, td {
    border: 1px solid #444;
    padding: 8px 10px;
    vertical-align: top;
  }
  th {
    background: #2b2b2b;
    color: #fff;
  }
</style>
"""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp1252", errors="replace")


def print_sop_pdf(md_path: Path):
    """Convert markdown to PDF using pandoc and open for printing."""
    try:
        # Create PDF in temp directory
        tmpdir = tempfile.gettempdir()
        pdf_path = os.path.join(tmpdir, f"sop_{md_path.stem}.pdf")
        
        # Use pandoc with xelatex (from MiKTeX) to create PDF
        cmd = [
            "pandoc",
            str(md_path),
            "-o",
            pdf_path,
            "--pdf-engine=xelatex",
            "-V", "geometry:margin=0.75in",
            "-V", "fontsize=12pt",
            "-V", "linestretch=1.2",
            "-V", "header-includes=\\usepackage{enumitem}\\setlist{nosep,topsep=0pt,parsep=0pt,partopsep=0pt}",
            "--resource-path", str(md_path.parent),
        ]
        
        # Run pandoc
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc failed: {result.stderr}")
        
        # Open PDF with print dialog
        if sys.platform.startswith("win"):
            os.startfile(pdf_path, "print")
        elif sys.platform == "darwin":
            subprocess.run(["open", pdf_path], check=False)
        else:
            subprocess.run(["xdg-open", pdf_path], check=False)
            
    except FileNotFoundError:
        messagebox.showerror("Pandoc Not Found", 
            "Pandoc is required for PDF printing but was not found.\n\n"
            "Please ensure pandoc is installed and in your system PATH.")
    except Exception as e:
        messagebox.showerror("Print Error", f"Failed to create PDF:\n{e}")
        
        # Write HTML with print-friendly CSS
        print_css = """
<style>
  @media print {
    body { 
      color: #000; 
      background: #fff; 
      font-size: 14pt;
      line-height: 1.2;
    }
    h1, h2, h3, h4 { color: #000; }
    h1 { 
      border-bottom-color: #000; 
      font-size: 22pt;
      page-break-after: avoid;
    }
    h2 { 
      border-bottom-color: #333; 
      font-size: 22pt;
      page-break-after: avoid;
    }
    h3 { 
      font-size: 18pt;
      page-break-after: avoid;
    }
    h4 {
      font-size: 16pt;
      page-break-after: avoid;
    }
    p { font-size: 14pt; }
    li { font-size: 14pt; }
    h2 + ul, h2 + ol { margin-top: 0.2em; }
    ul, ol { margin-top: 0.2em; margin-bottom: 0.2em; }
    code { 
      background: #f0f0f0; 
      color: #000; 
      font-size: 12pt;
    }
    blockquote { 
      border-left-color: #000; 
      background: #f5f5f5; 
      font-size: 14pt;
    }
    a { color: #0066cc; }
    th, td { 
      border-color: #000; 
      font-size: 14pt;
    }
    th { background: #e0e0e0; color: #000; }
    table { page-break-inside: avoid; }
  }
  @page { margin: 0.75in; }
</style>
"""
        full_html = html_content.replace("</head>", f"{print_css}</head>")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        
        # Open the file with default browser for printing
        if sys.platform.startswith("win"):
            os.startfile(html_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", html_path], check=False)
        else:
            subprocess.run(["xdg-open", html_path], check=False)
        
        messagebox.showinfo("Print SOP", "SOP opened in browser. Use Ctrl+P or browser's Print menu to print.")
            
    except Exception as e:
        messagebox.showerror("Print Error", f"Failed to print SOP:\n{e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: SopViewer.py <path-to-md>")
        raise SystemExit(2)

    md_path = Path(sys.argv[1]).expanduser().resolve()

    root = tk.Tk()
    root.title(f"SOP — {md_path.stem}")
    root.geometry("980x800")

    if not md_path.exists():
        messagebox.showerror("Missing SOP", f"File not found:\n{md_path}")
        root.destroy()
        return

    md = MarkdownIt("commonmark", {"html": False, "linkify": True}).enable("table")

    md_text = read_text(md_path)
    html_body = md.render(md_text)

    html = f"<!doctype html><html><head><meta charset='utf-8'>{CSS}</head><body>{html_body}</body></html>"

    # Button frame at the top
    btn_frame = tk.Frame(root, bg="#1e1e1e", pady=8)
    btn_frame.pack(fill="x", side="top")
    
    print_btn = tk.Button(
        btn_frame,
        text="Print SOP",
        command=lambda: print_sop_pdf(md_path),
        bg="#2b2b2b",
        fg="#ffffff",
        activebackground="#3a3a3a",
        activeforeground="#ffffff",
        font=("Arial", 11),
        padx=20,
        pady=6,
        relief="raised",
        borderwidth=1,
        cursor="hand2"
    )
    print_btn.pack(side="right", padx=10)
    
    close_btn = tk.Button(
        btn_frame,
        text="Close",
        command=root.destroy,
        bg="#2b2b2b",
        fg="#ffffff",
        activebackground="#3a3a3a",
        activeforeground="#ffffff",
        font=("Arial", 11),
        padx=20,
        pady=6,
        relief="raised",
        borderwidth=1,
        cursor="hand2"
    )
    close_btn.pack(side="right", padx=5)

    frame = HtmlFrame(root, horizontal_scrollbar="auto")
    frame.pack(fill="both", expand=True)
    frame.load_html(html)

    root.mainloop()


if __name__ == "__main__":
    main()
