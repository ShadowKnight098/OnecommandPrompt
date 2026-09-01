import React, { useState } from 'react';
import { X, Check, FileCode, CheckCircle2, Code2 } from 'lucide-react';

export default function EntrypointSelector({
  candidates,
  currentEntrypoint,
  onSelect,
  onClose
}) {
  const [selected, setSelected] = useState(currentEntrypoint || (candidates[0]?.file_path || ''));

  const handleConfirm = () => {
    onSelect(selected);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink-950/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-ink-300 rounded-xl w-full max-w-xl shadow-paper-lg overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-ink-200 flex items-center justify-between bg-ink-50/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-white border border-ink-200 text-ink-900 flex items-center justify-center shadow-paper-sm">
              <FileCode className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold font-sans text-ink-950 tracking-tight">Select Application Entry Point</h3>
              <p className="text-xs text-ink-500 font-sans">Choose the file that starts your Python application.</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-ink-400 hover:text-ink-800 hover:bg-ink-100 rounded-md transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Candidate options */}
        <div className="p-5 overflow-y-auto flex-1 space-y-3">
          {candidates.map((cand) => {
            const isSelected = selected === cand.file_path;

            return (
              <div
                key={cand.file_path}
                onClick={() => setSelected(cand.file_path)}
                className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-ink-50 border-ink-950 shadow-paper-sm'
                    : 'bg-white border-ink-200 hover:border-ink-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                      isSelected ? 'border-ink-950 bg-ink-950 text-white' : 'border-ink-400 bg-white'
                    }`}>
                      {isSelected && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                    </div>
                    <span className="font-mono font-bold text-ink-950 text-sm">{cand.file_path}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    {cand.has_main_block && (
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold">
                        __main__ block
                      </span>
                    )}
                    {cand.framework && (
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-ink-100 text-ink-800 font-semibold border border-ink-200">
                        {cand.framework}
                      </span>
                    )}
                  </div>
                </div>

                {/* Code Preview snippet */}
                {cand.preview_lines && cand.preview_lines.length > 0 && (
                  <div className="mt-2.5 p-3 rounded-md bg-ink-950 text-ink-200 overflow-x-auto text-[11px] font-mono leading-relaxed shadow-inner">
                    <div className="flex items-center gap-1.5 text-ink-400 text-[10px] mb-1.5 pb-1 border-b border-ink-800">
                      <Code2 className="w-3 h-3" />
                      <span>Code Preview</span>
                    </div>
                    {cand.preview_lines.map((line, idx) => (
                      <div key={idx} className="whitespace-pre">
                        <span className="text-ink-600 select-none mr-2">{idx + 1}</span>
                        <span>{line}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-ink-200 bg-ink-50/50 flex items-center justify-end gap-2.5">
          <button
            onClick={onClose}
            className="px-3.5 py-2 text-xs font-medium font-sans text-ink-600 hover:text-ink-900 rounded-md transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="px-5 py-2 bg-ink-950 hover:bg-ink-900 text-white rounded-lg text-xs font-medium font-sans flex items-center gap-1.5 shadow-paper-sm transition-colors"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            Confirm Selection
          </button>
        </div>
      </div>
    </div>
  );
}
