import React, { useState, useEffect } from 'react';
import { 
  FolderGit2, 
  Terminal, 
  Package, 
  ArrowRight, 
  Search, 
  RefreshCw, 
  Code2, 
  Copy, 
  Check, 
  Sparkles,
  Layers,
  ChevronRight
} from 'lucide-react';
import { listProjects } from '../api/client';

const CATEGORIES = [
  { id: 'all', label: 'All Projects' },
  { id: 'fastapi', label: 'FastAPI' },
  { id: 'streamlit', label: 'Streamlit' },
  { id: 'data', label: 'Data & AI' },
  { id: 'cli', label: 'CLI & Scripts' }
];

export default function ProjectShowcase({ onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [copiedId, setCopiedId] = useState(null);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const data = await listProjects(20);
      setProjects(data.projects || []);
    } catch (err) {
      console.log('Failed to fetch showcase projects:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCopyCommand = (e, project) => {
    e.stopPropagation();
    const cmd = project.installer_commands?.windows || `irm http://127.0.0.1:8000/i/${project.id}.ps1 -OutFile install.ps1; .\\install.ps1`;
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
    if (selectedCategory === 'data') return (
      (p.description || '').toLowerCase().includes('data') ||
      (p.description || '').toLowerCase().includes('ai') ||
      (p.project_name || '').toLowerCase().includes('model')
    );
    if (selectedCategory === 'cli') return !p.entry_point_framework || p.entry_point_framework === 'python';

    return true;
  });

  return (
    <div className="w-full bg-white border border-ink-200 rounded-2xl p-6 sm:p-7 shadow-paper space-y-5">
      {/* Header with Title & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-ink-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold font-sans text-ink-950">
              Community Projects & Examples
            </h3>
            <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-ink-100 text-ink-600">
              {projects.length} Available
            </span>
          </div>
          <p className="text-xs text-ink-500 font-sans mt-0.5">
            Click any project to inspect dependencies or copy its 1-click bootstrap installer.
          </p>
        </div>

        {/* Search Bar & Refresh */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-lg bg-ink-50 border border-ink-200 text-xs font-sans text-ink-900 focus:outline-none focus:border-ink-400 focus:bg-white w-44 sm:w-56"
            />
          </div>

          <button
            onClick={fetchProjects}
            disabled={isLoading}
            className="p-1.5 rounded-lg bg-ink-50 hover:bg-ink-100 border border-ink-200 text-ink-600 hover:text-ink-950 transition-colors cursor-pointer"
            title="Refresh"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-3 py-1 rounded-lg text-xs font-medium font-sans whitespace-nowrap transition-colors cursor-pointer ${
              selectedCategory === cat.id
                ? 'bg-ink-950 text-white'
                : 'bg-ink-50 hover:bg-ink-100 text-ink-600 hover:text-ink-900 border border-ink-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Project Cards Grid */}
      {isLoading ? (
        <div className="py-12 text-center text-xs text-ink-400 font-sans flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-ink-500" />
          <span>Loading project library...</span>
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="py-12 text-center text-xs text-ink-500 font-sans space-y-1">
          <FolderGit2 className="w-6 h-6 mx-auto text-ink-400" />
          <p className="font-semibold text-ink-800">No matching projects found</p>
          <p className="text-ink-400">Upload a project above to publish the first one!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {filteredProjects.map((proj) => {
            const isCopied = copiedId === proj.id;

            return (
              <div
                key={proj.id}
                onClick={() => onSelectProject(proj.id)}
                className="group p-4 rounded-xl bg-ink-50/50 hover:bg-white border border-ink-200 hover:border-ink-300 transition-all shadow-paper-xs hover:shadow-paper-sm cursor-pointer flex flex-col justify-between space-y-3"
              >
                <div className="space-y-1.5">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-md bg-white border border-ink-200 flex items-center justify-center text-ink-900 shrink-0">
                        <Code2 className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold font-sans text-ink-950 group-hover:text-indigo-600 transition-colors line-clamp-1">
                          {proj.project_name}
                        </h4>
                        <span className="text-[10px] font-mono text-ink-400">
                          {proj.entry_point || 'main.py'} • {proj.python_requirement}
                        </span>
                      </div>
                    </div>

                    {proj.entry_point_framework && proj.entry_point_framework !== 'python' && (
                      <span className="text-[10px] font-mono uppercase font-semibold px-2 py-0.5 rounded bg-indigo-50 border border-indigo-200 text-indigo-700 shrink-0">
                        {proj.entry_point_framework}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-ink-600 font-sans line-clamp-2 leading-relaxed">
                    {proj.description || "Self-contained Python application ready for single-command bootstrap installation."}
                  </p>
                </div>

                {/* Footer Actions */}
                <div className="pt-2 border-t border-ink-200/80 flex items-center justify-between gap-2">
                  <span className="text-[11px] font-mono text-ink-500">
                    {proj.dependencies_count} packages
                  </span>

                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={(e) => handleCopyCommand(e, proj)}
                      className="px-2.5 py-1 rounded-md bg-white hover:bg-ink-100 border border-ink-200 text-ink-700 text-[11px] font-medium font-sans flex items-center gap-1 transition-colors"
                      title="Copy PowerShell command"
                    >
                      {isCopied ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-600" />
                          <span className="text-emerald-700 font-semibold">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Command</span>
                        </>
                      )}
                    </button>

                    <span className="inline-flex items-center text-xs font-semibold text-ink-900 group-hover:text-indigo-600 font-sans">
                      Open <ChevronRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
