'use client'

import { useState, useEffect } from 'react'
import type { InboxItem } from '@/components/InboxDrawerWidget'
import { InboxReadingPane } from './inbox/InboxReadingPane'
import { RightDrawer } from './inbox/RightDrawer'
import { InboxTabId, INBOX_ACTIONS, InboxActionId } from '@/lib/inbox/actions'
import { ActivityEntry } from './inbox/ActivityPanel'
import { applyAction } from '@/lib/actions/apply'
import type { ActionRunResult, ActionId } from '@/lib/actions/types'
import { undoById } from '@/lib/actions/undo'

 type InboxDetailPanelProps = {
  item: InboxItem | null
  onClose?: () => void
 }

const INITIAL_TAB_CONTENTS: Record<InboxTabId, string> = {
  original: '',
  summary: '',
  draft: '',
  tasks: '',
  history: '',
}

export function InboxDetailPanel({ item, onClose }: InboxDetailPanelProps) {
  const [activeTab, setActiveTab] = useState<InboxTabId>('original')
  const [tabContents, setTabContents] = useState<Record<InboxTabId, string>>(INITIAL_TAB_CONTENTS)
  const [activities, setActivities] = useState<ActivityEntry[]>([])
  const [isDrawerOpen, setIsDrawerOpen] = useState(true)
  const [lastUndoId, setLastUndoId] = useState<string | null>(null)

  useEffect(() => {
    if (item) {
      const timer = setTimeout(() => {
        setActiveTab('original')
        setTabContents(INITIAL_TAB_CONTENTS)
        setActivities([])
        setLastUndoId(null)
      }, 0)
      return () => clearTimeout(timer)
    }
  }, [item?.id])

  if (!item) {
    return (
      <div className="flex h-full items-center justify-center bg-[var(--ak-color-bg-app)]">
        <div className="max-w-xs text-center p-8 apple-glass-enhanced rounded-2xl animate-in fade-in zoom-in-95 duration-700">
          <p className="font-semibold text-[var(--ak-color-text-primary)]">Posteingang leer</p>
          <p className="text-sm mt-2 text-[var(--ak-color-text-secondary)]">
            Wähle eine Konversation aus der Liste aus, um mit der Bearbeitung zu beginnen.
          </p>
        </div>
      </div>
    )
  }

  const handleApplyAction = (result: ActionRunResult) => {
    const target = {
      module: 'inbox' as const,
      targetId: item.id,
      updateTab: (tab: InboxTabId, content: string, shouldAppend?: boolean) =>
        setTabContents((prev) => ({
          ...prev,
          [tab]: shouldAppend && prev[tab] ? `${prev[tab]}\n\n${content}` : content,
        })),
      setActiveTab,
      addActivity: (entry: ActivityEntry) => setActivities((prev) => [entry, ...prev]),
      labelLookup: (id: ActionId) => INBOX_ACTIONS[id as InboxActionId]?.label || result.action.label,
      getTabContent: (tab: InboxTabId) => tabContents[tab],
    }

    const applied = applyAction(result, target)
    setLastUndoId(applied.undoId || null)
  }

  return (
    <div className="flex h-full overflow-hidden bg-[var(--ak-color-bg-app)]">
      <div className="flex-1 min-w-0 h-full relative">
        <InboxReadingPane 
          item={item} 
          activeTab={activeTab}
          onTabChange={setActiveTab}
          tabContents={tabContents}
        />
        {lastUndoId && (
          <div className="absolute bottom-4 left-4">
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
      </div>

      <RightDrawer 
        item={item} 
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onApplyAction={handleApplyAction}
        activities={activities}
      />

      {!isDrawerOpen && (
        <button
          onClick={() => setIsDrawerOpen(true)}
          className="fixed right-6 bottom-6 w-12 h-12 rounded-full bg-[var(--ak-color-accent)] text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform z-30"
          title="Kontext & Aktionen öffnen"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
          </svg>
        </button>
      )}
    </div>
  )
}

