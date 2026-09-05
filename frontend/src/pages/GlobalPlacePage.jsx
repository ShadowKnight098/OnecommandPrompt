import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { 
  Globe, 
  Search, 
  RefreshCw, 
  Code2, 
  Copy, 
  Check, 
  ArrowRight, 
  Terminal, 
  Package, 
  FolderGit2, 
  Sparkles,
  ExternalLink,
  ChevronRight,
  Layers,
  Cpu
} from 'lucide-react';
import { listProjects } from '../api/client';

const CATEGORIES = [
  { id: 'all', label: 'All Global Packages' },
  { id: 'fastapi', label: 'FastAPI' },
  { id: 'web', label: 'React & Web' },
  { id: 'streamlit', label: 'Streamlit' },
  { id: 'data', label: 'Data & AI' },
  { id: 'cli', label: 'CLI & Tools' }
];

export default function GlobalPlacePage({ onSelectProject, onNavigateHome }) {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [copiedId, setCopiedId] = useState(null);
  const [activePlatform, setActivePlatform] = useState('windows'); // 'windows' | 'unix'

  const fetchGlobalProjects = async () => {
    setIsLoading(true);
    try {
      // Fetch only public / global packages
      const data = await listProjects(50);
      setProjects(data.projects || []);
    } catch (err) {
      console.log('Failed to fetch global projects:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGlobalProjects();
  }, []);

  const handleCopyCommand = (e, project) => {
    e.stopPropagation();
    const cmd = activePlatform === 'windows'
      ? (project.installer_commands?.windows || `irm http://127.0.0.1:8000/i/${project.id}.ps1 -OutFile install.ps1; .\\install.ps1`)
      : (project.installer_commands?.unix || `curl -fsSL http://127.0.0.1:8000/i/${project.id}.sh -o install.sh && bash install.sh`);
    
    navigator.clipboard.writeText(cmd);
    setCopiedId(project.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredProjects = projects.filter(p => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = (
      (p.project_name || '').toLowerCase().includes(q) ||
      (p.description || '').toLowerCase().includes(q) ||
      (p.entry_point_framework || '').toLowerCase().includes(q) ||
      (p.id || '').toLowerCase().includes(q)
    );

    if (!matchesSearch) return false;

    if (selectedCategory === 'all') return true;
    if (selectedCategory === 'fastapi') return (p.entry_point_framework || '').toLowerCase().includes('fastapi');
    if (selectedCategory === 'streamlit') return (p.entry_point_framework || '').toLowerCase().includes('streamlit');
    if (selectedCategory === 'web') return (p.entry_point_framework || '').includes('html') || (p.entry_point_framework || '').includes('react') || (p.entry_point_framework || '').includes('vite');
    if (selectedCategory === 'data') return (
      (p.description || '').toLowerCase().includes('data') ||
      (p.description || '').toLowerCase().includes('ai') ||
      (p.project_name || '').toLowerCase().includes('model')
    );
    if (selectedCategory === 'cli') return !p.entry_point_framework || p.entry_point_framework === 'python';

    return true;
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      <Navbar onReset={onNavigateHome} hasProject={false} />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-8 animate-fade-in">
        {/* Hero Header */}
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 text-white text-xs font-semibold shadow-sm">
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            <span>Global Place</span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Discover and Run Any Community Package.
          </h1>

          <p className="text-slate-600 text-xs sm:text-sm leading-relaxed max-w-xl mx-auto">
            Browse open-source projects published by the community. Copy the one-command installer script and run it natively in your PowerShell or Bash terminal.
          </p>
        </div>

        {/* Toolbar: Platform switcher & Search & Category filters */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 sm:p-6 shadow-paper space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            {/* Platform Selector Tabs */}
            <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200 w-fit text-xs font-medium">
              <button
                onClick={() => setActivePlatform('windows')}
                className={`px-3.5 py-1.5 rounded-lg transition-all cursor-pointer ${
                  activePlatform === 'windows'
                    ? 'bg-white text-slate-900 shadow-sm font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Windows (PowerShell)
              </button>
              <button
                onClick={() => setActivePlatform('unix')}
                className={`px-3.5 py-1.5 rounded-lg transition-all cursor-pointer ${
                  activePlatform === 'unix'
                    ? 'bg-white text-slate-900 shadow-sm font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Linux / macOS (Bash)
              </button>
            </div>

            {/* Search Bar */}
            <div className="flex items-center gap-2">
              <div className="relative flex-1 sm:w-64">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search global packages..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-sans text-slate-900 focus:outline-none focus:border-slate-400 focus:bg-white transition-all"
                />
              </div>

              <button
                onClick={fetchGlobalProjects}
                disabled={isLoading}
                className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-slate-900 transition-all cursor-pointer active:scale-95"
                title="Refresh"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {CATEGORIES.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium font-sans whitespace-nowrap transition-all cursor-pointer active:scale-95 ${
                  selectedCategory === cat.id
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Global Packages Grid */}
        {isLoading ? (
          <div className="py-16 text-center text-xs text-slate-500 font-sans flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-slate-700" />
            <span>Loading Global Place repositories...</span>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-500 font-sans space-y-2 bg-white rounded-2xl border border-slate-200 p-8">
            <FolderGit2 className="w-8 h-8 mx-auto text-slate-400" />
            <p className="font-bold text-sm text-slate-800">No public packages found</p>
            <p className="text-slate-500 max-w-sm mx-auto">
              Be the first to publish an open package! Return to the packager and publish with public visibility.
            </p>
            <button
              onClick={onNavigateHome}
              className="mt-3 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 text-white font-semibold text-xs transition-all active:scale-95 cursor-pointer"
            >
              <span>Package Codebase</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map((proj) => {
              const isCopied = copiedId === proj.id;
              const framework = proj.entry_point_framework || 'python';

              return (
                <div
                  key={proj.id}
                  onClick={() => onSelectProject(proj.id)}
                  className="group p-5 rounded-2xl bg-white hover:bg-slate-50/70 border border-slate-200 hover:border-slate-300 card-hover shadow-paper hover:shadow-paper-md cursor-pointer flex flex-col justify-between space-y-4 transition-all"
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-sm">
                          <Code2 className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div>
                          <h4 className="text-xs font-bold font-sans text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1">
                            {proj.project_name}
                          </h4>
                          <span className="text-[10px] font-mono text-slate-400">
                            id: {proj.id}
                          </span>
                        </div>
                      </div>

                      <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
                        {framework}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 font-sans line-clamp-2 leading-relaxed">
                      {proj.description || "Self-contained package with automated single-command bootstrap installation."}
                    </p>
                  </div>

                  <div className="space-y-3 pt-3 border-t border-slate-100">
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-500">
                      <span>{proj.dependencies_count} dependencies</span>
                      <span>{proj.file_count} files</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => handleCopyCommand(e, proj)}
                        className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold font-sans shadow-sm transition-all active:scale-95"
                      >
                        {isCopied ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Copied Command!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy {activePlatform === 'windows' ? 'PS1' : 'Bash'}</span>
                          </>
                        )}
                      </button>

                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); onSelectProject(proj.id); }}
                        className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
                        title="Inspect Package"
                      >
                        <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 bg-white mt-16">
        <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-slate-600 font-sans">© 2026 One-Command Prompt · Global Place</p>
          <div className="flex items-center gap-3 text-slate-500 font-mono text-[11px]">
            <span>Deterministic Runtime Engine</span>
            <span>•</span>
            <span>Public Open-Source Registry</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
