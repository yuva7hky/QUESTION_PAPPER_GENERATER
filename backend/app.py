"""
app.py — Flask Backend for Question Paper Generation System.

API Endpoints:
  POST /api/upload        — Upload a Question Bank (.docx)
  POST /api/generate      — Generate a unique question paper
  GET  /api/download/pdf/<id>  — Download generated paper as PDF
  GET  /api/download/docx/<id> — Download generated paper as DOCX
"""

import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from parser import parse_question_bank
from generator import generate_paper
from pdf_generator import generate_pdf
from docx_generator import generate_docx

# ── App Configuration ─────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# Directories (scoped within backend package or temp directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
GENERATED_DIR = os.path.join(BASE_DIR, 'generated')

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# In-memory store for parsed data and generated papers
# Key: file_id → parsed_data
_parsed_cache = {}
# Key: paper_id → paper_data
_paper_cache = {}


# ── Health Check ──────────────────────────────────────────────
@app.route('/', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render / cloud monitoring."""
    return jsonify({
        'status': 'ok',
        'service': 'Question Paper Generation API'
    }), 200


# ── API: Upload ───────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload a Question Bank (.docx) file.
    
    Returns:
        JSON with file_id and parsed metadata summary.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if not file.filename.lower().endswith('.docx'):
        return jsonify({'error': 'Only .docx files are accepted.'}), 400

    # Save uploaded file
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)

    try:
        # Parse the question bank
        parsed_data = parse_question_bank(filepath)
        _parsed_cache[file_id] = parsed_data

        # Return summary
        metadata = parsed_data.get('metadata', {})
        part_a_count = len(parsed_data.get('part_a', {}).get('questions', {}))
        part_b_count = len(parsed_data.get('part_b', {}).get('questions', {}))
        part_c_count = len(parsed_data.get('part_c', {}).get('questions', {}))

        return jsonify({
            'file_id': file_id,
            'message': 'File uploaded and parsed successfully.',
            'summary': {
                'subject_code': metadata.get('subject_code', ''),
                'subject_name': metadata.get('subject_name', ''),
                'branch': metadata.get('branch', ''),
                'part_a_groups': part_a_count,
                'part_b_groups': part_b_count,
                'part_c_groups': part_c_count,
                'course_outcomes': len(parsed_data.get('course_outcomes', [])),
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to parse document: {str(e)}'}), 500


# ── API: Generate ─────────────────────────────────────────────
@app.route('/api/generate', methods=['POST'])
def generate():
    """
    Generate a unique question paper from a previously uploaded file.
    
    Request body:
        { "file_id": "abc12345", "exam_type": "CIE_I" }
    
    Returns:
        JSON with paper_id and complete paper data.
    """
    data = request.get_json()
    if not data or 'file_id' not in data:
        return jsonify({'error': 'file_id is required.'}), 400

    file_id = data['file_id']
    exam_type = data.get('exam_type', 'CIE_I')

    if file_id not in _parsed_cache:
        return jsonify({'error': 'File not found. Please upload again.'}), 404

    parsed_data = _parsed_cache[file_id]

    try:
        result = generate_paper(parsed_data, file_id, exam_type)
        paper_id = result['paper_id']
        paper_data = result['paper']

        # Cache for download
        _paper_cache[paper_id] = paper_data

        return jsonify({
            'paper_id': paper_id,
            'paper': paper_data,
        }), 200

    except RuntimeError as e:
        return jsonify({'error': str(e)}), 409  # Conflict — all combinations exhausted

    except NotImplementedError as e:
        return jsonify({'error': str(e)}), 501  # Not yet implemented

    except Exception as e:
        return jsonify({'error': f'Failed to generate paper: {str(e)}'}), 500


# ── API: Download PDF ─────────────────────────────────────────
@app.route('/api/download/pdf/<paper_id>', methods=['GET'])
def download_pdf(paper_id):
    """Generate and download the question paper as PDF."""
    if paper_id not in _paper_cache:
        return jsonify({'error': 'Paper not found. Please generate again.'}), 404

    paper_data = _paper_cache[paper_id]
    output_path = os.path.join(GENERATED_DIR, f"{paper_id}.pdf")

    try:
        generate_pdf(paper_data, output_path)
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"Question_Paper_{paper_id}.pdf",
            mimetype='application/pdf',
        )
    except Exception as e:
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500


# ── API: Download DOCX ────────────────────────────────────────
@app.route('/api/download/docx/<paper_id>', methods=['GET'])
def download_docx(paper_id):
    """Generate and download the question paper as DOCX."""
    if paper_id not in _paper_cache:
        return jsonify({'error': 'Paper not found. Please generate again.'}), 404

    paper_data = _paper_cache[paper_id]
    output_path = os.path.join(GENERATED_DIR, f"{paper_id}.docx")

    try:
        generate_docx(paper_data, output_path)
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"Question_Paper_{paper_id}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
    except Exception as e:
        return jsonify({'error': f'Failed to generate DOCX: {str(e)}'}), 500


# ── Main ──────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
