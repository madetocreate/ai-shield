import { recordAudit } from './audit'
import type { ActionId, ActionOutput, ApplyResult, ActionRunResult, IdempotencyKey } from './types'
import { formatOutputText } from './utils/format'
import type { InboxTabId } from '../inbox/actions'
import type { ActivityEntry as InboxActivity } from '@/components/inbox/ActivityPanel'
import type { ActivityEntry as CustomerActivity } from '@/modules/customers/panels/CustomerActivityPanel'
import type { HistoryEntry as StorageHistory } from '@/modules/settings/storage/types'
import { pushUndo } from './undo'

type InboxTarget = {
  module: 'inbox'
  updateTab: (tab: InboxTabId, content: string, append?: boolean) => void
  setActiveTab: (tab: InboxTabId) => void
  addActivity: (entry: InboxActivity) => void
  labelLookup: (id: ActionId) => string
  targetId?: string
  getTabContent?: (tab: InboxTabId) => string
}

type SimpleTarget = {
  module: 'customers' | 'growth' | 'storage'
  setResult: (text: string) => void
  addActivity: (entry: CustomerActivity | StorageHistory | { id: string; label: string; time: string }) => void
  labelLookup: (id: ActionId) => string
  targetId?: string
  currentResult?: string | null
}

type DocumentsTarget = {
  module: 'documents'
  updateTabs: (data: Partial<Record<'summary' | 'extraction' | 'tasks' | 'history', string>>) => void
  addHistory: (entry: { id: string; label: string; time: string }) => void
  targetId?: string
  getTabContent?: (tab: 'summary' | 'extraction' | 'tasks' | 'history') => string
}

export type ApplyTarget = InboxTarget | SimpleTarget | DocumentsTarget

const toTabForInbox: Record<ActionId, InboxTabId> = {
  'inbox.summarize': 'summary',
  'inbox.top3': 'summary',
  'inbox.draftReply': 'draft',
  'inbox.nextSteps': 'tasks',
  'inbox.assignCase': 'history',
  'inbox.setNotifications': 'history',
  // Unused for other modules
  'customers.profileShort': 'summary',
  'customers.top3Open': 'summary',
  'customers.nextSteps': 'summary',
  'customers.followupDraft': 'draft',
  'customers.timelineSummary': 'summary',
  'customers.risksBlockers': 'history',
  'customers.suggestTags': 'history',
  'growth.variants3': 'draft',
  'growth.hookImprove': 'draft',
  'growth.ctaSuggestions': 'draft',
  'growth.translate': 'draft',
  'growth.campaignPlan': 'tasks',
  'growth.newsletterStart': 'tasks',
  'growth.keywordCluster': 'tasks',
  'storage.summarize': 'summary',
  'storage.extractFacts': 'summary',
  'storage.saveAsMemory': 'history',
  'storage.suggestTags': 'summary',
  'storage.editMemory': 'summary',
  'documents.summarize': 'summary',
  'documents.extractKeyFields': 'summary',
  'documents.classify': 'history',
  'documents.suggestNextSteps': 'tasks',
  'documents.saveAsMemory': 'history',
  'documents.routeToCase': 'history',
}

const makeActivityId = () => Math.random().toString(36).slice(2, 10)

const appliedKeys = new Set<IdempotencyKey>()

function handleInbox(target: InboxTarget, actionId: ActionId, output: ActionOutput): { text: string; undoId?: string } {
  const text = formatOutputText(output)
  const tab = toTabForInbox[actionId] || 'history'
  const append = actionId === 'inbox.top3' || actionId === 'inbox.nextSteps'
  const previous = target.getTabContent ? target.getTabContent(tab) : ''
  target.updateTab(tab, text, append)
  target.setActiveTab(tab)
  target.addActivity({
    id: makeActivityId(),
    label: target.labelLookup(actionId),
    type: actionId,
    time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
  })

  const undoId = pushUndo({
    actionId,
    target: { module: target.module, targetId: target.targetId },
    label: 'Letzte Inbox-Aktion rückgängig',
    undo: () => target.updateTab(tab, previous || ''),
  })

  return { text, undoId }
}

function handleSimple(target: SimpleTarget, actionId: ActionId, output: ActionOutput): { text: string; undoId?: string } {
  const text = formatOutputText(output)
  const previous = target.currentResult || ''
  target.setResult(text)
  target.addActivity({
    id: makeActivityId(),
    label: target.labelLookup(actionId),
    time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
    type: actionId,
  } as unknown as CustomerActivity)

  const undoId = pushUndo({
    actionId,
    target: { module: target.module, targetId: target.targetId },
    label: 'Änderung rückgängig',
    undo: () => target.setResult(previous),
  })

  return { text, undoId }
}

function handleDocuments(target: DocumentsTarget, actionId: ActionId, output: ActionOutput): { text: string; undoId?: string } {
  const text = formatOutputText(output)
  const prevSummary = target.getTabContent ? target.getTabContent('summary') : ''
  const prevExtraction = target.getTabContent ? target.getTabContent('extraction') : ''
  const prevTasks = target.getTabContent ? target.getTabContent('tasks') : ''
  const historyEntry = {
    id: makeActivityId(),
    label: actionId,
    time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
  }
  switch (actionId) {
    case 'documents.summarize':
      target.updateTabs({ summary: text })
      break
    case 'documents.extractKeyFields':
      target.updateTabs({ extraction: text })
      break
    case 'documents.suggestNextSteps':
      target.updateTabs({ tasks: text })
      break
    default:
      target.updateTabs({ history: text })
      break
  }
  target.addHistory(historyEntry)

  const undoId = pushUndo({
    actionId,
    target: { module: target.module, targetId: target.targetId },
    label: 'Dokumenten-Aktion rückgängig',
    undo: () => {
      target.updateTabs({
        summary: prevSummary,
        extraction: prevExtraction,
        tasks: prevTasks,
      })
    },
  })

  return { text, undoId }
}

export function applyAction(result: ActionRunResult, target: ApplyTarget): ApplyResult {
  if (appliedKeys.has(result.idempotencyKey)) {
    return {
      appliedText: '',
      auditId: recordAudit({
        actionId: result.action.id,
        module: target.module,
        targetId: target.targetId,
        preview: result.previewText,
        outputType: result.action.outputType,
        jobId: result.job.id,
        idempotencyKey: result.idempotencyKey,
        durationMs: result.durationMs,
        status: 'canceled',
        safeErrorMessage: 'Duplicate apply (idempotent no-op)',
      }).id,
      idempotencyKey: result.idempotencyKey,
    }
  }

  let appliedText = ''
  let undoId: string | undefined
  if (target.module === 'inbox') {
    const res = handleInbox(target, result.action.id, result.output)
    appliedText = res.text
    undoId = res.undoId
  } else if (target.module === 'documents') {
    const res = handleDocuments(target, result.action.id, result.output)
    appliedText = res.text
    undoId = res.undoId
  } else {
    const res = handleSimple(target, result.action.id, result.output)
    appliedText = res.text
    undoId = res.undoId
  }

  const audit = recordAudit({
    actionId: result.action.id,
    module: target.module,
    targetId: target.targetId,
    preview: result.previewText,
    outputType: result.action.outputType,
    jobId: result.job.id,
    idempotencyKey: result.idempotencyKey,
    durationMs: result.durationMs,
    status: 'success',
  })

  appliedKeys.add(result.idempotencyKey)

  return { appliedText, auditId: audit.id, undoId, idempotencyKey: result.idempotencyKey }
}

