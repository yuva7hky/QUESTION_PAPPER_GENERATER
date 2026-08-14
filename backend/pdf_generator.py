"""
pdf_generator.py — Generate professional CIE-I / Model Question Paper PDF.

Uses reportlab to create a document that matches the official
JIT examination paper format:
  - Register number boxes
  - College header & Exam title
  - Metadata grid
  - Course outcomes
  - Borderless question layout (matching official printed paper)
  - EXAMCELL footer & K-level legend
"""

import os
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

from html import escape as html_escape

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_local_path(img_url, base_dir=BASE_DIR):
    """Convert relative URL /api/images/<file_id>/<filename> to local disk path."""
    if not img_url:
        return None
    if img_url.startswith('/api/images/'):
        rel_path = img_url.replace('/api/images/', '').lstrip('/')
        return os.path.join(base_dir, 'uploads', 'images', rel_path)
    return img_url


def _resolve_equation_path(eq_url, base_dir=BASE_DIR):
    """Convert relative URL /api/equations/<file_id>/<filename> to local disk path."""
    if not eq_url:
        return None
    if eq_url.startswith('/api/equations/'):
        rel_path = eq_url.replace('/api/equations/', '').lstrip('/')
        return os.path.join(base_dir, 'uploads', 'equations', rel_path)
    return eq_url


def _build_pdf_markup(q_or_text, prefix=""):
    """Build ReportLab paragraph markup with inline equation images."""
    if isinstance(q_or_text, dict):
        content = q_or_text.get('content')
        if content:
            parts = [prefix]
            for item in content:
                if item['type'] == 'text':
                    parts.append(html_escape(item['value']))
                elif item['type'] == 'equation':
                    local_path = item.get('local_path') or _resolve_equation_path(item.get('url'))
                    if local_path and os.path.exists(local_path):
                        ar = item.get('aspect_ratio', 1.0)
                        h_pt = 12.0
                        w_pt = h_pt * ar
                        parts.append(f" <img src='{local_path}' width='{w_pt:.1f}' height='{h_pt:.1f}' valign='middle'/> ")
                    else:
                        parts.append(f" ${html_escape(item.get('latex', ''))}$ ")
            return "".join(parts)
        else:
            return prefix + html_escape(q_or_text.get('text', ''))
    else:
        return prefix + str(q_or_text)


def _make_question_cell(text_markup, images, styles, base_dir=BASE_DIR, max_w=310, max_h=220):
    """Create cell content containing question text and any associated diagram flowables."""
    flowables = [Paragraph(text_markup, styles['CellText'])]
    if images:
        for img_url in images:
            local_path = _resolve_local_path(img_url, base_dir)
            if local_path and os.path.exists(local_path):
                try:
                    with PILImage.open(local_path) as pil_img:
                        w, h = pil_img.size
                    if w > 0 and h > 0:
                        scale = min(float(max_w) / float(w), float(max_h) / float(h), 1.0)
                        scaled_w = max(100.0, w * scale)
                        scaled_h = max(40.0, h * scale)
                        img_flowable = RLImage(local_path, width=scaled_w, height=scaled_h)
                        img_flowable.hAlign = 'CENTER'
                        flowables.append(Spacer(1, 3))
                        flowables.append(img_flowable)
                        flowables.append(Spacer(1, 3))
                except Exception as e:
                    print(f"Warning: Could not embed image {local_path} in PDF: {e}")
    if len(flowables) == 1:
        return flowables[0]
    return flowables


