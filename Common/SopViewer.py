#!/usr/bin/env python3
import sys
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
  h1, h2, h3, h4 { color: #ffffff; margin-top: 1.2em; }
  h1 { font-size: 24px; border-bottom: 1px solid #444; padding-bottom: 8px; }
  h2 { font-size: 20px; border-bottom: 1px solid #333; padding-bottom: 6px; }
  h3 { font-size: 16px; }
  p { margin: 0.55em 0; }
  ul, ol { margin: 0.4em 0 0.8em 1.3em; }
  li { margin: 0.25em 0; }
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

    frame = HtmlFrame(root, horizontal_scrollbar="auto")
    frame.pack(fill="both", expand=True)
    frame.load_html(html)

    root.mainloop()


if __name__ == "__main__":
    main()
