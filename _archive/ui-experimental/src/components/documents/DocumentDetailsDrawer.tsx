'use client'

import { useState } from 'react'
import { 
  TagIcon, 
  CloudArrowDownIcon, 
  ShareIcon, 
  SparklesIcon, 
  CheckIcon, 
  DocumentTextIcon, 
  ArchiveBoxIcon, 
  ClipboardDocumentCheckIcon,
  XMarkIcon,
  CommandLineIcon
} from '@heroicons/react/24/outline'
import clsx from 'clsx'
import { listActionsForModule } from '@/lib/actions/registry'
import { runAction } from '@/lib/actions/runner'
import { applyAction } from '@/lib/actions/apply'
import { AkIconButton } from '@/components/ui/AkIconButton'
import { AkButton } from '@/components/ui/AkButton'
import type { ActionRunResult, ActionId } from '@/lib/actions/types'
import { 
  DrawerHeader, 
  DrawerCard, 
  DrawerSectionTitle, 
  ActionGroup, 
  ActionButton, 
  DrawerEmptyState,
  StatusChip
} from '@/components/ui/drawer-kit'
import { AkDrawerScaffold } from '@/components/ui/AkDrawerScaffold'
import { AkBadge } from '@/components/ui/AkBadge'
import { undoById } from '@/lib/actions/undo'

// Types (Dummy)
type Document = {
  id: string
  title: string
  type: string
  size: string
  uploadedAt: string
  tags: string[]
  contentPreview: string
  author?: string
  status?: 'processed' | 'pending' | 'error'
}

type DocumentDetailsDrawerProps = {
  document: Document | null
  onClose: () => void
}

type DocumentTab = 'original' | 'summary' | 'extraction' | 'tasks' | 'history'

