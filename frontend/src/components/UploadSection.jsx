import { useRef, useState, useCallback } from 'react';

/**
 * UploadSection Component
 * 
 * Compact drag-and-drop file upload area for the left panel.
 * Accepts only .docx files with validation.
 * 
 * Props:
 *   file        — currently selected File object (or null)
 *   onFileChange — callback(File) when a valid file is selected
 *   disabled    — disables interaction when generating
 */
export default function UploadSection({ file, onFileChange, disabled }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState('');

  const handleFile = useCallback(
    (f) => {
      setError('');
      if (!f) return;
      if (!f.name.toLowerCase().endsWith('.docx')) {
        setError('Only .docx files are accepted.');
        return;
      }
      if (f.size > 10 * 1024 * 1024) {
        setError('File size must be under 10 MB.');
        return;
      }
      onFileChange(f);
    },
    [onFileChange]
  );

  const onDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      handleFile(e.dataTransfer.files?.[0]);
    },
    [handleFile, disabled]
  );

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div>
      <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
        Upload Question Bank
      </label>

      <div
        className={`drop-zone p-5 text-center ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''} ${disabled ? 'opacity-50 pointer-events-none' : ''}`}
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !disabled && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        id="upload-dropzone"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".docx"
          onChange={(e) => { handleFile(e.target.files?.[0]); e.target.value = ''; }}
          className="hidden"
          id="file-input"
        />

        {file ? (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-green-100 flex items-center justify-center shrink-0">
              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="text-left min-w-0">
              <p className="font-semibold text-sm text-green-800 truncate">{file.name}</p>
              <p className="text-xs text-gray-400">{formatSize(file.size)} · Click to replace</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <svg className="w-8 h-8 text-primary-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <div>
              <p className="text-sm font-medium text-gray-600">Drop .docx file here</p>
              <p className="text-xs text-gray-400">or click to browse</p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <p className="mt-1.5 text-xs text-red-600 flex items-center gap-1" role="alert">
          <svg className="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
