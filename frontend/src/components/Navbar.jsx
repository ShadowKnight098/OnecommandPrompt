import React, { useState } from 'react';
import { Terminal, RotateCcw, User, LogOut, Shield, ChevronDown, Globe, Layers } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ onReset, hasProject, currentPage = 'home', onNavigate }) {
  const { user, openAuthModal, signOut } = useAuth();
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  return (
    <header className="border-b border-ink-200 bg-white/95 backdrop-blur-xs sticky top-0 z-50 transition-all duration-200">
      <div className="max-w-5xl mx-auto px-3 sm:px-6 h-14 sm:h-16 flex items-center justify-between gap-2">
        {/* Brand */}
        <div 
          className="flex items-center gap-2 sm:gap-3 cursor-pointer select-none group shrink-0" 
          onClick={onReset}
        >
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-md bg-ink-950 flex items-center justify-center text-white shadow-paper-sm transition-transform duration-200 group-hover:scale-105">
            <Terminal className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          </div>
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-xs sm:text-base text-ink-950 tracking-tight font-sans">
              One-Command
            </span>
            <span className="text-[10px] px-1 py-0.2 rounded border border-ink-200 bg-ink-100/60 text-ink-700 font-mono font-medium leading-none hidden xs:inline">
              v2.0
            </span>
          </div>
        </div>

        {/* Central Navigation: Packager & Global Place */}
        <div className="flex items-center p-0.5 sm:p-1 bg-slate-100 rounded-lg sm:rounded-xl border border-slate-200 text-xs font-sans">
          <button
            onClick={() => onNavigate && onNavigate('home')}
            className={`flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-md sm:rounded-lg font-medium transition-all cursor-pointer text-[11px] sm:text-xs ${
              currentPage === 'home'
                ? 'bg-white text-slate-900 shadow-sm font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Layers className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
            <span>Packager</span>
          </button>

          <button
            onClick={() => onNavigate && onNavigate('global')}
            className={`flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-md sm:rounded-lg font-medium transition-all cursor-pointer text-[11px] sm:text-xs ${
              currentPage === 'global'
                ? 'bg-white text-slate-900 shadow-sm font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Globe className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-emerald-600" />
            <span>Global Place</span>
          </button>
        </div>

        {/* Actions & Auth */}
        <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
          {hasProject && currentPage === 'home' && (
            <button
              onClick={onReset}
              className="hidden md:flex items-center gap-1.5 text-xs text-ink-700 hover:text-ink-950 px-2.5 py-1.5 rounded-md border border-ink-300 bg-white hover:bg-ink-50 shadow-paper-sm transition-all font-medium font-sans active:scale-[0.97]"
              title="Upload another project"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>New</span>
            </button>
          )}

          {/* User Auth state */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-1 sm:gap-1.5 text-xs text-ink-800 bg-ink-100/70 hover:bg-ink-100 px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-md border border-ink-200 font-medium transition-all cursor-pointer select-none"
              >
                <div className="w-4 h-4 rounded-full bg-slate-900 text-emerald-400 flex items-center justify-center text-[9px] font-bold">
                  {user.email ? user.email.charAt(0).toUpperCase() : 'U'}
                </div>
                <span className="max-w-[70px] sm:max-w-[100px] truncate font-mono text-[10px] sm:text-[11px] hidden xs:inline">
                  {user.email?.split('@')[0]}
                </span>
                <ChevronDown className="w-3 h-3 text-ink-500" />
              </button>

              {userDropdownOpen && (
                <div 
                  className="absolute right-0 mt-1.5 w-48 bg-white border border-slate-200 rounded-xl shadow-lg p-1.5 z-50 animate-scale-in text-xs font-sans"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="px-3 py-2 border-b border-slate-100">
                    <p className="font-semibold text-slate-900 truncate">{user.email}</p>
                    <p className="text-[10px] text-emerald-600 font-medium flex items-center gap-1 mt-0.5">
                      <Shield className="w-3 h-3" /> Private Auth Active
                    </p>
                  </div>

                  <button
                    onClick={() => { signOut(); setUserDropdownOpen(false); }}
                    className="w-full mt-1 flex items-center gap-2 px-3 py-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer text-left"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={openAuthModal}
              className="flex items-center gap-1 sm:gap-1.5 text-[11px] sm:text-xs font-medium font-sans text-ink-800 hover:text-ink-950 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-md border border-ink-300 bg-white hover:bg-ink-50 shadow-paper-sm transition-all duration-150 active:scale-[0.97] cursor-pointer"
            >
              <User className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-ink-500" />
              <span>Sign In</span>
            </button>
          )}

          <a
            href="https://github.com/ShadowKnight098"
            target="_blank"
            rel="noreferrer"
            className="p-1.5 sm:p-2 text-ink-500 hover:text-ink-950 hover:bg-ink-100 rounded-md transition-colors"
            title="GitHub Profile"
          >
            <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
