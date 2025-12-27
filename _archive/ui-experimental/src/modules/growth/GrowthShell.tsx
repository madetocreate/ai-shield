'use client';

import React, { useState } from 'react';
import { GrowthLeftDrawer } from './GrowthLeftDrawer';
import { GrowthRightDrawer } from './GrowthRightDrawer';
import { GrowthCanvas } from './GrowthCanvas';
import { GrowthMode, CampaignType } from './types';
import { GROWTH_ACTIONS } from './actions';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { applyAction } from '@/lib/actions/apply';
import type { ActionRunResult } from '@/lib/actions/types';
import { undoById } from '@/lib/actions/undo';

export function GrowthShell() {
  const [activeMode, setActiveMode] = useState<GrowthMode>('campaigns');
  const [campaignType, setCampaignType] = useState<CampaignType>('newsletter');
  const [isLeftOpen, setIsLeftOpen] = useState(true);
  const [isRightOpen, setIsRightOpen] = useState(true);
  const [activities, setActivities] = useState<{ id: string, label: string, time: string }[]>([]);
  const [lastResult, setLastResult] = useState<string | null>(null);
  const [lastUndoId, setLastUndoId] = useState<string | null>(null);

  const handleApplyAction = (result: ActionRunResult) => {
    const target = {
      module: 'growth' as const,
      targetId: `${activeMode}-${campaignType}`,
      setResult: (text: string) => setLastResult(text),
      addActivity: (entry: { id: string; label: string; time: string }) => setActivities((prev) => [entry, ...prev]),
      labelLookup: (id: string) => GROWTH_ACTIONS[id as keyof typeof GROWTH_ACTIONS]?.label || result.action.label,
      currentResult: lastResult,
    }
    const applied = applyAction(result, target)
    setLastUndoId(applied.undoId || null)
  }

  return (
    <div className="flex h-full overflow-hidden bg-[var(--ak-color-bg-app)] relative">
      <GrowthLeftDrawer
        activeMode={activeMode}
        onModeChange={(m) => { setActiveMode(m); setLastResult(null); setLastUndoId(null); }}
        isOpen={isLeftOpen}
      />

      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        <GrowthCanvas 
          mode={activeMode} 
          campaignType={campaignType}
          onCampaignTypeChange={(t) => { setCampaignType(t); setLastResult(null); setLastUndoId(null); }}
          result={lastResult}
        />
        {lastUndoId && (
          <div className="absolute bottom-4 left-4 z-10">
            <button
              onClick={() => {
                undoById(lastUndoId)
                setLastUndoId(null)
              }}
              className="px-3 py-1.5 text-[11px] font-semibold rounded-lg bg-white/80 border border-[var(--ak-color-border-subtle)] shadow-sm hover:bg-[var(--ak-color-bg-hover)]"
            >
              Rückgängig
            </button>
          </div>
        )}

        {!isLeftOpen && (
          <button onClick={() => setIsLeftOpen(true)} className="fixed left-6 bottom-6 w-12 h-12 bg-white rounded-full shadow-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-green-500 transition-all z-30"><ChevronRight className="w-6 h-6" /></button>
        )}
        {!isRightOpen && (
          <button onClick={() => setIsRightOpen(true)} className="fixed right-6 bottom-6 w-12 h-12 bg-white rounded-full shadow-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-green-500 transition-all z-30"><ChevronLeft className="w-6 h-6" /></button>
        )}
      </div>

      <GrowthRightDrawer
        mode={activeMode}
        campaignType={campaignType}
        onApplyAction={handleApplyAction}
        activities={activities}
        isOpen={isRightOpen}
        onClose={() => setIsRightOpen(false)}
      />
    </div>
  );
}

