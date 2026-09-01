import React, { useState } from 'react';
import { 
  Copy, 
  Check, 
  Terminal, 
  ChevronDown, 
  ChevronUp, 
  Eye, 
  X, 
  CheckCircle2, 
  ShieldCheck, 
  HelpCircle,
  Share2,
  ExternalLink,
  Send,
  Globe,
  Code2
} from 'lucide-react';
import { fetchScriptContent } from '../api/client';

export default function CommandOutput({
  projectId,
  commands,
  plan,
  onReset
}) {
  const [activePlatform, setActivePlatform] = useState('windows');
  const [copied, setCopied] = useState(false);
  const [isAccordionOpen, setIsAccordionOpen] = useState(true);
  const [scriptModalOpen, setScriptModalOpen] = useState(false);
  const [scriptContent, setScriptContent] = useState('');
  const [isLoadingScript, setIsLoadingScript] = useState(false);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);
  const [markdownCopied, setMarkdownCopied] = useState(false);

  const activeCommand = commands ? commands[activePlatform] : '';
  const shareUrl = typeof window !== 'undefined' ? `${window.location.origin}/?p=${projectId}` : '';

  const handleCopy = () => {
    if (!activeCommand) return;
    navigator.clipboard.writeText(activeCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleViewScript = async () => {
    setIsLoadingScript(true);
    setScriptModalOpen(true);
    try {
      const ext = activePlatform === 'windows' ? 'ps1' : 'sh';
      const url = `/i/${projectId}.${ext}`;
      const content = await fetchScriptContent(url);
      setScriptContent(content);
    } catch (err) {
      setScriptContent('# Error loading installer script: ' + err.message);
    } finally {
      setIsLoadingScript(false);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${plan?.project_name || 'Project'} - One-Command Installer`,
          text: `Install and run ${plan?.project_name || 'this Python project'} with a single command:\n${activeCommand}`,
          url: shareUrl,
        });
        return;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.log('Native share failed, opening modal');
        }
      }
    }
    setShareModalOpen(true);
  };

  const handleCopyShareLink = () => {
    navigator.clipboard.writeText(shareUrl);
    setLinkCopied(true);
    setTimeout(() => setLinkCopied(false), 2500);
  };

  const markdownSnippet = `### Quick Install: ${plan?.project_name || 'Python Project'}

Run this single command on **${activePlatform === 'windows' ? 'Windows PowerShell' : 'Linux / macOS'}**:

\`\`\`${activePlatform === 'windows' ? 'powershell' : 'bash'}
${activeCommand}
\`\`\`

[![One-Command Installer](https://img.shields.io/badge/Install_with-One--Command-22c55e?style=flat&logo=terminal)](${shareUrl})
`;

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(markdownSnippet);
    setMarkdownCopied(true);
    setTimeout(() => setMarkdownCopied(false), 2500);
  };

  const explanationSteps = [
    {
      num: 1,
      title: "Detect Python Runtime",
      detail: `Inspects target computer for an existing compatible Python (${plan?.runtime?.version || '>=3.10'}). Reuses it immediately with zero downloads.`,
    },
    {
      num: 2,
      title: "Verify or Install",
      detail: "If compatible Python is missing, automatically installs Python via winget (Windows) or package manager (Linux/macOS).",
    },
    {
      num: 3,
      title: "Download & Sync Project Files",
      detail: "Performs non-destructive overlay extraction. If project already exists, updates code in-place while 100% preserving .env, databases, local datasets, and custom files.",
    },
    {
      num: 4,
      title: "Virtual Environment (.venv)",
      detail: "Checks for existing .venv. Reuses existing environment on updates with zero reinstall, or initializes a clean one on first run.",
    },
    {
      num: 5,
      title: "Sync Dependencies",
      detail: `Incrementally verifies and synchronizes ${plan?.dependencies?.length || 0} package(s) inside .venv without re-downloading existing packages.`,
    },
    {
      num: 6,
      title: "Validate Files",
      detail: `Ensures entry point (${plan?.entrypoint?.entry_file || 'main.py'}) and configuration exist and are intact.`,
    },
    {
      num: 7,
      title: "Launch Application",
      detail: "Executes the application with clean output and startup logs.",
    },
  ];

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">
      {/* Main Command Card */}
      <div className="bg-white border border-ink-200 rounded-xl p-6 sm:p-8 shadow-paper-md">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-ink-200">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center justify-center shadow-paper-sm">
              <CheckCircle2 className="w-5 h-5 text-emerald-700" />
            </div>
            <div>
              <h2 className="text-xl font-bold font-sans text-ink-950 tracking-tight">Your installer is ready</h2>
              <p className="text-xs text-ink-500 font-sans">Run this single command on the target computer (supports fresh installs & in-place updates).</p>
            </div>
          </div>

          <div className="flex flex-wrap sm:flex-nowrap items-center gap-2 w-full sm:w-auto">
            <button
              onClick={handleShare}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 text-xs text-indigo-800 hover:text-indigo-950 px-3.5 py-2.5 sm:py-2 rounded-lg bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 font-semibold font-sans transition-colors shadow-paper-sm active:scale-95"
            >
              <Share2 className="w-4 h-4 text-indigo-600" />
              <span>Share Installer</span>
            </button>

            <button
              onClick={handleViewScript}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 text-xs text-ink-700 hover:text-ink-950 px-3.5 py-2.5 sm:py-2 rounded-lg bg-ink-50 hover:bg-ink-100 border border-ink-300 font-medium font-sans transition-colors active:scale-95"
            >
              <Eye className="w-4 h-4 text-ink-600" />
              <span>Inspect Script</span>
            </button>
          </div>
        </div>

        {/* Platform Selector Tabs */}
        <div className="flex items-center gap-2 mt-6 p-1 rounded-lg bg-ink-100 border border-ink-200 w-fit">
          <button
            onClick={() => setActivePlatform('windows')}
            className={`px-3.5 py-1.5 rounded-md text-xs font-semibold font-sans transition-all ${
              activePlatform === 'windows'
                ? 'bg-white text-ink-950 shadow-paper-sm'
                : 'text-ink-600 hover:text-ink-950'
            }`}
          >
            Windows (PowerShell)
          </button>

          <button
            onClick={() => setActivePlatform('unix')}
            className={`px-3.5 py-1.5 rounded-md text-xs font-semibold font-sans transition-all ${
              activePlatform === 'unix'
                ? 'bg-white text-ink-950 shadow-paper-sm'
                : 'text-ink-600 hover:text-ink-950'
            }`}
          >
            Linux / macOS (Bash)
          </button>
        </div>

        {/* Authentic Terminal Box */}
        <div className="mt-4 rounded-xl border border-ink-800 bg-ink-950 overflow-hidden shadow-paper-md">
          {/* Terminal Window Top Bar */}
          <div className="px-4 py-2.5 bg-ink-900 border-b border-ink-800 flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
              <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
            </div>
            <span className="text-[11px] font-mono text-ink-400 font-medium">
              {activePlatform === 'windows' ? 'powershell.exe' : 'bash'}
            </span>
            <div className="w-10" />
          </div>

          {/* Terminal Code Command */}
          <div className="p-4 sm:p-5 font-mono text-xs sm:text-sm text-ink-100 overflow-x-auto select-all leading-relaxed">
            <div className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold select-none">
                {activePlatform === 'windows' ? 'PS >' : '$'}
              </span>
              <code>{activeCommand}</code>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="mt-5 flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          <span className="text-xs text-ink-500 font-sans flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-700" />
            <span>Deterministic • Safe In-Place Updates • Isolated in .venv</span>
          </span>

          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            <button
              onClick={handleShare}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium font-sans text-sm bg-white hover:bg-ink-50 text-ink-800 border border-ink-300 transition-all shadow-paper-sm"
            >
              <Share2 className="w-4 h-4 text-ink-600" />
              <span>Share</span>
            </button>

            <button
              onClick={handleCopy}
              className={`w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg font-medium font-sans text-sm transition-all shadow-paper-sm ${
                copied
                  ? 'bg-emerald-700 text-white'
                  : 'bg-ink-950 hover:bg-ink-900 text-white'
              }`}
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Copied Command!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy Command</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Step-by-Step Terminal Tutorial / Quickstart */}
      <div className="bg-white border border-ink-200 rounded-xl p-6 sm:p-8 shadow-paper-md space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-ink-200">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-800 flex items-center justify-center">
            <Terminal className="w-5 h-5 text-indigo-700" />
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-bold font-sans text-ink-950">Quickstart Tutorial & Execution Guide</h3>
            <p className="text-xs text-ink-500 font-sans">Follow these 3 terminal steps to install and open the project.</p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Step 1: Open Terminal & Prepare Workspace */}
          <div className="p-4 sm:p-5 rounded-xl bg-ink-50/70 border border-ink-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-full bg-ink-950 text-white font-mono font-bold text-xs flex items-center justify-center">1</span>
                <h4 className="text-sm font-bold font-sans text-ink-950">
                  {activePlatform === 'windows' ? 'Open PowerShell & Create Workspace' : 'Open Terminal & Create Workspace'}
                </h4>
              </div>
              <span className="text-[11px] font-mono text-ink-500 font-medium px-2 py-0.5 bg-ink-100 rounded">
                {activePlatform === 'windows' ? 'powershell' : 'bash'}
              </span>
            </div>
            <p className="text-xs text-ink-600 font-sans leading-relaxed">
              Open your terminal and choose or create a clean directory where you want this project installed:
            </p>
            <div className="relative group">
              <div className="p-3 bg-ink-950 rounded-lg font-mono text-xs text-ink-100 flex items-center justify-between overflow-x-auto select-all">
                <code>
                  {activePlatform === 'windows'
                    ? `mkdir ${plan?.project_name || 'my-project'}; cd ${plan?.project_name || 'my-project'}`
                    : `mkdir -p ${plan?.project_name || 'my-project'} && cd ${plan?.project_name || 'my-project'}`}
                </code>
                <button
                  onClick={() => {
                    const cmd = activePlatform === 'windows'
                      ? `mkdir ${plan?.project_name || 'my-project'}; cd ${plan?.project_name || 'my-project'}`
                      : `mkdir -p ${plan?.project_name || 'my-project'} && cd ${plan?.project_name || 'my-project'}`;
                    navigator.clipboard.writeText(cmd);
                  }}
                  className="ml-3 shrink-0 p-1.5 rounded bg-ink-800 hover:bg-ink-700 text-ink-300 hover:text-white transition-colors"
                  title="Copy command"
                >
                  <Copy className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Step 2: Run Installer */}
          <div className="p-4 sm:p-5 rounded-xl bg-ink-50/70 border border-ink-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-full bg-indigo-600 text-white font-mono font-bold text-xs flex items-center justify-center">2</span>
                <h4 className="text-sm font-bold font-sans text-ink-950">Run One-Command Bootstrap Script</h4>
              </div>
              <span className="text-[11px] font-mono text-emerald-700 font-semibold px-2 py-0.5 bg-emerald-50 border border-emerald-200 rounded">
                Auto-installs Python + .venv + dependencies
              </span>
            </div>
            <p className="text-xs text-ink-600 font-sans leading-relaxed">
              Paste and run the installer command. It will check Python, build the isolated virtual environment, and install all required packages:
            </p>
            <div className="relative group">
              <div className="p-3 bg-ink-950 rounded-lg font-mono text-xs text-ink-100 flex items-center justify-between overflow-x-auto select-all">
                <code className="text-emerald-300">{activeCommand}</code>
                <button
                  onClick={handleCopy}
                  className="ml-3 shrink-0 p-1.5 rounded bg-ink-800 hover:bg-ink-700 text-ink-300 hover:text-white transition-colors"
                  title="Copy command"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
          </div>

          {/* Step 3: Open in VS Code & Start Developing */}
          <div className="p-4 sm:p-5 rounded-xl bg-ink-50/70 border border-ink-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-full bg-ink-950 text-white font-mono font-bold text-xs flex items-center justify-center">3</span>
                <h4 className="text-sm font-bold font-sans text-ink-950">Open in VS Code & Develop</h4>
              </div>
              <span className="text-[11px] font-mono text-ink-500 font-medium px-2 py-0.5 bg-ink-100 rounded">
                code .
              </span>
            </div>
            <p className="text-xs text-ink-600 font-sans leading-relaxed">
              Once installation completes, navigate into the project directory and open it directly in Visual Studio Code:
            </p>
            <div className="relative group">
              <div className="p-3 bg-ink-950 rounded-lg font-mono text-xs text-ink-100 flex items-center justify-between overflow-x-auto select-all">
                <code>
                  {activePlatform === 'windows'
                    ? `cd ${plan?.project_name || 'project'}; code .`
                    : `cd ${plan?.project_name || 'project'} && code .`}
                </code>
                <button
                  onClick={() => {
                    const cmd = activePlatform === 'windows'
                      ? `cd ${plan?.project_name || 'project'}; code .`
                      : `cd ${plan?.project_name || 'project'} && code .`;
                    navigator.clipboard.writeText(cmd);
                  }}
                  className="ml-3 shrink-0 p-1.5 rounded bg-ink-800 hover:bg-ink-700 text-ink-300 hover:text-white transition-colors"
                  title="Copy command"
                >
                  <Copy className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Step 4: Re-running in the Future */}
          <div className="p-4 sm:p-5 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-full bg-emerald-700 text-white font-mono font-bold text-xs flex items-center justify-center">4</span>
                <h4 className="text-sm font-bold font-sans text-emerald-950">How to re-run the app later</h4>
              </div>
              <span className="text-[11px] font-mono text-emerald-800 font-semibold px-2 py-0.5 bg-emerald-100 rounded">
                virtualenv runner
              </span>
            </div>
            <p className="text-xs text-emerald-900 font-sans leading-relaxed">
              To run the application again anytime in the future using the created virtual environment:
            </p>
            <div className="p-3 bg-ink-950 rounded-lg font-mono text-xs text-ink-100 flex items-center justify-between overflow-x-auto select-all">
              <code>
                {activePlatform === 'windows'
                  ? `.\\.venv\\Scripts\\python.exe ${plan?.entrypoint?.entry_file || 'main.py'}`
                  : `./.venv/bin/python ${plan?.entrypoint?.entry_file || 'main.py'}`}
              </code>
              <button
                onClick={() => {
                  const cmd = activePlatform === 'windows'
                    ? `.\\.venv\\Scripts\\python.exe ${plan?.entrypoint?.entry_file || 'main.py'}`
                    : `./.venv/bin/python ${plan?.entrypoint?.entry_file || 'main.py'}`;
                  navigator.clipboard.writeText(cmd);
                }}
                className="ml-3 shrink-0 p-1.5 rounded bg-ink-800 hover:bg-ink-700 text-ink-300 hover:text-white transition-colors"
                title="Copy command"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Expandable "What will this command do?" Drawer */}
      <div className="bg-white border border-ink-200 rounded-xl p-6 shadow-paper">
        <button
          onClick={() => setIsAccordionOpen(!isAccordionOpen)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-md bg-ink-100 text-ink-900 flex items-center justify-center">
              <HelpCircle className="w-3.5 h-3.5" />
            </div>
            <h3 className="font-bold font-sans text-ink-950 text-sm sm:text-base">What will this command do?</h3>
          </div>
          <div className="p-1 rounded-md bg-ink-100 text-ink-600">
            {isAccordionOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {isAccordionOpen && (
          <div className="mt-5 space-y-2.5 pt-4 border-t border-ink-200">
            {explanationSteps.map((step) => (
              <div
                key={step.num}
                className="flex items-start gap-3 p-3 rounded-lg bg-ink-50/60 border border-ink-200"
              >
                <div className="w-5 h-5 rounded-md bg-ink-950 text-white flex items-center justify-center font-mono font-bold text-[11px] shrink-0 mt-0.5">
                  {step.num}
                </div>
                <div>
                  <h4 className="text-xs font-bold font-sans text-ink-950">{step.title}</h4>
                  <p className="text-xs text-ink-600 font-sans mt-0.5 leading-relaxed">{step.detail}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Script Inspector Modal */}
      {scriptModalOpen && (
        <div className="fixed inset-0 z-50 bg-ink-950/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-ink-300 rounded-xl w-full max-w-4xl shadow-paper-lg flex flex-col max-h-[85vh] overflow-hidden">
            <div className="p-4 sm:p-5 border-b border-ink-200 flex items-center justify-between bg-ink-50/50">
              <div className="flex items-center gap-3">
                <Terminal className="w-5 h-5 text-ink-900" />
                <div>
                  <h3 className="font-bold font-sans text-ink-950 text-base">
                    Generated Script ({activePlatform === 'windows' ? 'PowerShell .ps1' : 'Bash .sh'})
                  </h3>
                  <p className="text-xs text-ink-500 font-sans">Full source code executed on the target machine.</p>
                </div>
              </div>
              <button
                onClick={() => setScriptModalOpen(false)}
                className="p-1.5 text-ink-400 hover:text-ink-800 hover:bg-ink-100 rounded-md transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 overflow-auto flex-1 bg-ink-950 font-mono text-xs text-ink-100 leading-relaxed whitespace-pre">
              {isLoadingScript ? (
                <div className="text-center py-12 text-ink-400 font-sans">Loading script...</div>
              ) : (
                scriptContent
              )}
            </div>

            <div className="p-4 border-t border-ink-200 bg-ink-50/50 flex items-center justify-between">
              <span className="text-xs text-ink-500 font-sans">Deterministic bootstrap installer</span>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(scriptContent);
                  alert('Script copied to clipboard!');
                }}
                className="px-4 py-2 bg-ink-950 hover:bg-ink-900 text-white rounded-lg text-xs font-medium font-sans flex items-center gap-1.5 shadow-paper-sm transition-colors"
              >
                <Copy className="w-3.5 h-3.5" />
                Copy Raw Script
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Share Modal */}
      {shareModalOpen && (
        <div className="fixed inset-0 z-50 bg-ink-950/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-ink-300 rounded-xl w-full max-w-lg shadow-paper-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="p-4 sm:p-5 border-b border-ink-200 flex items-center justify-between bg-ink-50/50">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center">
                  <Share2 className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold font-sans text-ink-950 text-base">Share One-Command Installer</h3>
                  <p className="text-xs text-ink-500 font-sans">Share this project so anyone can install it with one command.</p>
                </div>
              </div>
              <button
                onClick={() => setShareModalOpen(false)}
                className="p-1.5 text-ink-400 hover:text-ink-800 hover:bg-ink-100 rounded-md transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-5 space-y-5">
              {/* Option 1: Direct Share Link */}
              <div className="space-y-2">
                <label className="text-xs font-bold font-sans text-ink-950 flex items-center justify-between">
                  <span>Direct Web Link</span>
                  {linkCopied && <span className="text-emerald-700 text-[11px] font-semibold">Link Copied!</span>}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={shareUrl}
                    className="flex-1 bg-ink-50 border border-ink-300 rounded-lg px-3 py-2 text-xs font-mono text-ink-900 select-all focus:outline-none"
                  />
                  <button
                    onClick={handleCopyShareLink}
                    className={`px-3.5 py-2 rounded-lg text-xs font-medium font-sans flex items-center gap-1.5 transition-all shrink-0 ${
                      linkCopied
                        ? 'bg-emerald-700 text-white shadow-paper-sm'
                        : 'bg-ink-950 hover:bg-ink-900 text-white shadow-paper-sm'
                    }`}
                  >
                    {linkCopied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{linkCopied ? 'Copied' : 'Copy Link'}</span>
                  </button>
                </div>
              </div>

              {/* Option 2: GitHub README Badge & Markdown */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold font-sans text-ink-950">GitHub README Snippet</label>
                  <button
                    onClick={handleCopyMarkdown}
                    className="text-xs text-indigo-700 hover:text-indigo-900 font-semibold font-sans flex items-center gap-1"
                  >
                    {markdownCopied ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                    <span>{markdownCopied ? 'Copied!' : 'Copy Markdown'}</span>
                  </button>
                </div>
                <div className="p-3 bg-ink-950 rounded-lg font-mono text-[11px] text-ink-300 overflow-x-auto select-all max-h-28 leading-relaxed whitespace-pre">
                  {markdownSnippet}
                </div>
              </div>

              {/* Option 3: Quick Social Links */}
              <div className="space-y-2 pt-2 border-t border-ink-100">
                <label className="text-xs font-medium font-sans text-ink-500">Quick Share</label>
                <div className="grid grid-cols-3 gap-2">
                  <a
                    href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(`Check out ${plan?.project_name || 'this project'} on One-Command Installer! Run it in one step:`)}&url=${encodeURIComponent(shareUrl)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-1.5 p-2 rounded-lg bg-ink-50 hover:bg-ink-100 border border-ink-200 text-xs font-medium font-sans text-ink-800 transition-colors"
                  >
                    <span>Twitter / X</span>
                  </a>

                  <a
                    href={`https://api.whatsapp.com/send?text=${encodeURIComponent(`Install ${plan?.project_name || 'this project'} with One-Command: ${shareUrl}`)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-1.5 p-2 rounded-lg bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 text-xs font-medium font-sans text-emerald-800 transition-colors"
                  >
                    <span>WhatsApp</span>
                  </a>

                  <a
                    href={`mailto:?subject=${encodeURIComponent(`One-Command Installer: ${plan?.project_name || 'Project'}`)}&body=${encodeURIComponent(`Hi,\n\nYou can install and run ${plan?.project_name || 'this project'} in a single command:\n\n${shareUrl}\n\nCommand:\n${activeCommand}`)}`}
                    className="flex items-center justify-center gap-1.5 p-2 rounded-lg bg-ink-50 hover:bg-ink-100 border border-ink-200 text-xs font-medium font-sans text-ink-800 transition-colors"
                  >
                    <span>Email</span>
                  </a>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-ink-200 bg-ink-50/50 flex items-center justify-end">
              <button
                onClick={() => setShareModalOpen(false)}
                className="px-4 py-2 bg-white hover:bg-ink-100 text-ink-800 border border-ink-300 rounded-lg text-xs font-medium font-sans shadow-paper-sm transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
