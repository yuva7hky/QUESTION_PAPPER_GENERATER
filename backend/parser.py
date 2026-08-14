"""
parser.py — DOCX Question Bank Parser.

Reads a .docx file containing a single-table Question Bank and extracts:
  - Metadata (SU00, SU01, BR00, YR00, SE00)
  - Course Outcomes (CO1–CO6)
  - Part A questions grouped by question number
  - Part B questions grouped by question number and sub-part (a/b)
  - Part C questions (same structure as Part B)
  - Marks distribution from section headers
"""

import os
import re
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from docx import Document


# Mappings for Branch names to Short Branch Code
BRANCH_MAP = {
    'ARTIFICIAL INTELLIGENCE AND DATA SCIENCE': 'ADS',
    'AI & DS': 'ADS',
    'AI AND DS': 'ADS',
    'ADS': 'ADS',
    'COMPUTER SCIENCE AND ENGINEERING': 'CSE',
    'CSE': 'CSE',
    'INFORMATION TECHNOLOGY': 'IT',
    'IT': 'IT',
    'COMPUTER SCIENCE AND BUSINESS SYSTEMS': 'CSBS',
    'CSBS': 'CSBS',
    'ELECTRONICS AND COMMUNICATION ENGINEERING': 'ECE',
    'ECE': 'ECE',
    'ELECTRICAL AND ELECTRONICS ENGINEERING': 'EEE',
    'EEE': 'EEE',
    'MECHANICAL ENGINEERING': 'MECH',
    'MECH': 'MECH',
    'CIVIL ENGINEERING': 'CIVIL',
    'CIVIL': 'CIVIL',
}

# Semester to Roman Numeral & Year calculation
SEM_MAP = {
    '1': ('I', 'I'),
    '1ST': ('I', 'I'),
    'FIRST': ('I', 'I'),
    'I': ('I', 'I'),
    '2': ('II', 'I'),
    '2ND': ('II', 'I'),
    'SECOND': ('II', 'I'),
    'II': ('II', 'I'),
    '3': ('III', 'II'),
    '3RD': ('III', 'II'),
    'THIRD': ('III', 'II'),
    'III': ('III', 'II'),
    '4': ('IV', 'II'),
    '4TH': ('IV', 'II'),
    'FOURTH': ('IV', 'II'),
    'IV': ('IV', 'II'),
    '5': ('V', 'III'),
    '5TH': ('V', 'III'),
    'FIFTH': ('V', 'III'),
    'V': ('V', 'III'),
    '6': ('VI', 'III'),
    '6TH': ('VI', 'III'),
    'SIXTH': ('VI', 'III'),
    'VI': ('VI', 'III'),
    '7': ('VII', 'IV'),
    '7TH': ('VII', 'IV'),
    'SEVENTH': ('VII', 'IV'),
    'VII': ('VII', 'IV'),
    '8': ('VIII', 'IV'),
    '8TH': ('VIII', 'IV'),
    'EIGHTH': ('VIII', 'IV'),
    'VIII': ('VIII', 'IV'),
}


