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
import re
from pathlib import Path
import tempfile

_INCLUDE_RE = re.compile(r"\{\{\s*include\s+(.+?)\s*\}\}")

def expand_includes(md_text: str, sop_root: Path) -> str:
    sop_root = Path(sop_root).resolve()
    sop_root_name = sop_root.name.lower()  # usually "sop"

    def repl(match):
        rel_path_raw = match.group(1).strip()
        rel_path = rel_path_raw.replace("\\", "/")

        # Tolerate "sop/..." in includes even when sop_root is already ".../sop"
        lower = rel_path.lower()
        if lower.startswith(sop_root_name + "/"):
            rel_path = rel_path[len(sop_root_name) + 1 :]

        inc = (sop_root / rel_path).resolve()

        if not inc.exists():
            # Keep error safe + separated
            return f"\n\n> **ERROR:** Missing include file: `{rel_path_raw}`\n\n"

        included = inc.read_text(encoding="utf-8")

        # Normalize line endings and guarantee trailing newline
        included = included.replace("\r\n", "\n").rstrip() + "\n"

        # CRITICAL: force separation so headers/lists don't get glued together
        return "\n\n" + included + "\n"

    return _INCLUDE_RE.sub(repl, md_text)

def preprocess_markdown(md_path: Path, sop_root: Path) -> str:
    md_path = Path(md_path).resolve()
    sop_root = Path(sop_root).resolve()
    text = md_path.read_text(encoding="utf-8")
    return expand_includes(text, sop_root)

def find_includes(md_text: str) -> list[str]:
    """Return raw include paths found in markdown text."""
    return [m.group(1).strip() for m in _INCLUDE_RE.finditer(md_text)]

def resolve_include_path(raw_path: str, sop_root: Path) -> Path:
    sop_root = Path(sop_root).resolve()
    sop_root_name = sop_root.name.lower()

    rel_path = raw_path.strip().replace("\\", "/")
    lower = rel_path.lower()

    # tolerate "sop/..." even if sop_root is already ".../sop"
    if lower.startswith(sop_root_name + "/"):
        rel_path = rel_path[len(sop_root_name) + 1 :]

    return (sop_root / rel_path).resolve()

def newest_dependency_mtime(md_path: Path, sop_root: Path, seen: set[Path] | None = None) -> float:
    """
    Return the newest modification time among md_path and all files it includes (recursively).
    Prevents infinite loops via `seen`.
    """
    md_path = Path(md_path).resolve()
    sop_root = Path(sop_root).resolve()
    if seen is None:
        seen = set()

    if md_path in seen:
        return 0.0
    seen.add(md_path)

    newest = md_path.stat().st_mtime

    text = md_path.read_text(encoding="utf-8")
    for raw in find_includes(text):
        inc_path = resolve_include_path(raw, sop_root)
        if inc_path.exists():
            newest = max(newest, newest_dependency_mtime(inc_path, sop_root, seen))
        else:
            # missing include: force rebuild so the PDF shows the error message
            newest = max(newest, newest + 1)

    return newest

def should_build(md: Path, pdf: Path, force: bool, sop_root: Path) -> bool:
    if force or not pdf.exists():
        return True

    newest_src = newest_dependency_mtime(md, sop_root)
    return newest_src > pdf.stat().st_mtime

def build_one(md_path: Path, pdf_path: Path, sop_root: Path):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # 1) Expand {{ include ... }} directives
    expanded_md = preprocess_markdown(md_path, sop_root)  # <-- pass sop_root

    # 2) Write expanded markdown to a temp file for pandoc
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(expanded_md)
        tmp_md_path = Path(tmp.name)

    try:
        # 3) Run pandoc on the expanded temp file
        # On Windows, pandoc uses ';' between resource paths
        resource_path = f"{md_path.parent};{Path(sop_root)}"

        cmd = [
            "pandoc",
            str(tmp_md_path),
            "-o",
            str(pdf_path),
            "--pdf-engine=xelatex",
            "-V", "geometry:margin=0.75in",
            "-V", "fontsize=12pt",
            "--resource-path", resource_path,
        ]
        subprocess.run(cmd, check=True)

    finally:
        # 4) Cleanup temp file
        try:
            tmp_md_path.unlink()
        except Exception:
            pass

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="sop")
    p.add_argument("--output", default="sop/_pdf")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    in_root = Path(args.input).resolve()
    out_root = Path(args.output).resolve()

    built = skipped = failed = 0

    for md in in_root.rglob("*.md"):
        rel = md.relative_to(in_root)

        # prevent recursion
        if "_pdf" in rel.parts:
            continue

        pdf = out_root / rel.with_suffix(".pdf")
        if not should_build(md, pdf, args.force, in_root):
            skipped += 1
            continue

        try:
            build_one(md, pdf, in_root)  # <-- pass sop_root
            print(f"OK   {md} -> {pdf}")
            built += 1
        except subprocess.CalledProcessError:
            print(f"FAIL {md}: pandoc error", file=sys.stderr)
            failed += 1

    print(f"\nDone. Built: {built}, Skipped: {skipped}, Failed: {failed}")

if __name__ == "__main__":
    main()