def generate_pdf(paper_data, output_path=None):
    """
    Generate a PDF question paper matching the printed JIT exam paper style.
    
    Args:
        paper_data: Paper dictionary from generator.generate_paper()
        output_path: Path to save the generated PDF file. If None, auto-generates in 'generated/'.
        
    Returns:
        Path to generated PDF file.
    """
    metadata = paper_data.get('metadata', {})
    course_outcomes = paper_data.get('course_outcomes', [])
    part_a = paper_data.get('part_a')
    part_b = paper_data.get('part_b')
    part_c = paper_data.get('part_c')

    exam_type = metadata.get('exam_type', 'CIE I')
    month_year = metadata.get('month_year', 'JULY 2026')
    paper_id = paper_data.get('paper_id', str(uuid.uuid4())[:8])

    if not output_path:
        out_dir = os.path.join(BASE_DIR, 'generated')
        os.makedirs(out_dir, exist_ok=True)
        filename = f"Question_Paper_{paper_id}.pdf"
        output_path = os.path.join(out_dir, filename)

    # ── Canvas / Page Setup ──
    # Margins: Left=0.6 in, Right=0.6 in, Top=0.6 in, Bottom=0.6 in
    margin = 0.6 * inch
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    styles = _create_styles()
    elements = []

    # ── Top Section: Reg No (top right) ───────────────────
    reg_data = [['Reg No'] + [''] * 12]
    reg_table = Table(reg_data, colWidths=[45] + [16] * 12)
    reg_table.setStyle(TableStyle([
        ('BOX', (1, 0), (-1, 0), 1, colors.black),
        ('INNERGRID', (1, 0), (-1, 0), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    # Outer wrapper to right-align reg_table
    wrap_table = Table([[Paragraph('', styles['MetaText']), reg_table]], colWidths=[doc.width - 237, 237])
    wrap_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(wrap_table)
    elements.append(Spacer(1, 4))

    # ── College Header ────────────────────────────────────
    elements.append(Paragraph("JEPPIAAR INSTITUTE OF TECHNOLOGY", styles['CollegeTitle']))
    elements.append(Paragraph("(An Autonomous Institution)", styles['CenterSmall']))
    elements.append(Paragraph('"Self-Belief | Self-Discipline | Self-Respect"', styles['CenterSmallItalic']))
    elements.append(Paragraph("Kunnam, Sunguvarchatram, Sriperumbudur – 631 604.", styles['CenterSmall']))
    elements.append(Spacer(1, 6))

    # ── Exam Title ────────────────────────────────────────
    exam_type = metadata.get('exam_type', 'CIE I').upper()
    month_year = metadata.get('month_year', '').upper()
    elements.append(Paragraph(
        f"<b>{exam_type} – {month_year}</b>",
        styles['ExamTitle']
    ))
    elements.append(Spacer(1, 6))

    # ── Metadata Grid ─────────────────────────────────────
    subject_code = metadata.get('su00') if metadata.get('su00') and metadata.get('su00') != '-' else metadata.get('subject_code', '-')
    subject_name = metadata.get('su01') if metadata.get('su01') and metadata.get('su01') != '-' else metadata.get('subject_name', '-')
    branch_info = metadata.get('branch_info') if metadata.get('branch_info') and metadata.get('branch_info') != '-' else '-'
    duration = metadata.get('duration', '1 ½ hours')
    date = metadata.get('date', '___________')
    max_marks = metadata.get('max_marks_display', metadata.get('max_marks', '-'))

    meta_data = [
        [
            Paragraph(f"<b>SUB CODE:</b> {subject_code}", styles['MetaText']),
            Paragraph(f"<b>SUBJECT:</b> {subject_name}", styles['MetaTextRight']),
        ],
        [
            Paragraph(f"<b>Duration:</b> {duration}", styles['MetaText']),
            Paragraph(f"<b>Branch / Year / Sem:</b> {branch_info}", styles['MetaTextRight']),
        ],
        [
            Paragraph(f"<b>Date:</b> {date}", styles['MetaText']),
            Paragraph(f"<b>Maximum:</b> {max_marks}", styles['MetaTextRight']),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[doc.width * 0.45, doc.width * 0.55])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 6))

    # ── Course Outcomes ───────────────────────────────────
    if course_outcomes:
        elements.append(Paragraph(
            "<b>Course Outcome: – After Successful Completion of the Course, the Students should be able to</b>",
            styles['COHeader']
        ))
        elements.append(Spacer(1, 2))
        for co in course_outcomes:
            co_table = Table(
                [[Paragraph(f"<b>{co['id']}</b>", styles['COId']), Paragraph(co['text'], styles['COText'])]],
                colWidths=[55, doc.width - 55]
            )
            co_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            elements.append(co_table)
        elements.append(Spacer(1, 6))

    # ── Instructions ──────────────────────────────────────
    elements.append(Paragraph("Answer all questions.", styles['CenterSmallBold']))
    elements.append(Spacer(1, 4))

    # Column widths for question sections: Q.NO(30), QUESTIONS(flex), CO NO(45), MARKS(45), K LEVEL(50)
    col_widths = [30, doc.width - 30 - 45 - 45 - 50, 45, 45, 50]

    # ═══════════ PART A ═══════════════════════════════════
    if part_a and part_a.get('questions'):
        config = part_a.get('config', '')
        elements.append(Paragraph(f"<b>PART – A ({config})</b>", styles['CenterSmallBold']))
        elements.append(Spacer(1, 4))

        a_data = [[
            Paragraph('<b>Q.NO</b>', styles['HeaderColCenter']),
            Paragraph('<b>QUESTIONS</b>', styles['HeaderColCenter']),
            Paragraph('<b>CO NO.</b>', styles['HeaderColCenter']),
            Paragraph('<b>MARKS</b>', styles['HeaderColCenter']),
            Paragraph('<b>K LEVEL</b>', styles['HeaderColCenter']),
        ]]

        for q in part_a['questions']:
            a_data.append([
                Paragraph(str(q['q_no']), styles['CellCenter']),
                _make_question_cell(_build_pdf_markup(q), q.get('images', []), styles),
                Paragraph(str(q['co']), styles['CellCenter']),
                Paragraph(str(q['marks']), styles['CellCenter']),
                Paragraph(str(q['k_level']), styles['CellCenter']),
            ])

        a_table = Table(a_data, colWidths=col_widths)
        a_table.setStyle(_get_clean_table_style())
        elements.append(a_table)
        elements.append(Spacer(1, 8))

    # ═══════════ PART B ═══════════════════════════════════
    if part_b and part_b.get('questions'):
        config = part_b.get('config', '')
        elements.append(Paragraph(f"<b>PART – B ({config})</b>", styles['CenterSmallBold']))
        elements.append(Spacer(1, 4))

        b_data = [[
            Paragraph('<b>Q.NO</b>', styles['HeaderColCenter']),
            Paragraph('<b>QUESTIONS</b>', styles['HeaderColCenter']),
            Paragraph('<b>CO NO.</b>', styles['HeaderColCenter']),
            Paragraph('<b>MARKS</b>', styles['HeaderColCenter']),
            Paragraph('<b>K LEVEL</b>', styles['HeaderColCenter']),
        ]]

        for group in part_b['questions']:
            q_no = group['q_no']
            a_q = group['a']
            b_q = group['b']

            b_data.append([
                Paragraph(f"{q_no}.", styles['CellCenter']),
                _make_question_cell(_build_pdf_markup(a_q, prefix="<b>a)</b> "), a_q.get('images', []), styles),
                Paragraph(str(a_q['co']), styles['CellCenter']),
                Paragraph(str(a_q['marks']), styles['CellCenter']),
                Paragraph(str(a_q['k_level']), styles['CellCenter']),
            ])
            b_data.append([
                '',
                Paragraph('<b>(OR)</b>', styles['CellCenterBold']),
                '', '', '',
            ])
            b_data.append([
                '',
                _make_question_cell(_build_pdf_markup(b_q, prefix="<b>b)</b> "), b_q.get('images', []), styles),
                Paragraph(str(b_q['co']), styles['CellCenter']),
                Paragraph(str(b_q['marks']), styles['CellCenter']),
                Paragraph(str(b_q['k_level']), styles['CellCenter']),
            ])

        b_table = Table(b_data, colWidths=col_widths)
        b_table.setStyle(_get_clean_table_style())
        elements.append(b_table)
        elements.append(Spacer(1, 8))

    # ═══════════ PART C ═══════════════════════════════════
    if part_c and part_c.get('questions'):
        config = part_c.get('config', '')
        elements.append(Paragraph(f"<b>PART – C ({config})</b>", styles['CenterSmallBold']))
        elements.append(Spacer(1, 4))

        c_data = [[
            Paragraph('<b>Q.NO</b>', styles['HeaderColCenter']),
            Paragraph('<b>QUESTIONS</b>', styles['HeaderColCenter']),
            Paragraph('<b>CO NO.</b>', styles['HeaderColCenter']),
            Paragraph('<b>MARKS</b>', styles['HeaderColCenter']),
            Paragraph('<b>K LEVEL</b>', styles['HeaderColCenter']),
        ]]

        for group in part_c['questions']:
            q_no = group['q_no']
            a_q = group['a']
            b_q = group['b']

            c_data.append([
                Paragraph(f"{q_no}.", styles['CellCenter']),
                _make_question_cell(_build_pdf_markup(a_q, prefix="<b>a)</b> "), a_q.get('images', []), styles),
                Paragraph(str(a_q['co']), styles['CellCenter']),
                Paragraph(str(a_q['marks']), styles['CellCenter']),
                Paragraph(str(a_q['k_level']), styles['CellCenter']),
            ])
            c_data.append([
                '',
                Paragraph('<b>(OR)</b>', styles['CellCenterBold']),
                '', '', '',
            ])
            c_data.append([
                '',
                _make_question_cell(_build_pdf_markup(b_q, prefix="<b>b)</b> "), b_q.get('images', []), styles),
                Paragraph(str(b_q['co']), styles['CellCenter']),
                Paragraph(str(b_q['marks']), styles['CellCenter']),
                Paragraph(str(b_q['k_level']), styles['CellCenter']),
            ])

        c_table = Table(c_data, colWidths=col_widths)
        c_table.setStyle(_get_clean_table_style())
        elements.append(c_table)
        elements.append(Spacer(1, 10))

    # ── EXAMCELL Footer Block ─────────────────────────────
    elements.append(Paragraph("<b>EXAMCELL</b>", styles['CenterBold']))
    elements.append(Paragraph("<b>Jeppiaar Institute of Technology (Autonomous)</b>", styles['CenterSmallBold']))
    elements.append(Paragraph("Kunnam, Sunguvarchatram, Sriperumbudur – 631 604.", styles['CenterSmall']))
    elements.append(Spacer(1, 8))

    # ── K-Level Legend ────────────────────────────────────
    elements.append(Paragraph(
        "K1-Remembering, K2-Understanding, K3-Applying, K4-Analysing, K5-Evaluating, K6-Creating",
        styles['Legend']
    ))

    # Build PDF
    doc.build(elements)
    return output_path


def _create_styles():
    """Create custom paragraph styles matching Times New Roman exam format."""
    base = getSampleStyleSheet()

    return {
        'CollegeTitle': ParagraphStyle(
            'CollegeTitle', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=12, fontName='Times-Bold',
            spaceAfter=1, leading=14,
        ),
        'ExamTitle': ParagraphStyle(
            'ExamTitle', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=11, fontName='Times-Bold',
            spaceAfter=2, leading=13,
        ),
        'CenterBold': ParagraphStyle(
            'CenterBold', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=10, fontName='Times-Bold',
            spaceAfter=1, leading=12,
        ),
        'CenterSmall': ParagraphStyle(
            'CenterSmall', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=8.5, fontName='Times-Roman', leading=10,
        ),
        'CenterSmallItalic': ParagraphStyle(
            'CenterSmallItalic', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=8, fontName='Times-Italic', leading=10,
        ),
        'CenterSmallBold': ParagraphStyle(
            'CenterSmallBold', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=11, fontName='Times-Bold', leading=13,
        ),
        'MetaText': ParagraphStyle(
            'MetaText', parent=base['Normal'],
            fontSize=8.5, fontName='Times-Roman', leading=11,
        ),
        'MetaTextRight': ParagraphStyle(
            'MetaTextRight', parent=base['Normal'],
            fontSize=8.5, fontName='Times-Roman', leading=11, alignment=TA_RIGHT,
        ),
        'COHeader': ParagraphStyle(
            'COHeader', parent=base['Normal'],
            fontSize=8.5, fontName='Times-Roman', leading=11,
        ),
        'COId': ParagraphStyle(
            'COId', parent=base['Normal'],
            fontSize=8.5, fontName='Times-Bold', leading=11,
        ),
        'COText': ParagraphStyle(
            'COText', parent=base['Normal'],
            fontSize=8.5, fontName='Times-Roman', leading=11,
        ),
        'HeaderColCenter': ParagraphStyle(
            'HeaderColCenter', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=8.5, fontName='Times-Bold', leading=11,
        ),
        'CellText': ParagraphStyle(
            'CellText', parent=base['Normal'],
            fontSize=8.5, fontName='Times-Roman', leading=11,
        ),
        'CellCenter': ParagraphStyle(
            'CellCenter', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=8.5, fontName='Times-Roman', leading=11,
        ),
        'CellCenterBold': ParagraphStyle(
            'CellCenterBold', parent=base['Normal'],
            alignment=TA_CENTER, fontSize=8.5, fontName='Times-Bold', leading=11,
        ),
        'Legend': ParagraphStyle(
            'Legend', parent=base['Normal'],
            fontSize=7.5, fontName='Times-Roman', alignment=TA_CENTER, textColor=colors.black,
        ),
    }


def _get_clean_table_style():
    """Clean borderless style (no vertical table grid lines)."""
    return TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ])
