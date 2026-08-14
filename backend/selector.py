"""
selector.py — Question Selection Engine.

Randomly selects questions from the parsed Question Bank to form
a complete question paper following the selected examination format:

  CIE_I (50 Marks):
    Part A: 5 x 2 = 10 Marks  — pick 5 from 10 question groups
    Part B: 2 x 13 = 26 Marks — pick 2 from 5 question groups (a/b with OR)
    Part C: 1 x 14 = 14 Marks — pick 1 from available groups (a/b with OR)

  MODEL (100 Marks):
    Part A: 10 x 2 = 20 Marks — all 10 question groups
    Part B: 5 x 13 = 65 Marks — all 5 question groups (a/b with OR)
    Part C: 1 x 15 = 15 Marks — 1 question group (a/b with OR)
"""

import random


def select_questions(parsed_data, exam_type='CIE_I'):
    """
    Select questions from parsed data to form a complete paper.
    
    Args:
        parsed_data: Output from parser.parse_question_bank()
        exam_type: Type of examination ('CIE_I' or 'MODEL')
    
    Returns:
        dict with selected questions structured for the generator.
    """
    if exam_type in ('CIE_I', 'CIE_II'):
        return _select_cie_i(parsed_data)
    elif exam_type == 'MODEL':
        return _select_model(parsed_data)
    else:
        raise ValueError(f"Unsupported exam type: {exam_type}. Supported: CIE_I, CIE_II, MODEL")


def _select_cie_i(parsed_data):
    """
    Select questions for CIE-I format (50 Marks).
    
    Pattern (from reference question paper):
      Part A: 5 x 2 = 10 Marks  — randomly pick 5 from available question groups
      Part B: 2 x 13 = 26 Marks — randomly pick 2 question groups (a OR b)
      Part C: 1 x 14 = 14 Marks — pick 1 question group (a OR b)
    """
    part_a_data = parsed_data['part_a']
    part_b_data = parsed_data['part_b']
    part_c_data = parsed_data['part_c']

    # ── Part A: pick 5 question groups, then 1 alternative each ──
    part_a_selected = []
    part_a_marks = 2

    all_a_q_nos = sorted(part_a_data['questions'].keys())
    selected_a_q_nos = random.sample(all_a_q_nos, min(5, len(all_a_q_nos)))
    for new_q_no, orig_q_no in enumerate(selected_a_q_nos, 1):
        alternatives = part_a_data['questions'][orig_q_no]
        if not alternatives:
            continue
        chosen = random.choice(alternatives)
        part_a_selected.append({
            'q_no': new_q_no,
            'text': chosen['text'],
            'content': chosen.get('content', []),
            'k_level': chosen['k_level'],
            'co': chosen['co'],
            'marks': part_a_marks,
            'alt_index': chosen['alt_index'],
            'images': chosen.get('images', []),
        })

    # ── Part B: pick 2 question groups, then 1 alternative per sub-part ──
    part_b_selected = []
    part_b_marks = 13

    all_b_q_nos = sorted(part_b_data['questions'].keys())
    selected_b_q_nos = random.sample(all_b_q_nos, min(2, len(all_b_q_nos)))
    selected_b_q_nos.sort()

    for new_q_no, orig_q_no in enumerate(selected_b_q_nos, 6):
        group = part_b_data['questions'][orig_q_no]
        a_alternatives = group.get('a', [])
        b_alternatives = group.get('b', [])

        if not a_alternatives or not b_alternatives:
            continue

        chosen_a = random.choice(a_alternatives)
        chosen_b = random.choice(b_alternatives)

        part_b_selected.append({
            'q_no': new_q_no,
            'a': {
                'text': chosen_a['text'],
                'content': chosen_a.get('content', []),
                'k_level': chosen_a['k_level'],
                'co': chosen_a['co'],
                'marks': part_b_marks,
                'alt_index': chosen_a['alt_index'],
                'images': chosen_a.get('images', []),
            },
            'b': {
                'text': chosen_b['text'],
                'content': chosen_b.get('content', []),
                'k_level': chosen_b['k_level'],
                'co': chosen_b['co'],
                'marks': part_b_marks,
                'alt_index': chosen_b['alt_index'],
                'images': chosen_b.get('images', []),
            },
        })

    # ── Part C: pick 1 question group ──────────────────────
    part_c_selected = []
    part_c_marks = 14

    all_c_q_nos = sorted(part_c_data['questions'].keys())
    if all_c_q_nos:
        selected_c_q_nos = random.sample(all_c_q_nos, min(1, len(all_c_q_nos)))
        
        for new_q_no, orig_q_no in enumerate(selected_c_q_nos, 8):
            group = part_c_data['questions'][orig_q_no]
            a_alternatives = group.get('a', [])
            b_alternatives = group.get('b', [])

            if not a_alternatives or not b_alternatives:
                continue

            chosen_a = random.choice(a_alternatives)
            chosen_b = random.choice(b_alternatives)

            part_c_selected.append({
                'q_no': new_q_no,
                'a': {
                    'text': chosen_a['text'],
                    'content': chosen_a.get('content', []),
                    'k_level': chosen_a['k_level'],
                    'co': chosen_a['co'],
                    'marks': part_c_marks,
                    'alt_index': chosen_a['alt_index'],
                    'images': chosen_a.get('images', []),
                },
                'b': {
                    'text': chosen_b['text'],
                    'content': chosen_b.get('content', []),
                    'k_level': chosen_b['k_level'],
                    'co': chosen_b['co'],
                    'marks': part_c_marks,
                    'alt_index': chosen_b['alt_index'],
                    'images': chosen_b.get('images', []),
                },
            })

    return {
        'metadata': dict(parsed_data['metadata']),
        'course_outcomes': parsed_data['course_outcomes'],
        'part_a': {
            'config': '5 x 2 = 10 Marks',
            'questions': part_a_selected,
        },
        'part_b': {
            'config': '2 x 13 = 26 Marks',
            'questions': part_b_selected,
        },
        'part_c': {
            'config': '1 x 14 = 14 Marks',
            'questions': part_c_selected,
        },
    }


