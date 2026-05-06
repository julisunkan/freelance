import io
import re
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


def _strip_html(html):
    if not html:
        return ''
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</p>', '\n', html)
    html = re.sub(r'</h[1-6]>', '\n', html)
    html = re.sub(r'</li>', '\n', html)
    html = re.sub(r'<li[^>]*>', '• ', html)
    html = re.sub(r'<strong>(.*?)</strong>', r'\1', html)
    html = re.sub(r'<em>(.*?)</em>', r'\1', html)
    html = re.sub(r'<[^>]+>', '', html)
    for ent, rep in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' '), ('&quot;', '"')]:
        html = html.replace(ent, rep)
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()


def _parse_html_sections(html):
    sections = []
    parts = re.split(r'(<h[1-6][^>]*>.*?</h[1-6]>)', html, flags=re.IGNORECASE | re.DOTALL)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r'<h([1-6])[^>]*>(.*?)</h[1-6]>', part, re.IGNORECASE | re.DOTALL)
        if m:
            level = int(m.group(1))
            text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            sections.append(('h', level, text))
        else:
            text = _strip_html(part)
            if text:
                sections.append(('p', 0, text))
    return sections


def generate_nda_pdf(nda):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=1*inch, rightMargin=1*inch,
                            topMargin=1*inch, bottomMargin=1*inch)

    brand = colors.HexColor('#4f46e5')
    dark = colors.HexColor('#1e1b4b')
    muted = colors.HexColor('#6b7280')
    body_color = colors.HexColor('#374151')

    styles = getSampleStyleSheet()
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=22, textColor=dark,
                             fontName='Helvetica-Bold', spaceAfter=6)
    sub_s = ParagraphStyle('S', parent=styles['Normal'], fontSize=10, textColor=muted,
                           spaceAfter=14, italic=True)
    h1_s = ParagraphStyle('H1', parent=styles['Normal'], fontSize=13, textColor=brand,
                           fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=4)
    h2_s = ParagraphStyle('H2', parent=styles['Normal'], fontSize=11, textColor=dark,
                           fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
    body_s = ParagraphStyle('B', parent=styles['Normal'], fontSize=9.5, textColor=body_color,
                            spaceAfter=5, leading=14)
    label_s = ParagraphStyle('L', parent=styles['Normal'], fontSize=8, textColor=muted, spaceAfter=2)

    story = []
    story.append(Paragraph('NON-DISCLOSURE AGREEMENT', title_s))
    story.append(Paragraph(f"Between <b>{nda['party_a']}</b> and <b>{nda['party_b']}</b>", sub_s))
    story.append(HRFlowable(width='100%', thickness=2, color=brand, spaceAfter=12))

    meta = [
        ['Status', nda.get('status', 'draft').title()],
        ['Purpose', (nda.get('purpose') or '')[:80]],
        ['Jurisdiction', nda.get('jurisdiction', '')],
        ['Created', (nda.get('created_at') or '')[:10]],
    ]
    t = Table(meta, colWidths=[1.3*inch, 5.2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), brand),
        ('TEXTCOLOR', (1, 0), (1, -1), body_color),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f5f3ff'), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.15*inch))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=12))

    nda_html = nda.get('nda_html') or ''
    sections = _parse_html_sections(nda_html)
    for kind, level, text in sections:
        if kind == 'h':
            s = h1_s if level <= 2 else h2_s
            story.append(Paragraph(text, s))
        else:
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 0.04*inch))
                    continue
                story.append(Paragraph(line, body_s))

    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=12))
    story.append(Paragraph('SIGNATURES', h1_s))

    def _sig_block(party_label, sig_b64, ip, signed_at):
        story.append(Paragraph(f'<b>{party_label}</b>', h2_s))
        if sig_b64 and sig_b64.startswith('data:image'):
            try:
                header, data = sig_b64.split(',', 1)
                img_bytes = base64.b64decode(data)
                img_buf = io.BytesIO(img_bytes)
                img = Image(img_buf, width=2.5*inch, height=0.9*inch)
                story.append(img)
            except Exception:
                story.append(Paragraph('[Signature on file]', body_s))
        else:
            story.append(Paragraph('[Not yet signed]', body_s))
        if ip:
            story.append(Paragraph(f'IP: {ip}  |  Signed: {(signed_at or "")[:19]} UTC', label_s))
        story.append(Spacer(1, 0.15*inch))

    _sig_block(nda['party_a'], nda.get('signature_a'), nda.get('ip_a'), nda.get('signed_at_a'))
    _sig_block(nda['party_b'], nda.get('signature_b'), nda.get('ip_b'), nda.get('signed_at_b'))

    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=6))
    story.append(Paragraph(f'Generated by NDA Generator AI  |  Document ID: {nda["public_id"]}', label_s))

    doc.build(story)
    buf.seek(0)
    return buf
