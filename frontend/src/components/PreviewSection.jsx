import katex from 'katex';
import 'katex/dist/katex.min.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Resolve asset URL against API_BASE_URL if configured.
 * In local dev (or empty base URL), returns the relative path (/api/...) for Vite proxy.
 * In production (with VITE_API_BASE_URL set), resolves to full backend URL.
 */
function getAssetUrl(url) {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('blob:') || url.startsWith('data:')) {
    return url;
  }
  if (API_BASE_URL && url.startsWith('/api/')) {
    const base = API_BASE_URL.replace(/\/+$/, '');
    return `${base}${url}`;
  }
  return url;
}

/**
 * Strip $ delimiters from LaTeX strings.
 * Handles: $...$, ${...}$, $$...$$
 */
function stripLatexDelimiters(latex) {
  if (!latex) return '';
  let s = latex.trim();
  // Strip $$...$$ first
  if (s.startsWith('$$') && s.endsWith('$$')) {
    s = s.slice(2, -2).trim();
  }
  // Strip $...$
  else if (s.startsWith('$') && s.endsWith('$')) {
    s = s.slice(1, -1).trim();
  }
  return s;
}

/**
 * Render a LaTeX string to HTML using KaTeX.
 * Returns the HTML string, or the original text on failure.
 */
function renderLatexToHtml(latex) {
  const cleaned = stripLatexDelimiters(latex);
  if (!cleaned) return null;
  try {
    return katex.renderToString(cleaned, {
      throwOnError: true,
      displayMode: false,
      output: 'html',
    });
  } catch {
    return null;
  }
}

/**
 * Render a text string that may contain inline $...$ LaTeX fragments.
 * Splits on $ delimiters and renders math segments with KaTeX.
 */
function renderTextWithLatex(text) {
  if (!text) return null;
  // Match $...$ (non-greedy, no nested $)
  const parts = text.split(/(\$[^$]+\$)/g);
  if (parts.length === 1) {
    // No LaTeX found
    return <span>{text}</span>;
  }
  return (
    <>
      {parts.map((part, idx) => {
        if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
          const html = renderLatexToHtml(part);
          if (html) {
            return (
              <span
                key={idx}
                className="katex-inline"
                dangerouslySetInnerHTML={{ __html: html }}
              />
            );
          }
          return <span key={idx}>{part}</span>;
        }
        return <span key={idx}>{part}</span>;
      })}
    </>
  );
}


function renderQuestionContent(q, prefix = '') {
  if (!q) return null;
  const content = q.content;
  if (content && content.length > 0) {
    return (
      <span className="inline break-words">
        {prefix && <span className="font-bold mr-1">{prefix}</span>}
        {content.map((item, idx) => {
          if (item.type === 'text') {
            return <span key={idx}>{renderTextWithLatex(item.value)}</span>;
          } else if (item.type === 'equation') {
            const latex = item.latex;
            const html = latex ? renderLatexToHtml(latex) : null;
            if (html) {
              return (
                <span
                  key={idx}
                  className="katex-inline"
                  dangerouslySetInnerHTML={{ __html: html }}
                />
              );
            }
            // Fallback to equation image
            if (item.url) {
              const isBlock = item.is_block;
              // Convert pt dimensions to CSS pixels (1pt = 96/72 px at standard screen DPI)
              // The PNG was rendered at 300 DPI, so we scale down to document pt size
              // 1pt = 1.3333px at 96dpi screen
              const origW = item.orig_w_pt || item.width_pt;
              const origH = item.orig_h_pt || item.height_pt;
              const PT_TO_PX = 96 / 72; // 1.3333
              const displayW = origW ? Math.round(origW * PT_TO_PX) : undefined;
              const displayH = origH ? Math.round(origH * PT_TO_PX) : undefined;

              return (
                <img
                  key={idx}
                  src={getAssetUrl(item.url)}
                  alt={item.latex || 'Math Equation'}
                  className={isBlock ? 'equation-block-img' : 'equation-inline-img'}
                  width={displayW}
                  height={displayH}
                  style={isBlock ? {
                    display: 'block',
                    margin: '4px 0',
                    width: displayW ? `${displayW}px` : 'auto',
                    height: displayH ? `${displayH}px` : 'auto',
                    maxWidth: '100%',
                    imageRendering: 'crisp-edges',
                  } : {
                    display: 'inline-block',
                    verticalAlign: '-0.3em',
                    width: displayW ? `${displayW}px` : 'auto',
                    height: displayH ? `${displayH}px` : 'auto',
                    maxHeight: '1.7em',
                    imageRendering: 'crisp-edges',
                  }}
                />
              );
            }
            if (latex) {
              return <span key={idx}>${latex}$</span>;
            }
            return null;
          }
          return null;
        })}
      </span>
    );
  }
  // Fallback: render q.text, which may contain inline $...$ LaTeX
  return (
    <div className="break-words">
      {prefix && <span className="font-bold mr-1">{prefix}</span>}
      {renderTextWithLatex(q.text)}
    </div>
  );
}


