"""Gera o material de repertório sociocultural; requer reportlab."""
from html import escape
from pathlib import Path
from shutil import copyfile
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'docs/repertorio-sociocultural.md'
TARGET = SOURCE.with_suffix('.pdf')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TrilhaTitle', fontName='Helvetica-Bold', fontSize=29, leading=34, textColor=colors.HexColor('#592695'), spaceAfter=20))
styles.add(ParagraphStyle(name='TrilhaSection', fontName='Helvetica-Bold', fontSize=18, leading=23, textColor=colors.HexColor('#592695'), spaceBefore=19, spaceAfter=12, keepWithNext=True))
styles.add(ParagraphStyle(name='TrilhaHeading', fontName='Helvetica-Bold', fontSize=13, leading=18, textColor=colors.HexColor('#291342'), spaceBefore=13, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle(name='TrilhaBody', fontName='Helvetica', fontSize=10, leading=16, textColor=colors.HexColor('#51445c'), spaceAfter=10, splitLongWords=True))

def page(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#e6dcef'))
    canvas.line(2*cm, 1.8*cm, 19*cm, 1.8*cm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#806b91'))
    canvas.drawString(2*cm, 1.2*cm, 'Trilha de Estudos | Repertório sociocultural')
    canvas.drawRightString(19*cm, 1.2*cm, str(doc.page))

story = []
for block in SOURCE.read_text(encoding='utf-8').split('\n\n'):
    block = block.strip()
    if not block:
        continue
    style = 'TrilhaTitle' if block.startswith('# ') else 'TrilhaSection' if block.startswith('## ') else 'TrilhaHeading' if block.startswith('### ') else 'TrilhaBody'
    text = escape(block.lstrip('# ').replace('\n', ' '))
    story.append(Paragraph(text, styles[style]))
SimpleDocTemplate(str(TARGET), pagesize=(21*cm, 29.7*cm), rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2.3*cm, title='Repertório sociocultural', author='Trilha de Estudos').build(story, onFirstPage=page, onLaterPages=page)
copyfile(TARGET, ROOT / 'assets/materials/repertorio-sociocultural.pdf')
print(TARGET)
