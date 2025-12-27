'use client';

import React, { useState, useEffect } from 'react';
import { StorageLeftDrawer } from './StorageLeftDrawer';
import { StorageRightDrawer } from './StorageRightDrawer';
import { StorageTab, MemoryItem, ChatSource, FileItem, HistoryEntry } from './types';
import { MOCK_MEMORIES, MOCK_CHATS, MOCK_FILES } from './mockData';
import { STORAGE_ACTIONS } from './actions';
import { Database, ChevronLeft, ChevronRight, Info } from 'lucide-react';
import { applyAction } from '@/lib/actions/apply';
import type { ActionRunResult, ActionId } from '@/lib/actions/types';
import { undoById } from '@/lib/actions/undo';

export function StorageShell() {
  const [selectedTab, setSelectedTab] = useState<StorageTab>('memories');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isLeftOpen, setIsLeftOpen] = useState(true);
  const [isRightOpen, setIsRightOpen] = useState(true);
  const [activities, setActivities] = useState<HistoryEntry[]>([]);
  const [lastResult, setLastResult] = useState<string | null>(null);
  const [lastUndoId, setLastUndoId] = useState<string | null>(null);

  const selectedItem = React.useMemo(() => {
    if (!selectedId) return null;
    if (selectedTab === 'memories') return MOCK_MEMORIES.find(m => m.id === selectedId) || null;
    if (selectedTab === 'chats') return MOCK_CHATS.find(c => c.id === selectedId) || null;
    return MOCK_FILES.find(f => f.id === selectedId) || null;
  }, [selectedId, selectedTab]);

  const handleApplyAction = (result: ActionRunResult) => {
    const target = {
      module: 'storage' as const,
      targetId: selectedId || undefined,
      setResult: (text: string) => setLastResult(text),
      addActivity: (entry: unknown) => setActivities((prev) => [entry as HistoryEntry, ...prev]),
      labelLookup: (id: ActionId) => STORAGE_ACTIONS[id as keyof typeof STORAGE_ACTIONS]?.label || result.action.label,
      currentResult: lastResult,
    }
    const applied = applyAction(result, target)
    setLastUndoId(applied.undoId || null)
  };

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    setSelectedId(null);
    setLastResult(null);
    setLastUndoId(null);
  }, [selectedTab]);
  /* eslint-enable react-hooks/set-state-in-effect */

  return (
    <div className="flex h-full overflow-hidden bg-[var(--ak-color-bg-app)] relative">
      {/* Left Drawer */}
      <StorageLeftDrawer
        selectedId={selectedId}
        selectedTab={selectedTab}
        onSelect={(id) => { setSelectedId(id); setLastResult(null); setLastUndoId(null); }}
        onTabChange={setSelectedTab}
        isOpen={isLeftOpen}
      />

      {/* Center: Chat / Action Result Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-6">
          {!selectedItem ? (
            <div className="max-w-sm space-y-4 opacity-40 animate-in fade-in duration-700">
              <Database className="w-16 h-16 mx-auto text-gray-300" />
              <div className="space-y-2">
                <h2 className="text-xl font-bold text-gray-900">Speicher-Verwaltung</h2>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Wähle eine Erinnerung, einen Chat oder ein Dokument aus, um die Details zu prüfen oder KI-Aktionen auszuführen.
                </p>
              </div>
            </div>
          ) : (
            <div className="w-full max-w-2xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {lastResult ? (
                <div className="apple-glass-enhanced p-8 rounded-3xl border border-green-500/10 text-left space-y-4 shadow-xl relative overflow-hidden group">
                  <div className="absolute top-0 left-0 w-1 h-full bg-green-500" />
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2 text-green-600 font-bold text-[10px] uppercase tracking-widest">
                      <Info className="w-4 h-4" />
                      <span>Ergebnis der Aktion</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {lastUndoId && (
                        <button
                          onClick={() => {
                            undoById(lastUndoId)
                            setLastUndoId(null)
                          }}
                          className="text-[11px] font-semibold text-green-600 hover:text-green-700 transition-colors"
                        >
                          Rückgängig
                        </button>
                      )}
                      <button onClick={() => setLastResult(null)} className="text-gray-300 hover:text-gray-500 transition-colors text-xs font-medium">Ausblenden</button>
                    </div>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-lg text-gray-800 leading-relaxed whitespace-pre-wrap">{lastResult}</p>
                  </div>
                </div>
              ) : (
                <div className="p-12 border-2 border-dashed border-gray-100 rounded-[40px] opacity-30">
                  <p className="text-gray-400 font-medium">Bereit für KI-Verwaltung</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Floating Toggles */}
        {!isLeftOpen && (
          <button onClick={() => setIsLeftOpen(true)} className="fixed left-6 bottom-6 w-12 h-12 bg-white rounded-full shadow-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-green-500 transition-all z-30">
            <ChevronRight className="w-6 h-6" />
          </button>
        )}
        {!isRightOpen && selectedItem && (
          <button onClick={() => setIsRightOpen(true)} className="fixed right-6 bottom-6 w-12 h-12 bg-white rounded-full shadow-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-green-500 transition-all z-30">
            <ChevronLeft className="w-6 h-6" />
          </button>
        )}
      </div>

      {/* Right Drawer */}
      <StorageRightDrawer
        selectedItem={selectedItem}
        selectedTab={selectedTab}
        onApplyAction={handleApplyAction}
        activities={activities}
        isOpen={isRightOpen}
        onClose={() => setIsRightOpen(false)}
      />
    </div>
  );
}