export default function PreviewSection({ paper }) {
  if (!paper) return null;

  const { metadata, course_outcomes, part_a, part_b, part_c } = paper;

  return (
    <div className="paper-preview font-serif text-[12px] text-black leading-relaxed" id="preview-section">

      {/* ── Register Number (Top Right) ──────────────── */}
      <div className="flex justify-end mb-4">
        <div className="flex items-center gap-[2px]" style={{ fontSize: '11px' }}>
          <span className="font-bold mr-1.5 font-sans text-xs">Reg No</span>
          {Array.from({ length: 12 }).map((_, i) => (
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
                <div className="flex-1 min-w-0 pr-3">
                  <div>{renderQuestionContent(q)}</div>
                  {q.images && q.images.length > 0 && (
                    <div className="mt-2 mb-1 flex flex-col items-center gap-2">
                      {q.images.map((imgSrc, imgIdx) => (
                        <img
                          key={imgIdx}
                          src={getAssetUrl(imgSrc)}
                          alt={`Diagram for question ${q.q_no}`}
                          className="max-h-56 max-w-full object-contain rounded border border-gray-200 shadow-2xs"
                        />
                      ))}
                    </div>
                  )}
                </div>
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
                  <div className="flex-1 min-w-0 pr-3">
                    {renderQuestionContent(group.a, 'a)')}
                    {group.a.images && group.a.images.length > 0 && (
                      <div className="mt-2 mb-1 flex flex-col items-center gap-2">
                        {group.a.images.map((imgSrc, imgIdx) => (
                          <img
                            key={imgIdx}
                            src={getAssetUrl(imgSrc)}
                            alt={`Diagram for question ${group.q_no}a`}
                            className="max-h-56 max-w-full object-contain rounded border border-gray-200 shadow-2xs"
                          />
                        ))}
                      </div>
                    )}
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
                  <div className="flex-1 min-w-0 pr-3">
                    {renderQuestionContent(group.b, 'b)')}
                    {group.b.images && group.b.images.length > 0 && (
                      <div className="mt-2 mb-1 flex flex-col items-center gap-2">
                        {group.b.images.map((imgSrc, imgIdx) => (
                          <img
                            key={imgIdx}
                            src={getAssetUrl(imgSrc)}
                            alt={`Diagram for question ${group.q_no}b`}
                            className="max-h-56 max-w-full object-contain rounded border border-gray-200 shadow-2xs"
                          />
                        ))}
                      </div>
                    )}
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
                  <div className="flex-1 min-w-0 pr-3">
                    {renderQuestionContent(group.a, 'a)')}
                    {group.a.images && group.a.images.length > 0 && (
                      <div className="mt-2 mb-1 flex flex-col items-center gap-2">
                        {group.a.images.map((imgSrc, imgIdx) => (
                          <img
                            key={imgIdx}
                            src={getAssetUrl(imgSrc)}
                            alt={`Diagram for question ${group.q_no}a`}
                            className="max-h-56 max-w-full object-contain rounded border border-gray-200 shadow-2xs"
                          />
                        ))}
                      </div>
                    )}
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
                  <div className="flex-1 min-w-0 pr-3">
                    {renderQuestionContent(group.b, 'b)')}
                    {group.b.images && group.b.images.length > 0 && (
                      <div className="mt-2 mb-1 flex flex-col items-center gap-2">
                        {group.b.images.map((imgSrc, imgIdx) => (
                          <img
                            key={imgIdx}
                            src={getAssetUrl(imgSrc)}
                            alt={`Diagram for question ${group.q_no}b`}
                            className="max-h-56 max-w-full object-contain rounded border border-gray-200 shadow-2xs"
                          />
                        ))}
                      </div>
                    )}
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
