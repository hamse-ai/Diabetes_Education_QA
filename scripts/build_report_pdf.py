"""Render reports/report.md to a print-ready PDF using MarkdownIt and Chrome."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/report.md"
OUTPUT = ROOT / "reports/diabetes_education_qa_report.pdf"

CSS = """
@page { size: A4; margin: 19mm 18mm 20mm; }
body { font: 10pt/1.48 Georgia, 'Times New Roman', serif; color: #1d2733; }
h1 { font: bold 25pt/1.15 Arial, sans-serif; color: #123d52; margin: 0 0 18pt; }
h2 { font: bold 16pt/1.2 Arial, sans-serif; color: #155e75; margin: 22pt 0 8pt; page-break-after: avoid; }
h3 { font: bold 12pt/1.2 Arial, sans-serif; color: #155e75; margin: 15pt 0 6pt; page-break-after: avoid; }
p { margin: 0 0 8pt; }
ul, ol { margin: 4pt 0 10pt; padding-left: 22pt; }
li { margin: 0 0 3pt; }
table { border-collapse: collapse; width: 100%; margin: 9pt 0 14pt; font-size: 9pt; page-break-inside: avoid; }
th { background: #e8f2f5; text-align: left; }
th, td { border: 1px solid #b8c8cf; padding: 5pt 6pt; vertical-align: top; }
a { color: #075985; overflow-wrap: anywhere; }
strong { color: #152c39; }
hr { border: 0; border-top: 1px solid #cad5da; margin: 16pt 0; }
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    chrome = next((shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser", "chrome") if shutil.which(name)), None)
    if not chrome:
        raise SystemExit("Chrome/Chromium is required to build the report PDF.")
    markdown = args.input.read_text(encoding="utf-8")
    rendered = MarkdownIt("commonmark", {"html": False}).enable("table").render(markdown)
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Diabetes Education QA for Adults - Research Report</title><style>{CSS}</style></head>
<body>{rendered}</body></html>"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="diabetes-qa-pdf-") as temp_dir:
        temp = Path(temp_dir)
        html_path = temp / "report.html"
        html_path.write_text(html, encoding="utf-8")
        command = [
            chrome, "--headless", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
            "--no-pdf-header-footer", f"--user-data-dir={temp / 'profile'}",
            f"--print-to-pdf={args.output.resolve()}", html_path.as_uri(),
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    print(f"Wrote {args.output.resolve()} ({args.output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