def parse_question_bank(filepath, file_id=None):
    """
    Parse a Question Bank .docx file.
    
    Args:
        filepath: Path to the .docx file.
        file_id: Optional unique identifier for storing extracted images.
    
    Returns:
        dict with metadata, course outcomes, and question sections with associated images.
    """
    if not file_id:
        file_id = os.path.splitext(os.path.basename(filepath))[0]

    doc = Document(filepath)

    if not doc.tables:
        raise ValueError("No tables found in the document. Expected a table-based Question Bank.")

    # Image and equation storage directories for this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, 'uploads', 'images', file_id)
    eq_dir = os.path.join(base_dir, 'uploads', 'equations', file_id)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(eq_dir, exist_ok=True)

    table = doc.tables[0]
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(cells)

    # ── Extract Metadata ──────────────────────────────────
    metadata = _extract_metadata(rows)

    # ── Extract Course Outcomes ───────────────────────────
    course_outcomes = _extract_course_outcomes(rows)

    # ── Find section boundaries ───────────────────────────
    part_a_start, part_a_config = None, ''
    part_b_start, part_b_config = None, ''
    part_c_start, part_c_config = None, ''

    for i, row in enumerate(rows):
        text = row[2].lower() if len(row) > 2 else ''
        if not text:
            text = ' '.join(c for c in row if c).lower()

        if re.search(r'part[\s\-\u2013\u2014\ufffd–—]*a\b', text):
            part_a_start = i
            part_a_config = _extract_marks_config(text)
        elif re.search(r'part[\s\-\u2013\u2014\ufffd–—]*b\b', text):
            part_b_start = i
            part_b_config = _extract_marks_config(text)
        elif re.search(r'part[\s\-\u2013\u2014\ufffd–—]*c\b', text):
            part_c_start = i
            part_c_config = _extract_marks_config(text)

    # ── Parse Part A ──────────────────────────────────────
    part_a_end = part_b_start if part_b_start else len(rows)
    part_a_questions = _parse_part_a(table, part_a_start, part_a_end, doc, file_id, img_dir, eq_dir)

    # ── Parse Part B ──────────────────────────────────────
    part_b_end = part_c_start if part_c_start else len(rows)
    part_b_questions = _parse_part_bc(table, part_b_start, part_b_end, doc, file_id, img_dir, eq_dir)

    # ── Parse Part C ──────────────────────────────────────
    part_c_questions = _parse_part_bc(table, part_c_start, len(rows), doc, file_id, img_dir, eq_dir)

    # ── Determine marks per question ──────────────────────
    part_a_marks = _extract_marks_per_question(part_a_config)
    part_b_marks = _extract_marks_per_question(part_b_config)
    part_c_marks = _extract_marks_per_question(part_c_config)

    return {
        'metadata': metadata,
        'course_outcomes': course_outcomes,
        'part_a': {
            'config': part_a_config,
            'marks_per_question': part_a_marks,
            'questions': part_a_questions,
        },
        'part_b': {
            'config': part_b_config,
            'marks_per_question': part_b_marks,
            'questions': part_b_questions,
        },
        'part_c': {
            'config': part_c_config,
            'marks_per_question': part_c_marks,
            'questions': part_c_questions,
        },
    }


def _extract_row_images(row, r_idx, doc, file_id, img_dir):
    """Extract embedded images from a table row XML and save to disk."""
    xml_str = row._element.xml
    rids = re.findall(r'(?:r:embed|r:id|r:link)="([^"]+)"', xml_str)
    extracted_urls = []
    for rid in rids:
        if rid in doc.part.rels and 'image' in doc.part.rels[rid].target_ref.lower():
            part = doc.part.rels[rid].target_part
            ext = os.path.splitext(part.filename)[1] or '.png'
            filename = f"img_{r_idx}_{rid}{ext}"
            disk_path = os.path.join(img_dir, filename)
            if not os.path.exists(disk_path):
                with open(disk_path, 'wb') as f:
                    f.write(part.blob)
            url = f"/api/images/{file_id}/{filename}"
            if url not in extracted_urls:
                extracted_urls.append(url)
    return extracted_urls


