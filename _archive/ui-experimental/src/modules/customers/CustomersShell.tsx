'use client';

import React, { useState } from 'react';
import { CustomersLeftDrawer } from './CustomersLeftDrawer';
import { CustomersRightDrawer } from './CustomersRightDrawer';
import { Customer } from './types';
import { ActivityEntry } from './panels/CustomerActivityPanel';
import { CUSTOMER_ACTIONS } from './actions';
import { Users, Info, ChevronLeft, ChevronRight } from 'lucide-react';
import { applyAction } from '@/lib/actions/apply';
import type { ActionRunResult, ActionId } from '@/lib/actions/types';
import { undoById } from '@/lib/actions/undo';

export function CustomersShell() {
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [activities, setActivities] = useState<ActivityEntry[]>([]);
  const [isLeftOpen, setIsLeftOpen] = useState(true);
  const [isRightOpen, setIsRightOpen] = useState(true);
  const [lastResult, setResult] = useState<string | null>(null);
  const [lastUndoId, setLastUndoId] = useState<string | null>(null);

  const handleApplyAction = (result: ActionRunResult) => {
    const target = {
      module: 'customers' as const,
      targetId: selectedCustomer?.id,
      setResult: (text: string) => setResult(text),
      addActivity: (entry: unknown) => setActivities((prev) => [entry as ActivityEntry, ...prev]),
      labelLookup: (id: ActionId) => CUSTOMER_ACTIONS.find((a) => a.id === id)?.label || result.action.label,
      currentResult: lastResult,
    }
    const applyResult = applyAction(result, target)
    setLastUndoId(applyResult.undoId || null)
  };

  return (
    <div className="flex h-full overflow-hidden bg-[var(--ak-color-bg-app)] relative">
      {/* Left Drawer: List */}
      <CustomersLeftDrawer
        selectedCustomerId={selectedCustomer?.id || null}
        onSelectCustomer={(c) => {
          setSelectedCustomer(c);
          setResult(null); // Reset result when switching customer
          setActivities([]); // Reset activities for mock demo
          setLastUndoId(null);
        }}
        isOpen={isLeftOpen}
      />

      {/* Middle: Chat (Placeholder/Active Area) */}
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        {/* Context Pill */}
        {selectedCustomer && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-white/80 backdrop-blur-md border border-green-500/20 rounded-full shadow-sm">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[11px] font-bold text-gray-700">Kunde: {selectedCustomer.name}</span>
            </div>
          </div>
        )}

        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-6">
          {!selectedCustomer ? (
            <div className="max-w-sm space-y-4 opacity-40">
              <Users className="w-16 h-16 mx-auto text-gray-300" />
              <div className="space-y-2">
                <h2 className="text-xl font-bold text-gray-900">Kunden-Bereich</h2>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Wähle einen Kunden aus der Liste aus, um die KI-gestützte Kundenakte und Aktionen zu nutzen.
                </p>
              </div>
            </div>
          ) : (
            <div className="w-full max-w-2xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Result Area */}
              {lastResult ? (
                <div className="apple-glass-enhanced p-8 rounded-3xl border border-green-500/10 text-left space-y-4 shadow-xl relative overflow-hidden group">
                  <div className="absolute top-0 left-0 w-1 h-full bg-green-500" />
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2 text-green-600 font-bold text-[10px] uppercase tracking-widest">
                      <Info className="w-4 h-4" />
                      <span>Letztes Ergebnis</span>
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
                      <button 
                        onClick={() => setResult(null)}
                        className="text-gray-300 hover:text-gray-500 transition-colors"
                      >
                        Verwerfen
                      </button>
                    </div>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-lg text-gray-800 leading-relaxed whitespace-pre-wrap">
                      {lastResult}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="p-12 border-2 border-dashed border-gray-100 rounded-[40px] opacity-30">
                  <p className="text-gray-400 font-medium">Bereit für KI-Aktionen</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Floating Toggle Buttons for Drawers (when closed or small screen) */}
        {!isLeftOpen && (
          <button 
            onClick={() => setIsLeftOpen(true)}
            className="fixed left-6 bottom-6 w-12 h-12 bg-white rounded-full shadow-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-green-500 transition-all z-30"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        )}
        {!isRightOpen && selectedCustomer && (
          <button 
            onClick={() => setIsRightOpen(true)}
            className="fixed right-6 bottom-6 w-12 h-12 bg-white rounded-full shadow-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-green-500 transition-all z-30"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
        )}
      </div>

      {/* Right Drawer: KI Panel */}
      <CustomersRightDrawer
        customer={selectedCustomer}
        onApplyAction={handleApplyAction}
        activities={activities}
        isOpen={isRightOpen}
        onClose={() => setIsRightOpen(false)}
      />
    </div>
  );
}

