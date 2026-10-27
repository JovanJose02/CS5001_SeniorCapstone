"""Adds the running header and page numbers that wkhtmltopdf (unpatched qt) cannot."""
import io, sys
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
src, dst = sys.argv[1], sys.argv[2]
import json, os
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
pdfmetrics.registerFont(TTFont("DejaVuI", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"))
FIG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figpages.json")))
LW, LH = 792.0, 612.0  # landscape letter


def fig_page(name, caption):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(LW, LH))
    img = ImageReader(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs", name + ".png"))
    iw, ih = img.getSize()
    para = Paragraph(caption, ParagraphStyle("cap", fontName="DejaVuI", fontSize=8, leading=10))
    _, caph = para.wrap(LW - 72, 100)
    box_w, box_h = LW - 72, LH - 44 - 30 - caph - 8
    sc = min(box_w / iw, box_h / ih)
    dw, dh = iw * sc, ih * sc
    x = (LW - dw) / 2
    y = LH - 44 - dh
    c.drawImage(img, x, y, dw, dh)
    para.drawOn(c, 36, y - caph - 8)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


r = PdfReader(src)
w = PdfWriter()
pages = []
for p in r.pages:
    txt = (p.extract_text() or "").strip()
    if not txt:
        continue  # blank page left by consecutive page breaks
    for name, cap in FIG.items():
        if "FIGPAGE:" + name in txt:
            p = fig_page(name, cap)
    pages.append(p)
n = len(pages)
for i, p in enumerate(pages, 1):
    pw, ph = float(p.mediabox.width), float(p.mediabox.height)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(pw, ph))
    c.setFont("DejaVu", 7)
    c.setFillGray(0.35)
    c.drawString(37, ph - 26, f"D2_Detailed_Design | Verified Student Sublease Marketplace | page {i} of {n}")
    c.drawRightString(pw - 37, ph - 26, "CS5001 Assignment 7 | Vanganuri, Asker Fredy, Aidja")
    c.save()
    buf.seek(0)
    p.merge_page(PdfReader(buf).pages[0])
    w.add_page(p)
w.add_metadata({"/Title": "D2 Detailed Design: Verified Student Sublease Marketplace",
                "/Author": "Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja"})
with open(dst, "wb") as f:
    w.write(f)
print("pages", n)
