/**
 * PreviewSection Component
 * 
 * Renders the generated question paper matching the official printed JIT examination paper.
 * Avoids web-style HTML table grid borders, using clean document formatting matching qp.jpeg.
 * 
 * Props:
 *   paper — generated paper object from the backend (or null)
 */
export default function PreviewSection({ paper }) {
  if (!paper) return null;

  const { metadata, course_outcomes, part_a, part_b, part_c } = paper;

  return (
    <div className="paper-preview font-serif text-[12px] text-black leading-relaxed" id="preview-section">

      {/* ── Register Number (Top Right) ──────────────── */}
      <div className="flex justify-end mb-4">
        <div className="flex items-center gap-[2px]" style={{ fontSize: '11px' }}>
          <span className="font-bold mr-1.5 font-sans text-xs">Reg No</span>
          {Array.from({ length: 10 }).map((_, i) => (
            <div
              key={i}
              className="w-[18px] h-[22px] border border-black bg-white"
              style={{ borderWidth: '1.2px' }}
            />
          ))}
        </div>
      </div>

      {/* ── College Header Text ────────────────────────── */}
      <div className="text-center mb-3">
        <h2 className="font-bold text-sm tracking-wide uppercase">
          JEPPIAAR INSTITUTE OF TECHNOLOGY
        </h2>
        <p className="text-[11px] text-gray-800 font-medium">(An Autonomous Institution)</p>
        <p className="text-[10px] text-gray-700 italic font-medium">"Self-Belief | Self-Discipline | Self-Respect"</p>
        <p className="text-[10px] text-gray-700">Kunnam, Sunguvarchatram, Sriperumbudur – 631 604.</p>
      </div>

      {/* ── Exam Title ────────────────────────────────── */}
      <p className="text-center font-bold text-xs mb-3 tracking-wide uppercase">
        {metadata?.exam_type || 'CIE I'} – {metadata?.month_year || 'JULY 2026'}
      </p>

      {/* ── Metadata Grid ─────────────────────────────── */}
      <div className="grid grid-cols-2 gap-y-1 text-[11px] mb-3 pb-2 border-b border-gray-400">
        <p><span className="font-bold">SUB CODE:</span> {metadata?.su00 || metadata?.subject_code || '-'}</p>
        <p className="text-right"><span className="font-bold">SUBJECT:</span> {metadata?.su01 || metadata?.subject_name || '-'}</p>
        <p><span className="font-bold">Duration:</span> {metadata?.duration || '1 ½ hours'}</p>
        <p className="text-right"><span className="font-bold">Branch / Year / Sem:</span> {metadata?.branch_info || '-'}</p>
        <p><span className="font-bold">Date:</span> {metadata?.date || '___________'}</p>
        <p className="text-right"><span className="font-bold">Maximum:</span> {metadata?.max_marks_display || metadata?.max_marks || '-'}</p>
      </div>

      {/* ── Course Outcomes ────────────────────────────── */}
      {course_outcomes && course_outcomes.length > 0 && (
        <div className="mb-4 text-[11px]">
          <p className="font-bold mb-1">
            Course Outcome: – After Successful Completion of the Course, the Students should be able to
          </p>
          {course_outcomes.map((co, i) => (
            <div key={i} className="flex gap-4 mb-0.5 ml-4">
              <span className="font-bold min-w-[55px]">{co.id}</span>
              <span>{co.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* ── Instructions ──────────────────────────────── */}
      <p className="text-center font-bold text-[11px] mb-3">Answer all questions.</p>

      {/* ═══════════ PART A ═══════════════════════════ */}
      {part_a && (
        <div className="mb-5">
          <p className="font-bold text-center text-[11px] mb-2">
            PART – A ({part_a.config || '5 x 2 = 10 Marks'})
          </p>

          {/* Borderless Document Column Header */}
          <div className="flex font-bold text-[11px] py-1 border-b border-gray-300 mb-1">
            <div className="w-10 text-center">Q.NO</div>
            <div className="flex-1 text-center">QUESTIONS</div>
            <div className="w-14 text-center">CO NO.</div>
            <div className="w-14 text-center">MARKS</div>
            <div className="w-16 text-center">K LEVEL</div>
          </div>

          {/* Questions Rows */}
          <div className="space-y-2 text-[11px]">
            {part_a.questions.map((q, i) => (
              <div key={i} className="flex items-start">
                <div className="w-10 text-center font-medium pt-0.5">{q.q_no}</div>
                <div className="flex-1 pr-3">{q.text}</div>
                <div className="w-14 text-center pt-0.5">{q.co}</div>
                <div className="w-14 text-center pt-0.5">{q.marks}</div>
                <div className="w-16 text-center pt-0.5">{q.k_level}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══════════ PART B ═══════════════════════════ */}
      {part_b && (
        <div className="mb-5">
          <p className="font-bold text-center text-[11px] mb-2">
            PART – B ({part_b.config || '2 x 13 = 26 Marks'})
          </p>

          {/* Header */}
          <div className="flex font-bold text-[11px] py-1 border-b border-gray-300 mb-1">
            <div className="w-10 text-center">Q.NO</div>
            <div className="flex-1 text-center">QUESTIONS</div>
            <div className="w-14 text-center">CO NO.</div>
            <div className="w-14 text-center">MARKS</div>
            <div className="w-16 text-center">K LEVEL</div>
          </div>

          <div className="space-y-3 text-[11px]">
            {part_b.questions.map((group, gi) => (
              <div key={gi} className="space-y-1">
                {/* (a) Question */}
                <div className="flex items-start">
                  <div className="w-10 text-center font-bold">{group.q_no}.</div>
                  <div className="flex-1 pr-3">
                    <span className="font-bold mr-1">a)</span> {group.a.text}
                  </div>
                  <div className="w-14 text-center">{group.a.co}</div>
                  <div className="w-14 text-center">{group.a.marks}</div>
                  <div className="w-16 text-center">{group.a.k_level}</div>
                </div>

                {/* (OR) Separator */}
                <div className="text-center font-bold text-[10px] py-0.5">
                  (OR)
                </div>

                {/* (b) Question */}
                <div className="flex items-start">
                  <div className="w-10"></div>
                  <div className="flex-1 pr-3">
                    <span className="font-bold mr-1">b)</span> {group.b.text}
                  </div>
                  <div className="w-14 text-center">{group.b.co}</div>
                  <div className="w-14 text-center">{group.b.marks}</div>
                  <div className="w-16 text-center">{group.b.k_level}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══════════ PART C ═══════════════════════════ */}
      {part_c && (
        <div className="mb-6">
          <p className="font-bold text-center text-[11px] mb-2">
            PART – C ({part_c.config || '1 x 14 = 14 Marks'})
          </p>

          {/* Header */}
          <div className="flex font-bold text-[11px] py-1 border-b border-gray-300 mb-1">
            <div className="w-10 text-center">Q.NO</div>
            <div className="flex-1 text-center">QUESTIONS</div>
            <div className="w-14 text-center">CO NO.</div>
            <div className="w-14 text-center">MARKS</div>
            <div className="w-16 text-center">K LEVEL</div>
          </div>

          <div className="space-y-3 text-[11px]">
            {part_c.questions.map((group, gi) => (
              <div key={gi} className="space-y-1">
                {/* (a) Question */}
                <div className="flex items-start">
                  <div className="w-10 text-center font-bold">{group.q_no}.</div>
                  <div className="flex-1 pr-3">
                    <span className="font-bold mr-1">a)</span> {group.a.text}
                  </div>
                  <div className="w-14 text-center">{group.a.co}</div>
                  <div className="w-14 text-center">{group.a.marks}</div>
                  <div className="w-16 text-center">{group.a.k_level}</div>
                </div>

                {/* (OR) Separator */}
                <div className="text-center font-bold text-[10px] py-0.5">
                  (OR)
                </div>

                {/* (b) Question */}
                <div className="flex items-start">
                  <div className="w-10"></div>
                  <div className="flex-1 pr-3">
                    <span className="font-bold mr-1">b)</span> {group.b.text}
                  </div>
                  <div className="w-14 text-center">{group.b.co}</div>
                  <div className="w-14 text-center">{group.b.marks}</div>
                  <div className="w-16 text-center">{group.b.k_level}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── EXAMCELL Footer Block ───────────────────────── */}
      <div className="text-center my-6 space-y-0.5">
        <p className="font-bold text-xs">EXAMCELL</p>
        <p className="font-bold text-[11px]">Jeppiaar Institute of Technology (Autonomous)</p>
        <p className="text-[10px] text-gray-700">Kunnam, Sunguvarchatram, Sriperumbudur – 631 604.</p>
      </div>

      {/* ── K-Level Legend ─────────────────────────────── */}
      <p className="text-[11px] text-center text-gray-600 border-t border-gray-200 pt-2">
        K1-Remembering, K2-Understanding, K3-Applying, K4-Analysing, K5-Evaluating, K6-Creating
      </p>
    </div>
  );
}
