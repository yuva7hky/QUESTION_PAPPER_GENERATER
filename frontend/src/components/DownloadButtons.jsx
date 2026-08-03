/**
 * DownloadButtons Component
 * 
 * PDF and DOCX download buttons for the bottom of the preview panel.
 * Disabled until a paper is generated.
 * 
 * Props:
 *   paperId        — generated paper ID (or null)
 *   onDownloadPdf  — callback to download PDF
 *   onDownloadDocx — callback to download DOCX
 *   downloading    — 'pdf' | 'docx' | null
 */
export default function DownloadButtons({ paperId, onDownloadPdf, onDownloadDocx, downloading }) {
  const isDisabled = !paperId;

  return (
    <div className="flex items-center justify-center gap-3 py-3 px-4 bg-gray-50 border-t border-gray-200 rounded-b-lg">
      {/* Download PDF */}
      <button
        onClick={onDownloadPdf}
        disabled={isDisabled || downloading === 'pdf'}
        className="btn-download"
        id="download-pdf-btn"
      >
        {downloading === 'pdf' ? (
          <>
            <svg className="animate-spin-slow w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Downloading…
          </>
        ) : (
          <>
            <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" opacity="0.2"/>
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zM14 2v6h6M10 13H8v5h2v-2h1a2 2 0 0 0 0-4h-1zm0 2v-1h1a.5.5 0 0 1 0 1h-1z"/>
            </svg>
            Download PDF
          </>
        )}
      </button>

      {/* Download DOCX */}
      <button
        onClick={onDownloadDocx}
        disabled={isDisabled || downloading === 'docx'}
        className="btn-download"
        id="download-docx-btn"
      >
        {downloading === 'docx' ? (
          <>
            <svg className="animate-spin-slow w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Downloading…
          </>
        ) : (
          <>
            <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" opacity="0.2"/>
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zM14 2v6h6"/>
            </svg>
            Download DOCX
          </>
        )}
      </button>
    </div>
  );
}