def _extract_metadata(rows):
    """
    Extract metadata fields from QB:
      SU00 = Subject Code (e.g. AIT519)
      SU01 = Subject Name (e.g. Artificial Intelligence)
      BR00 = Short Branch Code (CSE / IT / ADS / CSBS)
      YR00 = Year (I / II / III / IV)
      SE00 = Semester (I / II / III / IV / V / VI / VII / VIII)
    """
    metadata = {
        'su00': '-',
        'su01': '-',
        'br00': '-',
        'yr00': '-',
        'se00': '-',
        'subject_code': '-',
        'subject_name': '-',
        'branch': '-',
        'semester': '-',
        'branch_info': '-',
    }

    raw_br_list = []
    raw_se = '-'
    raw_yr = '-'

    for row in rows[:15]:
        col0 = row[0].strip().upper() if row[0] else ''
        col2 = row[2].strip() if len(row) > 2 else ''

        if not col2:
            continue

        if col0 == 'SE00' or col0.startswith('SE'):
            raw_se = col2

        elif col0.startswith('BR'):
            if col2 not in raw_br_list:
                raw_br_list.append(col2)

        elif col0 == 'YR00' or col0.startswith('YR'):
            raw_yr = col2

        elif col0 == 'SU00' or col0.startswith('SU00'):
            match = re.match(r'([A-Z0-9]+)\s*[–\-]\s*(.*)', col2)
            if match:
                metadata['su00'] = match.group(1).strip()
                if metadata['su01'] == '-':
                    metadata['su01'] = match.group(2).strip()
            else:
                metadata['su00'] = col2

        elif col0 == 'SU01' or col0.startswith('SU01'):
            metadata['su01'] = col2

    # ── Process BR00 (Complete Branch Information) ─────────
    if raw_br_list:
        full_br = ", ".join(raw_br_list)
        metadata['br00'] = full_br
        metadata['branch'] = full_br

    # ── Process SE00 (Semester) & YR00 (Year) ────────────
    if raw_se != '-':
        match_sem = re.search(r'\b(1ST|2ND|3RD|4TH|5TH|6TH|7TH|8TH|1|2|3|4|5|6|7|8|VIII|VII|VI|V|IV|III|II|I)\b', raw_se.upper())
        if match_sem:
            sem_key = match_sem.group(1)
            sem_roman, calc_yr = SEM_MAP.get(sem_key, (sem_key, '-'))
            metadata['se00'] = sem_roman
            metadata['semester'] = sem_roman
            if raw_yr == '-':
                raw_yr = calc_yr

    # ── Process YR00 (Year) ───────────────────────────────
    if raw_yr != '-':
        cleaned_yr = raw_yr.upper()
        match_yr = re.search(r'\b(1ST|2ND|3RD|4TH|1|2|3|4|IV|III|II|I)\b', cleaned_yr)
        if match_yr:
            yr_key = match_yr.group(1)
            yr_roman, _ = SEM_MAP.get(yr_key, (yr_key, '-'))
            metadata['yr00'] = yr_roman
        else:
            metadata['yr00'] = raw_yr

    # Fallbacks for subject code / subject name
    if metadata['su00'] != '-':
        metadata['subject_code'] = metadata['su00']
    if metadata['su01'] != '-':
        metadata['subject_name'] = metadata['su01']

    # Dynamically build Branch / Year / Sem: BR00 / YR00 / SE00
    metadata['branch_info'] = f"{metadata['br00']} / {metadata['yr00']} / {metadata['se00']}"

    return metadata


def _extract_course_outcomes(rows):
    """Extract course outcomes (CO1–CO6) from the metadata section."""
    outcomes = []
    for row in rows[:15]:
        col0 = row[0].strip().upper() if row[0] else ''
        col2 = row[2].strip() if len(row) > 2 else ''

        match = re.match(r'(CO\d+)#?', col0)
        if match and col2:
            outcomes.append({
                'id': match.group(1),
                'text': col2,
            })

    return outcomes


def _extract_marks_config(text):
    """Extract string like '5 x 2 = 10 Marks' from section header text."""
    match = re.search(r'\(\s*\d+\s*[xX*]\s*\d+[^)]*\)', text)
    if match:
        return match.group(0).strip('()').strip()
    return ''


def _extract_marks_per_question(config):
    """Parse mark per question from config string like '5 x 2 = 10 Marks'."""
    match = re.search(r'\d+\s*[xX*]\s*(\d+)', config)
    if match:
        return int(match.group(1))
    return 0


