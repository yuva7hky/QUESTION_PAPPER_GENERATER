"""
parser.py — DOCX Question Bank Parser.

Reads a .docx file containing a single-table Question Bank and extracts:
  - Metadata (semester, branch, subject code, subject name)
  - Course Outcomes (CO1–CO6)
  - Part A questions grouped by question number
  - Part B questions grouped by question number and sub-part (a/b)
  - Part C questions (same structure as Part B)
  - Marks distribution from section headers

The parser is designed around the observed QB format:
  - One large table (146 rows × 6 columns)
  - Metadata rows at top (SE00, BR00, SU00, CO1#–CO6#)
  - Section header rows ("Part-A ...", "Part – B ...", "Part – C ...")
  - Question rows with: Q.No, Alt#, QuestionText, KLevel, CO, S/A
"""

import re
from docx import Document


def parse_question_bank(filepath):
    """
    Parse a Question Bank .docx file.
    
    Args:
        filepath: Path to the .docx file.
    
    Returns:
        dict with keys:
            metadata: { semester, branch, subject_code, subject_name, branch_info }
            course_outcomes: [ { id, text } ]
            part_a: { config, questions: { q_no: [ { text, k_level, co, alt_index } ] } }
            part_b: { config, questions: { q_no: { a: [...], b: [...] } } }
            part_c: { config, questions: { q_no: { a: [...], b: [...] } } }
    """
    doc = Document(filepath)

    if not doc.tables:
        raise ValueError("No tables found in the document. Expected a table-based Question Bank.")

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
        if 'part-a' in text or 'part – a' in text or 'part- a' in text or 'part -a' in text:
            part_a_start = i
            part_a_config = _extract_marks_config(row[2])
        elif 'part-b' in text or 'part – b' in text or 'part- b' in text or 'part -b' in text:
            part_b_start = i
            part_b_config = _extract_marks_config(row[2])
        elif 'part-c' in text or 'part – c' in text or 'part- c' in text or 'part -c' in text:
            part_c_start = i
            part_c_config = _extract_marks_config(row[2])

    # ── Parse Part A ──────────────────────────────────────
    part_a_end = part_b_start if part_b_start else len(rows)
    part_a_questions = _parse_part_a(rows, part_a_start, part_a_end)

    # ── Parse Part B ──────────────────────────────────────
    part_b_end = part_c_start if part_c_start else len(rows)
    part_b_questions = _parse_part_bc(rows, part_b_start, part_b_end)

    # ── Parse Part C ──────────────────────────────────────
    part_c_questions = _parse_part_bc(rows, part_c_start, len(rows))

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


def _extract_metadata(rows):
    """Extract semester, branch, subject code, and subject name from metadata rows."""
    metadata = {
        'semester': '',
        'branch': '',
        'subject_code': '',
        'subject_name': '',
        'branch_info': '',
    }

    for row in rows[:12]:  # Metadata is in the first ~12 rows
        col0 = row[0].strip().upper() if row[0] else ''
        col2 = row[2].strip() if len(row) > 2 else ''

        if col0 == 'SE00' or col0.startswith('SE'):
            metadata['semester'] = col2

        elif col0 == 'BR00' or col0.startswith('BR'):
            metadata['branch'] = col2
            metadata['branch_info'] = col2

        elif col0 == 'SU00' or col0.startswith('SU'):
            # Format: "22AI401 – MACHINE LEARNING  (Lab integrated)"
            match = re.match(r'([A-Z0-9]+)\s*[–\-]\s*(.*)', col2)
            if match:
                metadata['subject_code'] = match.group(1).strip()
                metadata['subject_name'] = match.group(2).strip()
            else:
                metadata['subject_name'] = col2

    return metadata


def _extract_course_outcomes(rows):
    """Extract course outcomes (CO1–CO6) from the metadata section."""
    outcomes = []
    for row in rows[:15]:
        col0 = row[0].strip().upper() if row[0] else ''
        col2 = row[2].strip() if len(row) > 2 else ''

        # Match CO1#, CO2#, etc.
        match = re.match(r'(CO\d+)#?', col0)
        if match and col2:
            outcomes.append({
                'id': match.group(1),
                'text': col2,
            })

    return outcomes