def _select_model(parsed_data):
    """
    Select questions for Model Examination format (100 Marks).
    
    Pattern:
      Part A: 10 x 2 = 20 Marks — all 10 question groups, pick 1 alternative each
      Part B: 5 x 13 = 65 Marks — all 5 question groups, pick 1 alternative per sub-part (a/b)
      Part C: 1 x 15 = 15 Marks — 1 question group, pick 1 alternative per sub-part (a/b)
    """
    part_a_data = parsed_data['part_a']
    part_b_data = parsed_data['part_b']
    part_c_data = parsed_data['part_c']

    # ── Part A: 10 questions x 2 marks = 20 marks ──
    part_a_selected = []
    part_a_marks = 2

    for q_no in sorted(part_a_data['questions'].keys()):
        alternatives = part_a_data['questions'][q_no]
        if not alternatives:
            continue
        chosen = random.choice(alternatives)
        part_a_selected.append({
            'q_no': q_no,
            'text': chosen['text'],
            'content': chosen.get('content', []),
            'k_level': chosen['k_level'],
            'co': chosen['co'],
            'marks': part_a_marks,
            'alt_index': chosen['alt_index'],
            'images': chosen.get('images', []),
        })

    # ── Part B: 5 question groups x 13 marks = 65 marks ──
    part_b_selected = []
    part_b_marks = 13

    for q_no in sorted(part_b_data['questions'].keys()):
        group = part_b_data['questions'][q_no]
        a_alternatives = group.get('a', [])
        b_alternatives = group.get('b', [])

        if not a_alternatives or not b_alternatives:
            continue

        chosen_a = random.choice(a_alternatives)
        chosen_b = random.choice(b_alternatives)

        part_b_selected.append({
            'q_no': q_no,
            'a': {
                'text': chosen_a['text'],
                'content': chosen_a.get('content', []),
                'k_level': chosen_a['k_level'],
                'co': chosen_a['co'],
                'marks': part_b_marks,
                'alt_index': chosen_a['alt_index'],
                'images': chosen_a.get('images', []),
            },
            'b': {
                'text': chosen_b['text'],
                'content': chosen_b.get('content', []),
                'k_level': chosen_b['k_level'],
                'co': chosen_b['co'],
                'marks': part_b_marks,
                'alt_index': chosen_b['alt_index'],
                'images': chosen_b.get('images', []),
            },
        })

    # ── Part C: 1 question group x 15 marks = 15 marks ──
    part_c_selected = []
    part_c_marks = 15

    all_c_q_nos = sorted(part_c_data['questions'].keys())
    if all_c_q_nos:
        # Pick 1 group for Part C
        chosen_c_q_no = random.choice(all_c_q_nos)
        group = part_c_data['questions'][chosen_c_q_no]
        a_alternatives = group.get('a', [])
        b_alternatives = group.get('b', [])

        if a_alternatives and b_alternatives:
            chosen_a = random.choice(a_alternatives)
            chosen_b = random.choice(b_alternatives)

            # Part C question number comes after Part B (e.g. 16)
            part_c_selected.append({
                'q_no': 16,
                'a': {
                    'text': chosen_a['text'],
                    'content': chosen_a.get('content', []),
                    'k_level': chosen_a['k_level'],
                    'co': chosen_a['co'],
                    'marks': part_c_marks,
                    'alt_index': chosen_a['alt_index'],
                    'images': chosen_a.get('images', []),
                },
                'b': {
                    'text': chosen_b['text'],
                    'content': chosen_b.get('content', []),
                    'k_level': chosen_b['k_level'],
                    'co': chosen_b['co'],
                    'marks': part_c_marks,
                    'alt_index': chosen_b['alt_index'],
                    'images': chosen_b.get('images', []),
                },
            })

    return {
        'metadata': dict(parsed_data['metadata']),
        'course_outcomes': parsed_data['course_outcomes'],
        'part_a': {
            'config': '10 x 2 = 20 Marks',
            'questions': part_a_selected,
        },
        'part_b': {
            'config': '5 x 13 = 65 Marks',
            'questions': part_b_selected,
        },
        'part_c': {
            'config': '1 x 15 = 15 Marks',
            'questions': part_c_selected,
        },
    }