def omml_to_latex(elem):
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    
    if tag in ('oMath', 'oMathPara', 'e', 'num', 'den', 'sub', 'sup', 'fName', 'lim'):
        return ''.join(omml_to_latex(child) for child in elem)
    
    elif tag == 'r':
        text = ''
        for child in elem:
            ctag = child.tag.split('}')[-1]
            if ctag == 't':
                text += child.text or ''
        replacements = {
            '…': r'\dots',
            '∞': r'\infty',
            '∑': r'\sum ',
            'π': r'\pi ',
            'α': r'\alpha ', 'β': r'\beta ', 'θ': r'\theta ', 'λ': r'\lambda ',
            '≤': r'\le ', '≥': r'\ge ', '≠': r'\ne ', '×': r'\times ', '÷': r'\div ', '±': r'\pm '
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    elif tag == 'f':
        num_elem = elem.find('.//{*}num')
        den_elem = elem.find('.//{*}den')
        num = omml_to_latex(num_elem) if num_elem is not None else ''
        den = omml_to_latex(den_elem) if den_elem is not None else ''
        return f'\\frac{{{num}}}{{{den}}}'

    elif tag == 'sSup':
        e_elem = elem.find('.//{*}e')
        sup_elem = elem.find('.//{*}sup')
        e_str = omml_to_latex(e_elem) if e_elem is not None else ''
        sup_str = omml_to_latex(sup_elem) if sup_elem is not None else ''
        return f'{{{e_str}}}^{{{sup_str}}}'

    elif tag == 'sSub':
        e_elem = elem.find('.//{*}e')
        sub_elem = elem.find('.//{*}sub')
        e_str = omml_to_latex(e_elem) if e_elem is not None else ''
        sub_str = omml_to_latex(sub_elem) if sub_elem is not None else ''
        return f'{{{e_str}}}_{{{sub_str}}}'

    elif tag == 'sSubSup':
        e_elem = elem.find('.//{*}e')
        sub_elem = elem.find('.//{*}sub')
        sup_elem = elem.find('.//{*}sup')
        e_str = omml_to_latex(e_elem) if e_elem is not None else ''
        sub_str = omml_to_latex(sub_elem) if sub_elem is not None else ''
        sup_str = omml_to_latex(sup_elem) if sup_elem is not None else ''
        return f'{{{e_str}}}_{{{sub_str}}}^{{{sup_str}}}'

    elif tag == 'd':
        dPr = elem.find('.//{*}dPr')
        beg_chr = '('
        end_chr = ')'
        if dPr is not None:
            beg = dPr.find('.//{*}begChr')
            end = dPr.find('.//{*}endChr')
            if beg is not None: beg_chr = beg.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/math}val', beg_chr)
            if end is not None: end_chr = end.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/math}val', end_chr)
        e_elems = elem.findall('.//{*}e')
        inner = ''.join(omml_to_latex(e) for e in e_elems)
        beg_map = {'(': r'\left(', '[': r'\left[', '{': r'\left\{'}
        end_map = {')': r'\right)', ']': r'\right]', '}': r'\right\}'}
        b_str = beg_map.get(beg_chr, beg_chr)
        e_str = end_map.get(end_chr, end_chr)
        return f'{b_str}{inner}{e_str}'

    elif tag == 'nary':
        naryPr = elem.find('.//{*}naryPr')
        chr_val = '∑'
        if naryPr is not None:
            c = naryPr.find('.//{*}chr')
            if c is not None: chr_val = c.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/math}val', chr_val)
        sub_elem = elem.find('.//{*}sub')
        sup_elem = elem.find('.//{*}sup')
        e_elem = elem.find('.//{*}e')
        sub_str = f'_{{{omml_to_latex(sub_elem)}}}' if sub_elem is not None else ''
        sup_str = f'^{{{omml_to_latex(sup_elem)}}}' if sup_elem is not None else ''
        e_str = omml_to_latex(e_elem) if e_elem is not None else ''
        op_symbol = r'\sum' if chr_val == '∑' else (r'\int' if chr_val == '∫' else chr_val)
        return f'{op_symbol}{sub_str}{sup_str}{{{e_str}}}'

    elif tag == 'func':
        fname_elem = elem.find('.//{*}fName')
        e_elem = elem.find('.//{*}e')
        fname_str = omml_to_latex(fname_elem) if fname_elem is not None else ''
        e_str = omml_to_latex(e_elem) if e_elem is not None else ''
        return f'\\{fname_str}{{{e_str}}}'

    elif tag == 'rad':
        deg_elem = elem.find('.//{*}deg')
        e_elem = elem.find('.//{*}e')
        deg_str = f'[{omml_to_latex(deg_elem)}]' if deg_elem is not None and len(deg_elem) > 0 else ''
        e_str = omml_to_latex(e_elem) if e_elem is not None else ''
        return f'\\sqrt{deg_str}{{{e_str}}}'

    else:
        return ''.join(omml_to_latex(child) for child in elem)


