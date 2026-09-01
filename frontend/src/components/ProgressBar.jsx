import React from 'react';
import { Check, Loader2 } from 'lucide-react';

export default function ProgressBar({ currentStep = 1, statusText = "Analyzing project..." }) {
  const steps = [
    { id: 1, label: "Archive Extraction", detail: "Zip-Slip & integrity inspection" },
    { id: 2, label: "Python Runtime", detail: "Configuration & version requirements" },
    { id: 3, label: "Dependency Analysis", detail: "AST imports & package translation" },
    { id: 4, label: "Entry Point Scanner", detail: "Frameworks & __main__ blocks" },
  ];

  return (
    <div className="w-full max-w-2xl mx-auto my-8 p-6 sm:p-8 rounded-xl bg-white border border-ink-200 shadow-paper-md">
      <div className="flex items-center justify-between pb-5 mb-5 border-b border-ink-200">
        <div className="flex items-center gap-3">
          <Loader2 className="w-4 h-4 text-ink-950 animate-spin" />
          <h3 className="font-bold text-ink-950 font-sans text-base tracking-tight">{statusText}</h3>
        </div>
        <span className="text-xs font-mono text-ink-700 bg-ink-100 px-2.5 py-1 rounded border border-ink-200 font-medium">
          Step {Math.min(currentStep, 4)} of 4
        </span>
      </div>

      <div className="space-y-2.5">
        {steps.map((step) => {
          const isDone = currentStep > step.id;
          const isCurrent = currentStep === step.id;

          return (
            <div
              key={step.id}
              className={`flex items-center justify-between p-3.5 rounded-lg border transition-all ${
                isCurrent
                  ? 'bg-ink-50 border-ink-400'
                  : isDone
                  ? 'bg-white border-ink-200'
                  : 'bg-ink-50/40 border-ink-100 opacity-60'
              }`}
            >
              <div className="flex items-center gap-3.5">
                <div className={`w-6 h-6 rounded-md flex items-center justify-center font-mono text-xs font-bold transition-all ${
                  isDone
                    ? 'bg-ink-950 text-white'
                    : isCurrent
                    ? 'bg-ink-200 text-ink-950 border border-ink-300'
                    : 'bg-ink-100 text-ink-400'
                }`}>
                  {isDone ? <Check className="w-3.5 h-3.5 stroke-[2.5]" /> : isCurrent ? <Loader2 className="w-3 h-3 animate-spin" /> : step.id}
                </div>
                <div>
                  <p className={`text-sm font-semibold font-sans ${isCurrent ? 'text-ink-950' : isDone ? 'text-ink-900' : 'text-ink-400'}`}>
                    {step.label}
                  </p>
                  <p className="text-xs text-ink-500 font-sans">{step.detail}</p>
                </div>
              </div>

              <span className="text-xs font-mono font-medium">
                {isDone && <span className="text-accent-emerald font-semibold">Verified</span>}
                {isCurrent && <span className="text-ink-950 font-semibold">Processing...</span>}
                {!isDone && !isCurrent && <span className="text-ink-400">Waiting</span>}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