def _extract_marks_config(text):
    """
    Extract the marks configuration string from a section header.
    E.g., "Part-A (10 x 2 = 20 Marks)" → "10 x 2 = 20 Marks"
    """
    match = re.search(r'\(([^)]+)\)', text)
    if match:
        return match.group(1).strip()
    
    # Try without parentheses: "Part – A  10 x 2 = 20 Marks"
    match = re.search(r'(\d+\s*[x×]\s*\d+\s*=\s*\d+\s*Marks?)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return text


def _extract_marks_per_question(config):
    """
    Extract marks per question from config string.
    E.g., "10 x 2 = 20 Marks" → 2
    E.g., "5 x 13 = 65 Marks" → 13
    """
    match = re.search(r'\d+\s*[x×]\s*(\d+)', config)
    if match:
        return int(match.group(1))
    return 0


def _parse_part_a(rows, start_idx, end_idx):
    """
    Parse Part A questions. Each question number has multiple alternatives.
    
    Returns dict: { q_no: [ { text, k_level, co, alt_index } ] }
    """
    if start_idx is None:
        return {}

    questions = {}

    # Skip the header rows (section header + column headers)
    data_start = start_idx + 1
    # Find where actual question data begins (skip column header row)
    for i in range(data_start, min(data_start + 3, end_idx)):
        col0 = rows[i][0].strip().lower() if rows[i][0] else ''
        if 'qp' in col0 or 'q.no' in col0 or 'no' in col0:
            data_start = i + 1
            break

    for i in range(data_start, end_idx):
        row = rows[i]
        q_no_str = row[0].strip().rstrip('.')
        alt_str = row[1].strip() if len(row) > 1 else ''
        text = row[2].strip() if len(row) > 2 else ''
        k_level = row[3].strip() if len(row) > 3 else ''
        co = row[4].strip() if len(row) > 4 else ''

        # Skip empty rows or section headers
        if not text or not q_no_str:
            continue

        # Skip if q_no can't be parsed as a number
        try:
            q_no = int(q_no_str)
        except ValueError:
            continue

        try:
            alt_index = int(alt_str)
        except ValueError:
            alt_index = 1

        if q_no not in questions:
            questions[q_no] = []

        questions[q_no].append({
            'text': text,
            'k_level': k_level,
            'co': co,
            'alt_index': alt_index,
        })

    return questions


def _parse_part_bc(rows, start_idx, end_idx):
    """
    Parse Part B or Part C questions.
    Format: Q.a and Q.b with multiple alternatives each.
    
    Returns dict: { q_no: { 'a': [...], 'b': [...] } }
    """
    if start_idx is None:
        return {}

    questions = {}

    # Skip header rows
    data_start = start_idx + 1

    for i in range(data_start, end_idx):
        row = rows[i]
        q_no_str = row[0].strip().rstrip('.')
        alt_str = row[1].strip() if len(row) > 1 else ''
        text = row[2].strip() if len(row) > 2 else ''
        k_level = row[3].strip() if len(row) > 3 else ''
        co = row[4].strip() if len(row) > 4 else ''

        if not text or not q_no_str:
            continue

        # Parse format like "11.a" or "11.b" or "16.a."
        match = re.match(r'(\d+)\s*[.]\s*([ab])', q_no_str, re.IGNORECASE)
        if not match:
            continue

        q_no = int(match.group(1))
        sub_part = match.group(2).lower()

        try:
            alt_index = int(alt_str)
        except ValueError:
            alt_index = 1

        if q_no not in questions:
            questions[q_no] = {'a': [], 'b': []}

        questions[q_no][sub_part].append({
            'text': text,
            'k_level': k_level,
            'co': co,
            'alt_index': alt_index,
        })

    return questions
