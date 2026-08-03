"""
utils.py — Shared utilities for the Question Paper Generation System.

Provides:
  - Exam type constants (future-ready)
  - Unique hash generation for paper fingerprinting
  - In-memory store for tracking generated paper hashes
  - UUID generation for download file IDs
"""

import hashlib
import uuid

# ── Exam Type Constants ──────────────────────────────────────
# Currently only CIE_I is implemented. The architecture supports
# adding new types with minimal changes to the selector/generator.
EXAM_TYPES = {
    'CIE_I': 'CIE I',
    'CIE_II': 'CIE II',
    'MODEL': 'Model Examination',
    'SEMESTER': 'Semester Examination',
}

# ── In-Memory Store for Generated Paper Hashes ───────────────
# Key: file_id, Value: set of fingerprint hashes
# This ensures uniqueness per uploaded question bank.
_generated_hashes = {}


def generate_paper_fingerprint(selected_questions):
    """
    Create a deterministic hash from the selected question indices.
    
    Args:
        selected_questions: dict with 'part_a', 'part_b', 'part_c' keys,
                           each containing the selected alternative indices.
    
    Returns:
        A hex digest string representing this unique combination.
    """
    # Build a canonical string from all selections
    parts = []

    # Part A: list of (question_number, alternative_index) tuples
    part_a = selected_questions.get('part_a', {})
    for q in (part_a.get('questions', []) if isinstance(part_a, dict) else part_a):
        parts.append(f"A-{q['q_no']}-{q['alt_index']}")

    # Part B: list of (question_number, sub_part, alternative_index)
    part_b = selected_questions.get('part_b', {})
    for g in (part_b.get('questions', []) if isinstance(part_b, dict) else part_b):
        parts.append(f"B-{g['q_no']}-a-{g['a']['alt_index']}")
        parts.append(f"B-{g['q_no']}-b-{g['b']['alt_index']}")

    # Part C: same structure as Part B
    part_c = selected_questions.get('part_c', {})
    for g in (part_c.get('questions', []) if isinstance(part_c, dict) else part_c):
        parts.append(f"C-{g['q_no']}-a-{g['a']['alt_index']}")
        parts.append(f"C-{g['q_no']}-b-{g['b']['alt_index']}")

    canonical = '|'.join(parts)
    return hashlib.sha256(canonical.encode()).hexdigest()


def is_paper_unique(file_id, fingerprint):
    """
    Check if a paper with this fingerprint has been generated before
    for the given file_id.
    
    Returns True if unique, False if duplicate.
    """
    if file_id not in _generated_hashes:
        _generated_hashes[file_id] = set()

    return fingerprint not in _generated_hashes[file_id]


def register_paper(file_id, fingerprint):
    """Register a generated paper's fingerprint."""
    if file_id not in _generated_hashes:
        _generated_hashes[file_id] = set()
    _generated_hashes[file_id].add(fingerprint)


def generate_paper_id():
    """Generate a unique ID for a paper (used for download endpoints)."""
    return str(uuid.uuid4())[:8]


def get_generated_count(file_id):
    """Get the number of unique papers generated for a file."""
    return len(_generated_hashes.get(file_id, set()))
