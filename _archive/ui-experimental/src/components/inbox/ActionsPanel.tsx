'use client';

import React, { useState } from 'react';
import { InboxItem } from '@/components/InboxDrawerWidget';
import { getActionsForChannel, INBOX_ACTIONS, InboxActionId } from '@/lib/inbox/actions';
import { SparklesIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { ActionCard } from './ActionCard';
import { DrawerCard, ActionGroup, ActionButton } from '@/components/ui/drawer-kit/DrawerKit';
import clsx from 'clsx';
import { runAction } from '@/lib/actions/runner';
import type { ActionRunResult } from '@/lib/actions/types';

interface ActionsPanelProps {
  item: InboxItem;
  onApplyAction: (result: ActionRunResult) => void;
}

export const ActionsPanel: React.FC<ActionsPanelProps> = ({ item, onApplyAction }) => {
  const [activeActionId, setActiveActionId] = useState<InboxActionId | null>(null);
  const [previewOutput, setPreviewOutput] = useState<ActionRunResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const channelActions = getActionsForChannel(item.channel);

  const handleActionClick = async (id: InboxActionId) => {
    setActiveActionId(id);
    setPreviewOutput(null);
    setIsGenerating(true);

    try {
      const result = await runAction(id, {
        target: { module: 'inbox', targetId: item.id, title: item.title, channel: item.channel },
        moduleContext: { item },
      });
      setPreviewOutput(result);
    } catch (error) {
      console.error('Action run failed', error);
      setPreviewOutput(null);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="p-4 space-y-4 animate-in fade-in duration-300">
      <DrawerCard title="Quick Actions">
        <div className="space-y-4">
          <ActionGroup label="Empfohlen">
            {channelActions.map((actionId) => {
              const action = INBOX_ACTIONS[actionId];
              const isActive = activeActionId === actionId;
              
              return (
                <button
                  key={actionId}
                  onClick={() => handleActionClick(actionId)}
                  className={clsx(
                    "group flex flex-col gap-1 p-3 rounded-xl transition-all duration-200 border text-left",
                    isActive
                      ? "bg-[var(--ak-color-accent)] text-white border-transparent shadow-[var(--ak-shadow-colored)] scale-[1.02]"
                      : "bg-[var(--ak-color-bg-surface-muted)] text-[var(--ak-color-text-primary)] border-[var(--ak-color-border-subtle)] hover:bg-[var(--ak-color-bg-hover)] shadow-sm"
                  )}
                >
                  <div className="flex items-center justify-between w-full">
                    <div className={clsx(
                      "w-7 h-7 rounded-lg flex items-center justify-center transition-colors",
                      isActive ? "bg-white/20" : "bg-[var(--ak-color-bg-surface)] text-[var(--ak-color-accent-strong)]"
                    )}>
                      <SparklesIcon className="w-3.5 h-3.5" />
                    </div>
                    <ChevronRightIcon className={clsx("w-3 h-3 transition-transform", isActive ? "rotate-90 text-white" : "text-[var(--ak-color-text-muted)]")} />
                  </div>
                  <div className="mt-1">
                    <p className="text-xs font-bold truncate">{action.label}</p>
                    <p className={clsx(
                      "text-[9px] leading-tight line-clamp-2",
                      isActive ? "text-white/80" : "text-[var(--ak-color-text-muted)]"
                    )}>
                      {action.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </ActionGroup>
        </div>
      </DrawerCard>

      {activeActionId && (
        <ActionCard
          label={INBOX_ACTIONS[activeActionId].label}
          output={previewOutput?.previewText || ''}
          isGenerating={isGenerating}
          jobStatus={previewOutput?.job.status}
          onAccept={() => {
            if (previewOutput) {
              onApplyAction(previewOutput);
              setActiveActionId(null);
              setPreviewOutput(null);
            }
          }}
          onDiscard={() => {
            setActiveActionId(null);
            setPreviewOutput(null);
          }}
        />
      )}
    </div>
  );
};

