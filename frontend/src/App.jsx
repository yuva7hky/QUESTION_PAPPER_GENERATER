import { useState, useCallback, useRef } from 'react';
import axios from 'axios';

// Configure API Base URL for local development and production deployment
axios.defaults.baseURL =
  import.meta.env.VITE_API_URL ||
  'https://question-paper-generator-6j5l.onrender.com';

import Header from './components/Header';
import UploadSection from './components/UploadSection';
import ExamTypeSelector from './components/ExamTypeSelector';
import GenerateButton from './components/GenerateButton';
import PreviewSection from './components/PreviewSection';
import DownloadButtons from './components/DownloadButtons';

/**
 * App — Root component for Question Paper Generation System.
 * 
 * Layout:
 * 1. Top Full-Width Header (Banner Image + Title)
 * 2. Two Panels below:
 *    - Left Panel (approx 40% width): Upload, Exam Type Selector, Generate/Regenerate Buttons, Status
 *    - Right Panel (approx 60% width): Paper Preview (A4 document format) + Pinned Download Buttons
 */
export default function App() {
  // ── State ────────────────────────────────────────────────
  const [file, setFile] = useState(null);
  const [examType, setExamType] = useState('CIE_I');
  const [paper, setPaper] = useState(null);
  const [paperId, setPaperId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(null);
  const [toast, setToast] = useState(null);
  const [status, setStatus] = useState('');

  // Cache the file_id so regenerate reuses the uploaded document
  const fileIdRef = useRef(null);

  /** Show a toast notification that auto-dismisses */
  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  }, []);

  /** Handle file selection */
  const handleFileChange = useCallback((f) => {
    setFile(f);
    setPaper(null);
    setPaperId(null);
    fileIdRef.current = null;
    setStatus('');
    showToast('success', `"${f.name}" selected successfully!`);
  }, [showToast]);

  /** Upload the file to backend and return file_id */
  const uploadFile = useCallback(async () => {
    const formData = new FormData();
    formData.append('file', file);
    setStatus('Uploading document…');

    const uploadRes = await axios.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    fileIdRef.current = uploadRes.data.file_id;
    return uploadRes.data.file_id;
  }, [file]);

  /** Core generation logic (shared by generate and regenerate) */
  const doGenerate = useCallback(async (skipUpload = false, isRegenerate = false) => {
    if (!file) return;

    setLoading(true);

    try {
      let fid = fileIdRef.current;
      if (!fid || !skipUpload) {
        fid = await uploadFile();
      }

      setStatus(isRegenerate ? 'Regenerating new paper…' : 'Loading question paper…');
      const generateRes = await axios.post('/api/generate', {
        file_id: fid,
        exam_type: examType,
        regenerate: isRegenerate,
      });

      setPaper(generateRes.data.paper);
      setPaperId(generateRes.data.paper_id);
      setStatus('');
      showToast('success', isRegenerate ? 'New question paper generated!' : 'Question paper ready!');
    } catch (err) {
      const message =
        err.response?.data?.error || err.message || 'Something went wrong.';
      setStatus('');
      showToast('error', message);
    } finally {
      setLoading(false);
    }
  }, [file, examType, uploadFile, showToast]);

  /** Generate — displays cached paper if available, never creates new random paper after initial creation */
  const handleGenerate = useCallback(() => {
    doGenerate(!!fileIdRef.current, false);
  }, [doGenerate]);

  /** Regenerate — the ONLY action that creates a new random selection */
  const handleRegenerate = useCallback(() => {
    doGenerate(true, true);
  }, [doGenerate]);

  /** Download handler (shared for PDF and DOCX) */
  const handleDownload = useCallback(
    async (format) => {
      if (!paperId) return;

      setDownloading(format);
      try {
        const response = await axios.get(`/api/download/${format}/${paperId}`, {
          responseType: 'blob',
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        const formattedExam = (examType || 'CIE_I').replace('_', '-');
        const subCode = paper?.metadata?.su00 || paper?.metadata?.subject_code || 'PAPER';
        const fileName = `${formattedExam}-${subCode}.${format === 'pdf' ? 'pdf' : 'docx'}`;

        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        showToast('success', `${format.toUpperCase()} downloaded!`);
      } catch (err) {
        let message = `Failed to download ${format.toUpperCase()}.`;
        if (err.response?.data instanceof Blob && err.response.data.type.includes('json')) {
          try {
            const text = await err.response.data.text();
            const json = JSON.parse(text);
            if (json.error) message = json.error;
          } catch (e) {
            // fallback
          }
        }
        showToast('error', message);
      } finally {
        setDownloading(null);
      }
    },
    [paperId, showToast]
  );

  return (
    <div className="min-h-screen flex flex-col bg-slate-100">

      {/* ── Toast Notification ─────────────────────────── */}
      {toast && (
        <div
          className={`toast ${toast.type === 'success' ? 'toast-success' : 'toast-error'}`}
          role="alert"
        >
          {toast.message}
        </div>
      )}

      {/* ═══════════ 1. TOP FULL-WIDTH HEADER ═══════════════ */}
      <Header />

      {/* ═══════════ 2. MAIN TWO-PANEL LAYOUT ═══════════════ */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 pb-8 flex flex-col lg:flex-row gap-6">

        {/* ── LEFT PANEL (~40% width) ─────────────────────── */}
        <aside className="w-full lg:w-[40%] lg:max-w-[460px] flex flex-col gap-6">
          <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col gap-6">
            
            {/* Panel Title */}
            <div className="border-b border-gray-100 pb-3">
              <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider">
                Question Paper Controls
              </h2>
              <p className="text-xs text-gray-400 mt-0.5">
                Upload Question Bank and select pattern
              </p>
            </div>

            {/* Upload Section */}
            <UploadSection
              file={file}
              onFileChange={handleFileChange}
              disabled={loading}
            />

            {/* Exam Type Selector */}
            <ExamTypeSelector
              examType={examType}
              onChange={setExamType}
              disabled={loading}
            />

            {/* Generate & Regenerate Action Buttons */}
            <GenerateButton
              onGenerate={handleGenerate}
              onRegenerate={handleRegenerate}
              loading={loading}
              disabled={!file}
              hasGenerated={!!paper}
            />

            {/* Real-time Status Message */}
            {status && (
              <div className="flex items-center gap-2 text-xs font-medium text-blue-600 bg-blue-50 p-3 rounded-lg animate-fade-in border border-blue-100">
                <svg className="animate-spin-slow w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                {status}
              </div>
            )}
          </div>

          {/* Software Info Box */}
          <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-4 text-center">
            <p className="text-xs font-semibold text-gray-700">Jeppiaar Institute of Technology</p>
            <p className="text-[11px] text-gray-400 mt-0.5">Examination Cell Software © {new Date().getFullYear()}</p>
          </div>
        </aside>

        {/* ── RIGHT PANEL (~60% width) ────────────────────── */}
        <main className="flex-1 bg-white rounded-xl shadow-xs border border-gray-200 flex flex-col overflow-hidden min-h-[700px]">
          
          {/* Panel Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
            <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider flex items-center gap-2">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Official Question Paper Preview
            </h2>
            {paper && (
              <span className="text-xs bg-blue-100 text-blue-800 font-semibold px-2.5 py-0.5 rounded-full">
                {paper.metadata?.exam_type || 'Generated'} ({paper.metadata?.max_marks_display || paper.metadata?.max_marks})
              </span>
            )}
          </div>

          {/* Preview Area (Scrollable A4 document container) */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 bg-slate-200">
            {paper ? (
              <div className="animate-fade-in">
                <PreviewSection paper={paper} />
              </div>
            ) : (
              <div className="h-full min-h-[500px] flex flex-col items-center justify-center text-gray-400 text-center p-8">
                <div className="w-16 h-16 rounded-full bg-white shadow-xs flex items-center justify-center mb-4 text-blue-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-base font-bold text-gray-700">No Question Paper Generated Yet</p>
                <p className="text-xs text-gray-500 max-w-sm mt-1">
                  Upload a Question Bank (.docx) on the left panel, select examination pattern, and click <b>Generate Question Paper</b>.
                </p>
              </div>
            )}
          </div>

          {/* Download Buttons Footer */}
          <DownloadButtons
            paperId={paperId}
            onDownloadPdf={() => handleDownload('pdf')}
            onDownloadDocx={() => handleDownload('docx')}
            downloading={downloading}
          />
        </main>

      </div>
    </div>
  );
}