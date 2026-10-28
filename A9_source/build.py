"""Builds Requirements_Document.pdf and Technical_Specification.pdf from the .md sources in the repo root.

Needs the `markdown` package (pip install markdown) and Google Chrome. Run: python3 A9_source/build.py
"""
import os, re, subprocess, markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DOCS = ["Requirements_Document", "Technical_Specification"]

CSS = """
@page { size: Letter; margin: 15mm 12mm 14mm 12mm;
  @top-left { content: "%(title)s | Verified Student Sublease Marketplace"; font: 7pt 'Helvetica Neue', Arial, sans-serif; color: #555; }
  @bottom-right { content: "page " counter(page) " of " counter(pages); font: 7pt 'Helvetica Neue', Arial, sans-serif; color: #555; } }
body { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 9.2pt; line-height: 1.36; color: #111; }
h1 { font-size: 19pt; margin: 0 0 6px 0; }
h2 { font-size: 13pt; margin: 16px 0 5px 0; border-bottom: 1px solid #bbb; padding-bottom: 2px; break-after: avoid; }
h3 { font-size: 10.6pt; margin: 11px 0 4px 0; break-after: avoid; }
p { margin: 3px 0 6px 0; }
hr { border: 0; border-top: 1px solid #ccc; margin: 8px 0; }
table { border-collapse: collapse; width: 100%%; margin: 5px 0 9px 0; font-size: 7.7pt; line-height: 1.28; }
th { background: #E9EEF5; text-align: left; }
th, td { border: 1px solid #9aa; padding: 2px 4px; vertical-align: top; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
code { font-family: Menlo, monospace; font-size: 0.86em; background: #F1F1F1; padding: 0 2px; }
pre { background: #F6F6F6; border: 1px solid #ddd; padding: 5px; font-size: 7.2pt; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; }
ul { margin: 3px 0 6px 18px; padding: 0; }
a { color: #1a4f9c; text-decoration: none; }
"""

for name in DOCS:
    with open(os.path.join(ROOT, name + ".md")) as f:
        body = markdown.markdown(f.read(), extensions=["tables", "fenced_code", "sane_lists"])
    body = re.sub(r"<td>(Must|Should|Could)</td>", r"<td><b>\1</b></td>", body)
    title = name.replace("_", " ")
    html = (f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>"
            f"<style>{CSS % {'title': title}}</style></head><body>{body}</body></html>")
    html_path = os.path.join(ROOT, "A9_source", name + ".html")
    with open(html_path, "w") as f:
        f.write(html)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.join(ROOT, name + '.pdf')}", "file://" + html_path],
                   check=True, capture_output=True)
    print("built", name + ".pdf")
