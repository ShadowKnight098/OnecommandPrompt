import React from 'react';
import { Terminal, RotateCcw } from 'lucide-react';

export default function Navbar({ onReset, hasProject }) {
  return (
    <header className="border-b border-ink-200 bg-white/95 backdrop-blur-xs sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          className="flex items-center gap-3 cursor-pointer select-none group" 
          onClick={onReset}
        >
          <div className="w-8 h-8 rounded-md bg-ink-950 flex items-center justify-center text-white shadow-paper-sm">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm sm:text-base text-ink-950 tracking-tight font-sans">
                One-Command
              </span>
              <span className="text-[11px] px-1.5 py-0.5 rounded border border-ink-200 bg-ink-100/60 text-ink-700 font-mono font-medium leading-none">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-ink-500 hidden sm:block font-sans">Deterministic Project Installer</p>
          </div>
        </div>

        {/* Workflow Pipeline */}
        <div className="hidden md:flex items-center gap-1.5 text-[11px] font-mono text-ink-500">
          <span className="font-medium text-ink-900">DETECT</span>
          <span className="text-ink-300">→</span>
          <span className="font-medium text-ink-900">VERIFY</span>
          <span className="text-ink-300">→</span>
          <span className="font-medium text-ink-900">PLAN</span>
          <span className="text-ink-300">→</span>
          <span className="font-medium text-ink-900">INSTALL</span>
          <span className="text-ink-300">→</span>
          <span className="font-medium text-ink-900">RUN</span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2.5">
          {hasProject && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 text-xs text-ink-700 hover:text-ink-950 px-3 py-1.5 rounded-md border border-ink-300 bg-white hover:bg-ink-50 shadow-paper-sm transition-colors font-medium font-sans"
              title="Upload another project"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>New Project</span>
            </button>
          )}

          <a
            href="https://github.com/ShadowKnight098"
            target="_blank"
            rel="noreferrer"
            className="p-2 text-ink-500 hover:text-ink-950 hover:bg-ink-100 rounded-md transition-colors"
            title="GitHub Profile"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
