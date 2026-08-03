/**
 * GenerateButton Component
 * 
 * Contains equal-width Generate and Regenerate buttons for the left panel.
 * 
 * Props:
 *   onGenerate    — callback for initial generation
 *   onRegenerate  — callback for regeneration (reuses uploaded file)
 *   loading       — whether generation is in progress
 *   disabled      — whether generation is disabled (no file uploaded)
 *   hasGenerated  — whether a paper has already been generated
 */
export default function GenerateButton({ onGenerate, onRegenerate, loading, disabled, hasGenerated }) {
  return (
    <div className="flex flex-col gap-2.5 w-full">
      {/* Primary Generate Button */}
      <button
        onClick={onGenerate}
        disabled={disabled || loading}
        className="btn-primary w-full h-11 text-sm font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2"
        id="generate-btn"
      >
        {loading ? (
          <>
            <svg className="animate-spin-slow w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Generating Paper…
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Generate Question Paper
          </>
        )}
      </button>

      {/* Equal-Width Regenerate Button (visible after generation) */}
      {hasGenerated && (
        <button
          onClick={onRegenerate}
          disabled={loading}
          className="btn-outline w-full h-11 text-sm font-semibold rounded-lg shadow-2xs flex items-center justify-center gap-2"
          id="regenerate-btn"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Regenerate Question Paper
        </button>
      )}
    </div>
  );
}