export function DocumentDetailsDrawer({ document, onClose }: DocumentDetailsDrawerProps) {
  const [activeTab, setActiveTab] = useState<DocumentTab>('original')
  const [tabContents, setTabContents] = useState<Record<DocumentTab, string>>({
    original: '',
    summary: '',
    extraction: '',
    tasks: '',
    history: '',
  })
  const [history, setHistory] = useState<{ id: string; label: string; time: string }[]>([])
  const [preview, setPreview] = useState<ActionRunResult | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [lastUndoId, setLastUndoId] = useState<string | null>(null)

  if (!document) {
    return (
      <AkDrawerScaffold
        title={<DrawerHeader title="Dokumenten Analyse" subtitle="Keine Auswahl" onClose={onClose} />}
        headerClassName="!p-0"
        bodyClassName="h-full"
      >
        <DrawerEmptyState
          icon={<DocumentTextIcon className="h-10 w-10" />}
          title="Kein Dokument ausgewählt"
          description="Wähle ein Dokument aus deiner Bibliothek aus, um es zu analysieren."
          actions={
            <ActionGroup>
              <ActionButton label="Dokument hochladen" icon={<CloudArrowDownIcon className="h-4 w-4" />} shortcut="U" onClick={() => console.log('Upload')} variant="primary" />
              <ActionButton label="Rechnung auslesen" icon={<ClipboardDocumentCheckIcon className="h-4 w-4" />} shortcut="I" onClick={() => console.log('Invoice')} />
              <ActionButton label="Ordnen lassen" icon={<ArchiveBoxIcon className="h-4 w-4" />} shortcut="O" onClick={() => console.log('Organize')} />
            </ActionGroup>
          }
        />
      </AkDrawerScaffold>
    )
  }

  const docActions = listActionsForModule('documents')

  const OriginalContent = (
    <div className="space-y-6">
      <DrawerCard className="border-dashed" padding="normal">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-[var(--ak-color-bg-surface-muted)] shadow-inner flex items-center justify-center border border-[var(--ak-color-border-subtle)]">
            <span className="text-xl font-bold text-[var(--ak-color-accent-strong)] uppercase tracking-tight">{document.type}</span>
          </div>
          <div className="text-center">
            <h3 className="text-lg font-bold text-[var(--ak-color-text-primary)] leading-tight">{document.title}</h3>
            <div className="flex items-center justify-center gap-2 mt-2">
              <AkBadge tone="muted" size="sm">{document.size}</AkBadge>
              <AkBadge tone="muted" size="sm">{document.uploadedAt}</AkBadge>
            </div>
          </div>
        </div>
      </DrawerCard>

      <div className="grid grid-cols-2 gap-4">
        <DrawerCard>
          <DrawerSectionTitle>Status</DrawerSectionTitle>
          <div className="flex items-center gap-2">
            <StatusChip label="Bereit" variant="success" size="xs" />
          </div>
        </DrawerCard>
        <DrawerCard>
          <DrawerSectionTitle>Autor</DrawerSectionTitle>
          <p className="text-sm font-medium text-[var(--ak-color-text-primary)] truncate">{document.author || 'System'}</p>
        </DrawerCard>
      </div>

      <DrawerCard>
        <DrawerSectionTitle>Tags</DrawerSectionTitle>
        <div className="flex flex-wrap gap-2">
          {document.tags.map(tag => (
            <span key={tag} className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-md bg-[var(--ak-color-bg-surface-muted)] text-[var(--ak-color-text-secondary)] border border-[var(--ak-color-border-subtle)] hover:bg-[var(--ak-color-bg-hover)] transition-colors cursor-pointer shadow-sm">
              <TagIcon className="w-3 h-3" />
              {tag}
            </span>
          ))}
          <button className="px-2 py-0.5 text-xs font-medium rounded-md border border-dashed border-[var(--ak-color-border-subtle)] text-[var(--ak-color-text-muted)] hover:text-[var(--ak-color-accent-strong)] hover:border-[var(--ak-color-accent-strong)] transition-colors">
            + Tag
          </button>
        </div>
      </DrawerCard>

      <DrawerCard>
        <DrawerSectionTitle>Vorschau</DrawerSectionTitle>
        <div className="relative group">
          <div className="bg-[var(--ak-color-bg-surface-muted)] p-4 rounded-xl border border-[var(--ak-color-border-subtle)] font-mono text-[10px] leading-relaxed text-[var(--ak-color-text-secondary)] overflow-hidden max-h-[160px]">
            {document.contentPreview}
            <div className="mt-2 opacity-40">
              [Seiten 2-12...]
            </div>
          </div>
          <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-[var(--ak-color-bg-surface)] to-transparent pointer-events-none rounded-b-xl" />
        </div>
      </DrawerCard>
    </div>
  )

  const handleActionClick = async (actionId: ActionId) => {
    setIsGenerating(true)
    setPreview(null)
    try {
      const result = await runAction(actionId, {
        target: { module: 'documents', targetId: document.id, title: document.title },
        moduleContext: { document },
      })
      setPreview(result)
    } catch (error) {
      console.error('Document action failed', error)
      setPreview(null)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleApply = (result: ActionRunResult) => {
    const target = {
      module: 'documents' as const,
      targetId: document.id,
      updateTabs: (data: Partial<Record<'summary' | 'extraction' | 'tasks' | 'history', string>>) => setTabContents((prev) => ({ ...prev, ...data })),
      addHistory: (entry: { id: string; label: string; time: string }) => setHistory((prev) => [entry, ...prev]),
      getTabContent: (tab: 'summary' | 'extraction' | 'tasks' | 'history') => tabContents[tab],
    }
    const applied = applyAction(result, target)
    setLastUndoId(applied.undoId || null)
    setPreview(null)
  }

  const tabs: { id: DocumentTab; label: string }[] = [
    { id: 'original', label: 'Original' },
    { id: 'summary', label: 'KI-Summary' },
    { id: 'extraction', label: 'Extraktion' },
    { id: 'tasks', label: 'Aufgaben' },
    { id: 'history', label: 'Verlauf' },
  ]

  return (
    <div className="h-full grid grid-cols-1 lg:grid-cols-[minmax(0,1fr),360px]">
      <div className="flex flex-col h-full overflow-hidden bg-[var(--ak-color-bg-app)] relative">
        <AkDrawerScaffold
          title={<DrawerHeader 
            title="Dokumenten-Analyse" 
            subtitle={document.title}
            onClose={onClose} 
            trailing={
              <>
                <AkIconButton size="sm" variant="ghost" title="Download"><CloudArrowDownIcon className="h-4 w-4" /></AkIconButton>
                <AkIconButton size="sm" variant="ghost" title="Teilen"><ShareIcon className="h-4 w-4" /></AkIconButton>
              </>
            }
          />}
          headerClassName="!p-0"
          bodyClassName="flex flex-col h-full overflow-hidden"
        >
          <div className="flex items-center gap-1 px-4 py-2 border-b border-[var(--ak-color-border-hairline)] bg-[var(--ak-color-bg-surface-muted)]/30">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={clsx(
                  'px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider rounded-lg transition-all',
                  activeTab === tab.id
                    ? 'bg-[var(--ak-color-accent)] text-white shadow-sm scale-[1.02]'
                    : 'text-[var(--ak-color-text-muted)] hover:text-[var(--ak-color-text-primary)] hover:bg-[var(--ak-color-bg-hover)]'
                )}
              >
                {tab.label}
              </button>
            ))}
            {lastUndoId && (
              <button
                onClick={() => {
                  undoById(lastUndoId)
                  setLastUndoId(null)
                }}
                className="ml-auto px-3 py-1.5 text-[10px] font-semibold text-[var(--ak-color-accent-strong)] hover:text-[var(--ak-color-accent)]"
              >
                Rückgängig
              </button>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-4 ak-scrollbar">
            {activeTab === 'original' && OriginalContent}
            {activeTab === 'summary' && <SectionBox title="KI-Zusammenfassung" content={tabContents.summary} icon={<SparklesIcon className="h-4 w-4" />} />}
            {activeTab === 'extraction' && <SectionBox title="Daten-Extraktion" content={tabContents.extraction} icon={<ClipboardDocumentCheckIcon className="h-4 w-4" />} />}
            {activeTab === 'tasks' && <SectionBox title="Nächste Schritte" content={tabContents.tasks} icon={<CheckIcon className="h-4 w-4" />} />}
            {activeTab === 'history' && <SectionBox title="Audit-Trail" content={tabContents.history} history={history} icon={<ArchiveBoxIcon className="h-4 w-4" />} />}
          </div>
        </AkDrawerScaffold>
      </div>

      <div className="border-l border-[var(--ak-color-border-subtle)] bg-[var(--ak-color-bg-surface)] dark:bg-[var(--ak-color-graphite-surface)] p-4 space-y-4 overflow-y-auto ak-scrollbar">
        {preview ? (
          <DrawerCard className="border-[var(--ak-color-accent)]/20 bg-[var(--ak-color-accent-soft)]/10" padding="none">
            <div className="px-3 py-2 bg-[var(--ak-color-accent-soft)]/20 border-b border-[var(--ak-color-accent)]/10 flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-[10px] font-bold text-[var(--ak-color-accent-strong)] uppercase tracking-widest">
                <SparklesIcon className="w-3.5 h-3.5" />
                {isGenerating || preview.job.status !== 'completed' ? 'Wird vorbereitet…' : 'Vorschau'}
              </div>
              <AkIconButton size="sm" variant="ghost" onClick={() => setPreview(null)}><XMarkIcon className="w-3.5 h-3.5" /></AkIconButton>
            </div>
            <div className="p-3">
              {isGenerating || preview.job.status !== 'completed' ? (
                <div className="space-y-2 py-2">
                  <div className="h-2.5 bg-[var(--ak-color-bg-surface-muted)] rounded-full w-full animate-pulse" />
                  <div className="h-2.5 bg-[var(--ak-color-bg-surface-muted)] rounded-full w-5/6 animate-pulse" />
                </div>
              ) : (
                <div className="text-[11px] text-[var(--ak-color-text-secondary)] leading-relaxed whitespace-pre-wrap max-h-[160px] overflow-y-auto ak-scrollbar font-medium">
                  {preview?.previewText}
                </div>
              )}
            </div>
            <div className="p-2 border-t border-[var(--ak-color-border-subtle)] flex gap-2 justify-end bg-[var(--ak-color-bg-surface-muted)]/20">
              <AkButton size="sm" variant="ghost" onClick={() => setPreview(null)}>Verwerfen</AkButton>
              <AkButton 
                size="sm" 
                variant="primary" 
                disabled={isGenerating || !preview}
                onClick={() => preview && handleApply(preview)}
                leftIcon={<CheckIcon className="w-3.5 h-3.5" />}
              >
                Übernehmen
              </AkButton>
            </div>
          </DrawerCard>
        ) : (
          <ActionGroup title="Aktionen">
            {docActions.map((action) => (
              <ActionButton
                key={action.id}
                label={action.label}
                icon={<SparklesIcon className="w-4 h-4" />}
                onClick={() => handleActionClick(action.id)}
              />
            ))}
          </ActionGroup>
        )}
      </div>
    </div>
  )
}

const SectionBox = ({ title, content, history, icon }: { title: string; content: string; icon: React.ReactNode; history?: { id: string; label: string; time: string }[] }) => (
  <DrawerCard>
    <DrawerSectionTitle>{title}</DrawerSectionTitle>
    <div className="space-y-4">
      {history ? (
        <div className="space-y-3">
          {history.length > 0 ? history.map((entry) => (
            <div key={entry.id} className="flex items-start gap-3">
              <div className="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-[var(--ak-color-accent)] shadow-[0_0_8px_var(--ak-color-accent)]" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-[var(--ak-color-text-primary)] leading-none">{entry.label}</p>
                <p className="text-[10px] text-[var(--ak-color-text-muted)] mt-1 font-mono uppercase">{entry.time}</p>
              </div>
            </div>
          )) : (
            <div className="flex flex-col items-center justify-center py-8 text-center space-y-2 opacity-40">
              {icon}
              <p className="text-xs font-medium">Keine Einträge vorhanden.</p>
            </div>
          )}
          {content && (
            <div className="pt-3 border-t border-[var(--ak-color-border-hairline)]">
              <p className="text-xs text-[var(--ak-color-text-secondary)] whitespace-pre-wrap leading-relaxed">{content}</p>
            </div>
          )}
        </div>
      ) : (
        <div className={clsx(
          "min-h-[120px] flex flex-col items-center justify-center text-center p-4",
          !content && "opacity-40 space-y-2"
        )}>
          {!content && icon}
          <p className="text-xs text-[var(--ak-color-text-secondary)] whitespace-pre-wrap leading-relaxed">
            {content || 'Noch kein Ergebnis generiert.'}
          </p>
        </div>
      )}
    </div>
  </DrawerCard>
)

