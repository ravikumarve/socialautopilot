'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { exportPosts, exportSchedule, exportAnalytics, type ExportFormat } from '@/lib/api';

type ExportOption = {
  label: string;
  action: () => Promise<void>;
};

function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  // Clean up DOM element and object URL
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

function triggerJsonDownload(data: unknown, filename: string): void {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  triggerBlobDownload(blob, filename);
}

function getTimestampPrefix(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function ExportButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close dropdown on Escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const handleExportPostsCsv = useCallback(async () => {
    const blob = await exportPosts('csv');
    triggerBlobDownload(blob, `social-autopilot-posts-${getTimestampPrefix()}.csv`);
  }, []);

  const handleExportPostsJson = useCallback(async () => {
    const blob = await exportPosts('json');
    triggerBlobDownload(blob, `social-autopilot-posts-${getTimestampPrefix()}.json`);
  }, []);

  const handleExportScheduleCsv = useCallback(async () => {
    const blob = await exportSchedule();
    triggerBlobDownload(blob, `social-autopilot-schedule-${getTimestampPrefix()}.csv`);
  }, []);

  const handleExportAnalyticsJson = useCallback(async () => {
    const data = await exportAnalytics();
    triggerJsonDownload(data, `social-autopilot-analytics-${getTimestampPrefix()}.json`);
  }, []);

  const exportOptions: ExportOption[] = [
    { label: 'Export Posts (CSV)', action: handleExportPostsCsv },
    { label: 'Export Posts (JSON)', action: handleExportPostsJson },
    { label: 'Export Schedule (CSV)', action: handleExportScheduleCsv },
    { label: 'Export Analytics (JSON)', action: handleExportAnalyticsJson },
  ];

  const handleOptionClick = async (option: ExportOption) => {
    setExporting(true);
    setErrorMessage(null);
    setIsOpen(false);

    try {
      await option.action();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Export failed';
      setErrorMessage(message);
      console.error('Export error:', err);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div ref={dropdownRef} className="relative inline-block text-left">
      {/* Main button */}
      <button
        type="button"
        onClick={() => {
          setIsOpen((prev) => !prev);
          setErrorMessage(null);
        }}
        disabled={exporting}
        className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label="Export data"
      >
        {exporting ? (
          <svg
            className="h-4 w-4 animate-spin text-gray-500"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : (
          <svg
            className="h-4 w-4 text-gray-500"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"
            />
          </svg>
        )}
        {exporting ? 'Exporting…' : 'Export'}
        <svg
          className="h-4 w-4 text-gray-400"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div
          className="absolute right-0 z-20 mt-2 w-56 origin-top-right rounded-lg border border-gray-200 bg-white shadow-lg ring-1 ring-black ring-opacity-5"
          role="listbox"
          aria-label="Export options"
        >
          <div className="py-1">
            {exportOptions.map((option) => (
              <button
                key={option.label}
                type="button"
                role="option"
                onClick={() => handleOptionClick(option)}
                className="flex w-full items-center px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-indigo-50 hover:text-indigo-700 focus:outline-none focus:bg-indigo-50 focus:text-indigo-700"
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Inline error message */}
      {errorMessage && (
        <p className="mt-1 text-xs text-red-600" role="alert">
          {errorMessage}
        </p>
      )}
    </div>
  );
}