def _render_equation_asset(latex_str, file_id, eq_filename, eq_dir):
    os.makedirs(eq_dir, exist_ok=True)
    out_path = os.path.join(eq_dir, eq_filename)
    if os.path.exists(out_path):
        try:
            with PILImage.open(out_path) as img:
                w, h = img.size
            return out_path, w, h
        except Exception:
            pass

    try:
        fig = plt.figure(figsize=(0.1, 0.1))
        formatted_latex = f"${latex_str}$" if not latex_str.startswith('$') else latex_str
        text = fig.text(0, 0, formatted_latex, fontsize=11)
        fig.canvas.draw()
        bbox = text.get_window_extent(fig.canvas.get_renderer())
        w_in, h_in = bbox.width / fig.dpi, bbox.height / fig.dpi
        fig.set_size_inches(w_in + 0.04, h_in + 0.04)
        plt.savefig(out_path, dpi=300, bbox_inches='tight', transparent=True, pad_inches=0.01)
        plt.close(fig)

        with PILImage.open(out_path) as img:
            return out_path, img.width, img.height
    except Exception as e:
        print(f"Warning: Failed to render equation latex '{latex_str}': {e}")
        return None, 0, 0


def _parse_cell_content(cell, file_id, eq_dir, row_idx):
    """
    Parse a cell's paragraphs to extract structured content segments (text runs and OMML equations).
    Returns tuple: (full_text_string, content_list)
    """
    content = []
    current_text = ""
    eq_counter = 0

    for p in cell.paragraphs:
        for child in p._element:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'r':
                t_elems = child.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                t_text = ''.join([t.text or '' for t in t_elems])
                if t_text:
                    current_text += t_text
            elif tag in ('oMath', 'oMathPara'):
                if current_text:
                    content.append({'type': 'text', 'value': current_text})
                    current_text = ""
                
                try:
                    omml_raw = ET.tostring(child, encoding='utf-8').decode('utf-8')
                    # Standardize namespace prefix to m:
                    omml_xml_clean = re.sub(r'xmlns:ns\d+="[^"]*"', '', omml_raw)
                    omml_xml_clean = re.sub(r'ns\d+:', 'm:', omml_xml_clean)
                    if 'xmlns:m=' not in omml_xml_clean:
                        omml_xml_clean = omml_xml_clean.replace('<m:oMath', '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"')

                    latex = omml_to_latex(child)
                    if latex.strip():
                        eq_counter += 1
                        eq_filename = f"eq_{row_idx}_{eq_counter}.png"
                        out_path, w, h = _render_equation_asset(latex, file_id, eq_filename, eq_dir)
                        url = f"/api/equations/{file_id}/{eq_filename}"
                        aspect_ratio = (w / float(h)) if h > 0 else 1.0
                        
                        content.append({
                            'type': 'equation',
                            'latex': latex,
                            'omml': omml_xml_clean,
                            'local_path': out_path,
                            'url': url,
                            'width': w,
                            'height': h,
                            'aspect_ratio': aspect_ratio
                        })
                except Exception as e:
                    print(f"Warning: Exception parsing equation in row {row_idx}: {e}")

        if current_text and not current_text.endswith(' '):
            current_text += ' '

    if current_text:
        content.append({'type': 'text', 'value': current_text})

    # Consolidate adjacent text segments in content
    consolidated = []
    for item in content:
        if consolidated and consolidated[-1]['type'] == 'text' and item['type'] == 'text':
            consolidated[-1]['value'] += item['value']
        else:
            consolidated.append(item)

    full_text = "".join([item['value'] if item['type'] == 'text' else f" ${item.get('latex', '')}$ " for item in consolidated]).strip()

    return full_text, consolidated


