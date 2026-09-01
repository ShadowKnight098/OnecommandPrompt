import React, { useState } from 'react';
import {
  Upload,
  Cpu,
  Terminal,
  Laptop,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  FolderArchive,
  ShieldCheck,
  Code2,
  Copy,
  Check
} from 'lucide-react';

const STEPS = [
  {
    num: "01",
    title: "Upload",
    tag: "Drag & drop",
    desc: "Drop your source code. Datasets and virtual environments are automatically skipped.",
    icon: Upload,
    color: "text-indigo-600",
    bg: "bg-indigo-50",
    border: "border-indigo-200",
    dot: "bg-indigo-500",
    preview: "my-project/\n├── main.py\n└── requirements.txt",
    points: [
      { icon: FolderArchive, text: "Accepts a folder or a .zip" },
      { icon: ShieldCheck, text: "Datasets and .venv folders excluded automatically" }
    ]
  },
  {
    num: "02",
    title: "Auto-detect",
    tag: "AST scanner",
    desc: "A static AST parser identifies required packages, the entry point file, and security status in under half a second.",
    icon: Cpu,
    color: "text-emerald-600",
    bg: "bg-emerald-50",
    border: "border-emerald-200",
    dot: "bg-emerald-500",
    preview: "✓ Python >= 3.10\n✓ Entry: main.py\n✓ 4 dependencies",
    points: [
      { icon: ShieldCheck, text: "Runs locally — code never leaves the scanner" },
      { icon: CheckCircle2, text: "Flags missing or conflicting packages" }
    ]
  },
  {
    num: "03",
    title: "One command",
    tag: "PowerShell & bash",
    desc: "Generates a deterministic script that installs Python, builds a .venv, and pulls down your code.",
    icon: Terminal,
    color: "text-amber-600",
    bg: "bg-amber-50",
    border: "border-amber-200",
    dot: "bg-amber-500",
    preview: "irm https://one-cmd.dev/i/app.ps1 | iex",
    points: [
      { icon: CheckCircle2, text: "Same command works on Windows, macOS, and Linux" },
      { icon: ShieldCheck, text: "Pinned versions, so it runs the same way twice" }
    ]
  },
  {
    num: "04",
    title: "Launch & code",
    tag: "VS Code ready",
    desc: "The target machine runs your app with live output and opens VS Code with the .venv pre-selected.",
    icon: Laptop,
    color: "text-blue-600",
    bg: "bg-blue-50",
    border: "border-blue-200",
    dot: "bg-blue-500",
    preview: "$ cd my-project\n$ code .\n$ python main.py",
    points: [
      { icon: Code2, text: "Interpreter and debugger wired up on open" },
      { icon: CheckCircle2, text: "Streams stdout and stderr as it runs" }
    ]
  }
];

export default function StepsCarousel() {
  const [activeStep, setActiveStep] = useState(0);
  const [copied, setCopied] = useState(false);

  const step = STEPS[activeStep];
  const StepIcon = step.icon;

  const goTo = (idx) => {
    setActiveStep(idx);
    setCopied(false);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(step.preview);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      // clipboard unavailable — fail silently, button just won't confirm
    }
  };

  return (
    <div className="w-full bg-white border border-ink-200 rounded-2xl p-6 sm:p-8 shadow-paper-md space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 pb-4 border-b border-ink-100">
        <div>
          <h2 className="text-xl sm:text-2xl font-extrabold font-sans text-ink-950 tracking-tight">
            How One-Command works
          </h2>
          <p className="text-sm text-ink-500 font-sans mt-1 max-w-md">
            From local Python files to a shareable one-line installer on any machine.
          </p>
        </div>
        <div className="text-xs font-mono text-ink-400 font-semibold whitespace-nowrap">
          Step {activeStep + 1} of {STEPS.length}
        </div>
      </div>

      {/* Progress rail */}
      <div className="relative">
        <div className="absolute top-4 left-0 right-0 h-0.5 bg-ink-100 rounded-full" />
        <div
          className="absolute top-4 left-0 h-0.5 bg-ink-900 rounded-full transition-all duration-300"
          style={{ width: `${(activeStep / (STEPS.length - 1)) * 100}%` }}
        />
        <div className="relative grid grid-cols-4 gap-2">
          {STEPS.map((s, idx) => {
            const Icon = s.icon;
            const isSelected = activeStep === idx;
            const isPast = idx < activeStep;
            return (
              <button
                key={s.num}
                type="button"
                onClick={() => goTo(idx)}
                className="flex flex-col items-center gap-2 group focus:outline-none"
              >
                <span
                  className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all ${
                    isSelected
                      ? `${s.dot} border-transparent text-white scale-110 shadow-paper-xs`
                      : isPast
                      ? 'bg-ink-900 border-transparent text-white'
                      : 'bg-white border-ink-200 text-ink-400 group-hover:border-ink-400'
                  }`}
                >
                  {isPast && !isSelected ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <Icon className="w-4 h-4" />
                  )}
                </span>
                <span
                  className={`text-xs font-sans font-semibold hidden sm:block ${
                    isSelected ? 'text-ink-950' : 'text-ink-400'
                  }`}
                >
                  {s.title}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Active step detail */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 pt-2">
        {/* Left: description + checklist */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${step.bg} ${step.color}`}>
              <StepIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-mono font-semibold text-ink-400">{step.num} · {step.tag}</div>
              <h3 className="text-lg font-bold font-sans text-ink-950">{step.title}</h3>
            </div>
          </div>

          <p className="text-sm text-ink-600 font-sans leading-relaxed">
            {step.desc}
          </p>

          <ul className="space-y-2">
            {step.points.map((p, i) => {
              const PIcon = p.icon;
              return (
                <li key={i} className="flex items-start gap-2 text-sm text-ink-700 font-sans">
                  <PIcon className="w-4 h-4 mt-0.5 text-ink-400 flex-shrink-0" />
                  <span>{p.text}</span>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Right: terminal-style preview */}
        <div className="flex flex-col">
          <div className="rounded-xl overflow-hidden border border-ink-800 shadow-paper-sm flex-1">
            <div className="flex items-center justify-between px-3 py-2 bg-ink-900">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-400/80" />
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400/80" />
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/80" />
              </div>
              <button
                type="button"
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-[11px] font-mono text-ink-300 hover:text-white transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="p-4 bg-ink-950 min-h-[120px] flex items-center">
              <pre className="font-mono text-[13px] leading-relaxed text-emerald-300 whitespace-pre-wrap break-words">
                {step.preview}
              </pre>
            </div>
          </div>

          {/* Prev / Next */}
          <div className="flex items-center justify-between mt-3">
            <button
              type="button"
              disabled={activeStep === 0}
              onClick={() => goTo(Math.max(0, activeStep - 1))}
              className="flex items-center gap-1.5 text-xs font-sans font-semibold text-ink-500 hover:text-ink-900 disabled:opacity-30 disabled:hover:text-ink-500 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back
            </button>
            <button
              type="button"
              disabled={activeStep === STEPS.length - 1}
              onClick={() => goTo(Math.min(STEPS.length - 1, activeStep + 1))}
              className="flex items-center gap-1.5 text-xs font-sans font-semibold text-ink-900 hover:text-ink-600 disabled:opacity-30 disabled:hover:text-ink-900 transition-colors"
            >
              {activeStep === STEPS.length - 1 ? 'Done' : 'Next step'}
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}