#!/usr/bin/env python3
"""
Build SOP PDFs from Markdown using Pandoc (robust list + table handling).

Input:   ./sop/**.md
Output:  ./sop/_pdf/**.pdf   (mirrors folder structure)

Requires:
  - pandoc on PATH
  - MiKTeX (or another LaTeX PDF engine)
"""

from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

def should_build(md: Path, pdf: Path, force: bool) -> bool:
    if force or not pdf.exists():
        return True
    return md.stat().st_mtime > pdf.stat().st_mtime

def build_one(md_path: Path, pdf_path: Path):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pandoc",
        str(md_path),
        "-o",
        str(pdf_path),
        "--pdf-engine=xelatex",
        "-V", "geometry:margin=0.75in",
        "-V", "fontsize=12pt",
#        "--toc",
#        "--toc-depth=3",
    ]

    subprocess.run(cmd, check=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="sop")
    p.add_argument("--output", default="sop/_pdf")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    in_root = Path(args.input)
    out_root = Path(args.output)

    built = skipped = failed = 0

    for md in in_root.rglob("*.md"):
        rel = md.relative_to(in_root)

        # prevent recursion
        if "_pdf" in rel.parts:
            continue

        pdf = out_root / rel.with_suffix(".pdf")

        if not should_build(md, pdf, args.force):
            skipped += 1
            continue

        try:
            build_one(md, pdf)
            print(f"OK   {md} -> {pdf}")
            built += 1
        except subprocess.CalledProcessError as e:
            print(f"FAIL {md}: pandoc error", file=sys.stderr)
            failed += 1

    print(f"\nDone. Built: {built}, Skipped: {skipped}, Failed: {failed}")

if __name__ == "__main__":
    main()
