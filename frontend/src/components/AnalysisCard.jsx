import React from 'react';
import { 
  CheckCircle2, 
  Terminal, 
  Package, 
  FileCode, 
  ShieldAlert, 
  ShieldCheck, 
  ArrowRight, 
  AlertTriangle, 
  SlidersHorizontal,
  FolderGit2
} from 'lucide-react';

export default function AnalysisCard({
  analysis,
  onGenerate,
  onOpenDependencies,
  onOpenEntrypointSelector,
  isGenerating
}) {
  if (!analysis) return null;

  const enabledDepsCount = analysis.dependencies.filter(d => d.enabled).length;
  const isInferred = analysis.dependency_source === 'inferred_imports';
  const hasSecurityWarnings = analysis.security_warnings && analysis.security_warnings.length > 0;

  return (
    <div className="w-full max-w-3xl mx-auto bg-white border border-ink-200 rounded-xl p-6 sm:p-8 shadow-paper-md">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-ink-200">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-lg bg-ink-100 border border-ink-200 text-ink-900 flex items-center justify-center shadow-paper-sm">
            <FolderGit2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-bold font-sans text-ink-950 tracking-tight">{analysis.project_name}</h2>
              <span className="inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-medium font-sans">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                Analysis Complete
              </span>
            </div>
            <p className="text-xs text-ink-500 font-mono mt-0.5">
              ID: {analysis.project_id} • {analysis.file_count} files • {(analysis.total_size_bytes / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={onGenerate}
          disabled={isGenerating}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-ink-950 hover:bg-ink-900 text-white font-medium text-sm shadow-paper-sm transition-colors disabled:opacity-50 font-sans"
        >
          <span>{analysis.is_ambiguous_entrypoint ? 'Confirm & Generate' : 'Generate Installer'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Grid of Analysis Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
        {/* Runtime */}
        <div className="p-4 rounded-lg bg-ink-50/60 border border-ink-200 flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-md bg-white border border-ink-200 text-ink-900 flex items-center justify-center shrink-0 shadow-paper-sm">
            <Terminal className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <p className="text-xs text-ink-500 font-medium font-sans">Python Runtime</p>
            <p className="text-sm font-semibold text-ink-950 font-mono mt-0.5">{analysis.python_requirement}</p>
            <p className="text-xs text-ink-500 mt-1 font-sans">Checked on target machine before setup</p>
          </div>
        </div>

        {/* Entrypoint */}
        <div className="p-4 rounded-lg bg-ink-50/60 border border-ink-200 flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-md bg-white border border-ink-200 text-ink-900 flex items-center justify-center shrink-0 shadow-paper-sm">
            <FileCode className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <p className="text-xs text-ink-500 font-medium font-sans">Application Entry Point</p>
              {analysis.candidate_entry_points.length > 1 && (
                <button
                  onClick={onOpenEntrypointSelector}
                  className="text-xs text-accent-blue hover:text-blue-800 font-medium flex items-center gap-1 font-sans"
                >
                  <SlidersHorizontal className="w-3 h-3" />
                  Change
                </button>
              )}
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <p className="text-sm font-semibold text-ink-950 font-mono">{analysis.entry_point || 'None detected'}</p>
              {analysis.entry_point_framework && (
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-ink-200 text-ink-800 font-semibold">
                  {analysis.entry_point_framework}
                </span>
              )}
            </div>
            {analysis.is_ambiguous_entrypoint && (
              <p className="text-xs text-amber-800 flex items-center gap-1 mt-1 font-medium font-sans">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-700" />
                Multiple candidates detected
              </p>
            )}
          </div>
        </div>

        {/* Dependencies */}
        <div className="p-4 rounded-lg bg-ink-50/60 border border-ink-200 flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-md bg-white border border-ink-200 text-ink-900 flex items-center justify-center shrink-0 shadow-paper-sm">
            <Package className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <p className="text-xs text-ink-500 font-medium font-sans">Dependencies</p>
              <button
                onClick={onOpenDependencies}
                className="text-xs text-accent-blue hover:text-blue-800 font-medium flex items-center gap-1 font-sans"
              >
                <SlidersHorizontal className="w-3 h-3" />
                Review ({enabledDepsCount})
              </button>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <p className="text-sm font-semibold text-ink-950 font-mono">
                {enabledDepsCount} {enabledDepsCount === 1 ? 'package' : 'packages'}
              </p>
              <span className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded font-semibold border ${
                isInferred 
                  ? 'bg-amber-50 text-amber-900 border-amber-200' 
                  : 'bg-emerald-50 text-emerald-900 border-emerald-200'
              }`}>
                {isInferred ? 'AST Inferred' : 'requirements.txt'}
              </span>
            </div>
            <p className="text-xs text-ink-500 mt-1 font-sans">
              {isInferred ? 'Derived from import statements' : 'Explicitly declared dependencies'}
            </p>
          </div>
        </div>

        {/* Security Scan */}
        <div className="p-4 rounded-lg bg-ink-50/60 border border-ink-200 flex items-start gap-3.5">
          <div className={`w-9 h-9 rounded-md flex items-center justify-center shrink-0 border shadow-paper-sm ${
            hasSecurityWarnings 
              ? 'bg-amber-50 border-amber-200 text-amber-700' 
              : 'bg-white border-ink-200 text-emerald-700'
          }`}>
            {hasSecurityWarnings ? <ShieldAlert className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
          </div>
          <div className="flex-1">
            <p className="text-xs text-ink-500 font-medium font-sans">Security & Isolation</p>
            <p className="text-sm font-semibold text-ink-950 font-sans mt-0.5">
              {hasSecurityWarnings ? `${analysis.security_warnings.length} Advisory Notice` : 'Verified Safe'}
            </p>
            <p className="text-xs text-ink-500 mt-1 font-sans">Zip-Slip protected • Isolated in virtualenv</p>
          </div>
        </div>
      </div>

      {/* Warnings Banner if any */}
      {analysis.warnings && analysis.warnings.length > 0 && (
        <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 space-y-2">
          {analysis.warnings.map((warn, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-amber-900 font-sans">
              <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
              <span>{warn}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