def _parse_part_a(table, start_idx, end_idx, doc, file_id, img_dir, eq_dir=None):
    """Parse Part A questions into dictionary grouped by question number."""
    questions = {}
    if start_idx is None:
        return questions

    last_q = None

    for r_idx in range(start_idx + 1, end_idx):
        row = table.rows[r_idx]
        cells_text = [cell.text.strip() for cell in row.cells]
        if len(cells_text) < 3:
            continue

        row_imgs = _extract_row_images(row, r_idx, doc, file_id, img_dir)

        q_no_raw = cells_text[0].strip()
        alt_raw = cells_text[1].strip() if len(cells_text) > 1 else '1'
        
        # Extract rich text and equations from cell 2
        text, content = _parse_cell_content(row.cells[2], file_id, eq_dir, r_idx) if eq_dir else (cells_text[2].strip(), [{'type': 'text', 'value': cells_text[2].strip()}])
        if not text and len(cells_text) > 2:
            text = cells_text[2].strip()

        k_level = cells_text[3].strip() if len(cells_text) > 3 else ''
        co = cells_text[4].strip() if len(cells_text) > 4 else ''

        q_match = re.search(r'(\d+)', q_no_raw)
        if not q_match:
            if row_imgs and last_q:
                for img_url in row_imgs:
                    if img_url not in last_q['images']:
                        last_q['images'].append(img_url)
            continue

        if not text and not row_imgs:
            continue

        q_no = int(q_match.group(1))
        alt_idx = int(alt_raw) if alt_raw.isdigit() else 1

        if q_no not in questions:
            questions[q_no] = []

        q_obj = {
            'text': text,
            'content': content,
            'k_level': k_level,
            'co': co,
            'alt_index': alt_idx,
            'images': list(row_imgs),
        }
        questions[q_no].append(q_obj)
        last_q = q_obj

    return questions


def _parse_part_bc(table, start_idx, end_idx, doc, file_id, img_dir, eq_dir=None):
    """Parse Part B or Part C questions into dictionary grouped by question number and sub-part (a/b)."""
    questions = {}
    if start_idx is None:
        return questions

    current_q_no = None
    last_q_sub = None

    for r_idx in range(start_idx + 1, end_idx):
        row = table.rows[r_idx]
        cells_text = [cell.text.strip() for cell in row.cells]
        if len(cells_text) < 3:
            continue

        row_imgs = _extract_row_images(row, r_idx, doc, file_id, img_dir)

        q_no_raw = cells_text[0].strip()
        alt_raw = cells_text[1].strip() if len(cells_text) > 1 else '1'
        
        # Extract rich text and equations from cell 2
        text, content = _parse_cell_content(row.cells[2], file_id, eq_dir, r_idx) if eq_dir else (cells_text[2].strip(), [{'type': 'text', 'value': cells_text[2].strip()}])
        if not text and len(cells_text) > 2:
            text = cells_text[2].strip()

        k_level = cells_text[3].strip() if len(cells_text) > 3 else ''
        co = cells_text[4].strip() if len(cells_text) > 4 else ''
        sub_part_raw = cells_text[5].strip() if len(cells_text) > 5 else ''

        q_match = re.search(r'(\d+)', q_no_raw)
        if q_match:
            current_q_no = int(q_match.group(1))

        if not current_q_no:
            if row_imgs and last_q_sub:
                for img_url in row_imgs:
                    if img_url not in last_q_sub['images']:
                        last_q_sub['images'].append(img_url)
            continue

        if not text and not row_imgs:
            continue

        sub_match = re.search(r'([abAB])', q_no_raw + ' ' + sub_part_raw)
        sub_part = sub_match.group(1).lower() if sub_match else 'a'
        alt_idx = int(alt_raw) if alt_raw.isdigit() else 1

        if current_q_no not in questions:
            questions[current_q_no] = {'a': [], 'b': []}

        q_obj = {
            'text': text,
            'content': content,
            'k_level': k_level,
            'co': co,
            'alt_index': alt_idx,
            'images': list(row_imgs),
        }
        questions[current_q_no][sub_part].append(q_obj)
        last_q_sub = q_obj

    return questions
