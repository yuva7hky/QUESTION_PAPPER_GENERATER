"""
generator.py — Paper Generation & Uniqueness Engine.

Orchestrates the selection process and ensures every generated
question paper is unique by comparing hash fingerprints.

If a duplicate is detected, it re-rolls the selection until a
unique paper is produced (with a safety limit).
"""

from selector import select_questions
from utils import (
    generate_paper_fingerprint,
    is_paper_unique,
    register_paper,
    generate_paper_id,
    EXAM_TYPES,
)

# Maximum number of retries before giving up (safety valve)
MAX_RETRIES = 100


def generate_paper(parsed_data, file_id, exam_type='CIE_I'):
    """
    Generate a unique question paper.
    
    Args:
        parsed_data: Output from parser.parse_question_bank()
        file_id: Unique identifier for the uploaded file
        exam_type: Type of examination
    
    Returns:
        dict with:
            paper_id: unique download ID
            paper: complete paper structure for preview
    """
    selected = None
    for _ in range(MAX_RETRIES):
        selected = select_questions(parsed_data, exam_type)
        fingerprint = generate_paper_fingerprint(selected)

        if is_paper_unique(file_id, fingerprint):
            register_paper(file_id, fingerprint)
            break

    if selected is None:
        selected = select_questions(parsed_data, exam_type)

    paper_id = generate_paper_id()

    selected['metadata'] = dict(selected['metadata'])
    selected['metadata']['exam_type'] = EXAM_TYPES.get(exam_type, exam_type)
    selected['metadata']['max_marks'] = _calculate_max_marks(selected)
    selected['metadata']['date'] = '___________'
    selected['metadata']['month_year'] = _get_month_year()

    # Duration depends on exam type
    if exam_type in ('CIE_I', 'CIE_II'):
        selected['metadata']['duration'] = '1 ½ hours'
        selected['metadata']['max_marks_display'] = '50 Marks'
    elif exam_type == 'MODEL':
        selected['metadata']['duration'] = '3 hours'
        selected['metadata']['max_marks_display'] = '100 Marks'
    else:
        selected['metadata']['duration'] = '1 ½ hours'
        selected['metadata']['max_marks_display'] = '50 Marks'

    return {
        'paper_id': paper_id,
        'paper': selected,
    }


def _calculate_max_marks(selected):
    """Calculate total maximum marks from the paper structure."""
    total = 0

    # Part A: count × marks_per_question
    for q in selected.get('part_a', {}).get('questions', []):
        total += q.get('marks', 0)

    # Part B: count × marks_per_question (only one of a/b counts)
    for g in selected.get('part_b', {}).get('questions', []):
        total += g.get('a', {}).get('marks', 0)

    # Part C: count × marks_per_question
    for g in selected.get('part_c', {}).get('questions', []):
        total += g.get('a', {}).get('marks', 0)

    return str(total) + ' Marks'


def _get_month_year():
    """Get current month and year for the exam header."""
    import datetime
    now = datetime.datetime.now()
    return now.strftime('%B %Y').upper()
