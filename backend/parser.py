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

    # Image storage directory for this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, 'uploads', 'images', file_id)
    os.makedirs(img_dir, exist_ok=True)

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
    part_a_questions = _parse_part_a(table, part_a_start, part_a_end, doc, file_id, img_dir)

    # ── Parse Part B ──────────────────────────────────────
    part_b_end = part_c_start if part_c_start else len(rows)
    part_b_questions = _parse_part_bc(table, part_b_start, part_b_end, doc, file_id, img_dir)

    # ── Parse Part C ──────────────────────────────────────
    part_c_questions = _parse_part_bc(table, part_c_start, len(rows), doc, file_id, img_dir)

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


def _parse_part_a(table, start_idx, end_idx, doc, file_id, img_dir):
    """Parse Part A questions into dictionary grouped by question number."""
    questions = {}
    if start_idx is None:
        return questions

    last_q = None

    for r_idx in range(start_idx + 1, end_idx):
        row = table.rows[r_idx]
        cells = [cell.text.strip() for cell in row.cells]
        if len(cells) < 3:
            continue

        row_imgs = _extract_row_images(row, r_idx, doc, file_id, img_dir)

        q_no_raw = cells[0].strip()
        alt_raw = cells[1].strip() if len(cells) > 1 else '1'
        text = cells[2].strip() if len(cells) > 2 else ''
        k_level = cells[3].strip() if len(cells) > 3 else ''
        co = cells[4].strip() if len(cells) > 4 else ''

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
            'k_level': k_level,
            'co': co,
            'alt_index': alt_idx,
            'images': list(row_imgs),
        }
        questions[q_no].append(q_obj)
        last_q = q_obj

    return questions


def _parse_part_bc(table, start_idx, end_idx, doc, file_id, img_dir):
    """Parse Part B or Part C questions into dictionary grouped by question number and sub-part (a/b)."""
    questions = {}
    if start_idx is None:
        return questions

    current_q_no = None
    last_q_sub = None

    for r_idx in range(start_idx + 1, end_idx):
        row = table.rows[r_idx]
        cells = [cell.text.strip() for cell in row.cells]
        if len(cells) < 3:
            continue

        row_imgs = _extract_row_images(row, r_idx, doc, file_id, img_dir)

        q_no_raw = cells[0].strip()
        alt_raw = cells[1].strip() if len(cells) > 1 else '1'
        text = cells[2].strip() if len(cells) > 2 else ''
        k_level = cells[3].strip() if len(cells) > 3 else ''
        co = cells[4].strip() if len(cells) > 4 else ''
        sub_part_raw = cells[5].strip() if len(cells) > 5 else ''

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
            'k_level': k_level,
            'co': co,
            'alt_index': alt_idx,
            'images': list(row_imgs),
        }
        questions[current_q_no][sub_part].append(q_obj)
        last_q_sub = q_obj

    return questions
