import React, { useState } from 'react';
import { X, Plus, Trash2, Check, Package, Sparkles } from 'lucide-react';

export default function DependenciesList({
  dependencies,
  source,
  onSave,
  onClose
}) {
  const [items, setItems] = useState(dependencies || []);
  const [newPkgName, setNewPkgName] = useState('');

  const toggleItem = (index) => {
    const updated = [...items];
    updated[index].enabled = !updated[index].enabled;
    setItems(updated);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleAdd = (e) => {
    e.preventDefault();
    if (!newPkgName.trim()) return;

    setItems([
      ...items,
      {
        name: newPkgName.trim(),
        version_specifier: '',
        source: 'user',
        enabled: true,
        confidence: 1.0,
      }
    ]);
    setNewPkgName('');
  };

  const handleSave = () => {
    onSave(items);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink-950/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-ink-300 rounded-xl w-full max-w-lg shadow-paper-lg overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-ink-200 flex items-center justify-between bg-ink-50/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-white border border-ink-200 text-ink-900 flex items-center justify-center shadow-paper-sm">
              <Package className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold font-sans text-ink-950 tracking-tight">Review Dependencies</h3>
              <p className="text-xs text-ink-500 font-sans">
                Source: <span className="font-mono text-ink-900 font-medium">{source}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-ink-400 hover:text-ink-800 hover:bg-ink-100 rounded-md transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content list */}
        <div className="p-5 overflow-y-auto flex-1 space-y-2">
          {items.length === 0 ? (
            <p className="text-center text-ink-400 py-8 text-sm font-sans">No dependencies detected.</p>
          ) : (
            items.map((item, idx) => (
              <div
                key={idx}
                className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
                  item.enabled
                    ? 'bg-white border-ink-200 shadow-paper-sm'
                    : 'bg-ink-50 border-ink-200 opacity-60'
                }`}
              >
                <div className="flex items-center gap-3 flex-1">
                  <input
                    type="checkbox"
                    checked={item.enabled}
                    onChange={() => toggleItem(idx)}
                    className="w-4 h-4 rounded text-ink-950 bg-white border-ink-300 focus:ring-ink-900 cursor-pointer"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-ink-950">{item.name}</span>
                      {item.version_specifier && (
                        <span className="text-xs text-ink-500 font-mono">{item.version_specifier}</span>
                      )}
                    </div>
                    {item.mapped_from && (
                      <p className="text-[11px] text-ink-500 font-mono flex items-center gap-1 mt-0.5">
                        <Sparkles className="w-3 h-3 text-ink-400" />
                        Mapped from import <span className="text-ink-950 font-medium">"{item.mapped_from}"</span>
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => removeItem(idx)}
                    className="p-1.5 text-ink-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors"
                    title="Remove package"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}

          {/* Add custom package input */}
          <form onSubmit={handleAdd} className="mt-4 flex gap-2 pt-2">
            <input
              type="text"
              placeholder="Add package (e.g. requests>=2.30)"
              value={newPkgName}
              onChange={(e) => setNewPkgName(e.target.value)}
              className="flex-1 bg-white border border-ink-300 rounded-lg px-3 py-2 text-xs text-ink-950 placeholder-ink-400 focus:outline-none focus:border-ink-950 font-mono shadow-paper-sm"
            />
            <button
              type="submit"
              className="px-3.5 py-2 bg-ink-100 hover:bg-ink-200 border border-ink-300 text-ink-900 rounded-lg text-xs font-medium font-sans flex items-center gap-1 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add
            </button>
          </form>
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
            onClick={handleSave}
            className="px-5 py-2 bg-ink-950 hover:bg-ink-900 text-white rounded-lg text-xs font-medium font-sans flex items-center gap-1.5 shadow-paper-sm transition-colors"
          >
            <Check className="w-3.5 h-3.5" />
            Apply Changes
          </button>
        </div>
      </div>
    </div>
  );
}
