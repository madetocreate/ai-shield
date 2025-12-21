import type { z } from 'zod'

export type ActionModule = 'inbox' | 'customers' | 'growth' | 'storage' | 'documents'

export type ActionOutputType =
  | 'summary'
  | 'draft'
  | 'tasks'
  | 'plan'
  | 'tags'
  | 'extraction'
  | 'classification'
  | 'reply'
  | 'riskFlags'

export type ActionId =
  // Inbox
  | 'inbox.summarize'
  | 'inbox.top3'
  | 'inbox.draftReply'
  | 'inbox.nextSteps'
  | 'inbox.assignCase'
  | 'inbox.setNotifications'
  // Customers
  | 'customers.profileShort'
  | 'customers.top3Open'
  | 'customers.nextSteps'
  | 'customers.followupDraft'
  | 'customers.timelineSummary'
  | 'customers.risksBlockers'
  | 'customers.suggestTags'
  // Growth
  | 'growth.variants3'
  | 'growth.hookImprove'
  | 'growth.ctaSuggestions'
  | 'growth.translate'
  | 'growth.campaignPlan'
  | 'growth.newsletterStart'
  | 'growth.keywordCluster'
  // Storage
  | 'storage.summarize'
  | 'storage.extractFacts'
  | 'storage.saveAsMemory'
  | 'storage.suggestTags'
  | 'storage.editMemory'
  // Documents
  | 'documents.summarize'
  | 'documents.extractKeyFields'
  | 'documents.classify'
  | 'documents.suggestNextSteps'
  | 'documents.saveAsMemory'
  | 'documents.routeToCase'

export type RiskLevel = 'low' | 'medium' | 'high'

export type ActionPermissions = {
  roles: Array<'owner' | 'admin' | 'member'>
}

export type ActionOutputLimits = {
  maxChars?: number
  maxItems?: number
  maxFields?: number
  maxBullets?: number
}

export interface ActionDefinition {
  id: ActionId
  label: string
  description?: string
  supportedModules: ActionModule[]
  outputType: ActionOutputType
  requiresApproval: boolean
  uiPlacement: 'primary' | 'secondary'
  defaultTone?: 'short' | 'neutral' | 'locker' | 'formal'
  riskLevel: RiskLevel
  permissions: ActionPermissions
  dataAccess?: string[]
  outputLimits?: ActionOutputLimits
}

export type ActionTargetRef = {
  module: ActionModule
  targetId?: string
  title?: string
  subtype?: string
  channel?: string
}

export type ActionContext = Record<string, unknown> & {
  target?: ActionTargetRef
}

export type ActionRunOptions = {
  target: ActionTargetRef
  moduleContext?: Record<string, unknown>
  actionOverrides?: Partial<ActionDefinition>
}

export type JobStatus = 'queued' | 'running' | 'completed' | 'failed'

export type ActionJob = {
  id: string
  status: JobStatus
  startedAt: number
  finishedAt?: number
  error?: string
}

export type IdempotencyKey = string

export type SummaryOutput = { type: 'summary'; summary: string }
export type DraftOutput = { type: 'draft'; draft: string }
export type TasksOutput = { type: 'tasks'; tasks: string[] }
export type PlanOutput = { type: 'plan'; title?: string; steps: string[] }
export type TagsOutput = { type: 'tags'; tags: string[] }
export type ExtractionOutput = {
  type: 'extraction'
  fields: Record<string, string>
  highlights?: string[]
}
export type ClassificationOutput = {
  type: 'classification'
  label: string
  confidence?: number
  details?: string
}
export type ReplyOutput = { type: 'reply'; reply: string }
export type RiskFlagsOutput = { type: 'riskFlags'; flags: string[]; severity?: 'low' | 'medium' | 'high' }

export type ActionOutput =
  | SummaryOutput
  | DraftOutput
  | TasksOutput
  | PlanOutput
  | TagsOutput
  | ExtractionOutput
  | ClassificationOutput
  | ReplyOutput
  | RiskFlagsOutput

export interface ActionRunResult {
  action: ActionDefinition
  output: ActionOutput
  context: ActionContext
  previewText: string
  job: ActionJob
  idempotencyKey: IdempotencyKey
  fromCache?: boolean
  durationMs: number
}

export type ActionSchema = z.ZodType<ActionOutput>

export type ApplyResult = {
  appliedText: string
  auditId: string
  undoId?: string
  idempotencyKey: IdempotencyKey
}

export type AuditEntry = {
  id: string
  actionId: ActionId
  module: ActionModule
  targetId?: string
  outputType: ActionOutputType
  preview: string
  createdAt: string
  jobId?: string
  idempotencyKey?: IdempotencyKey
  durationMs?: number
  status: 'success' | 'failed' | 'canceled'
  safeErrorMessage?: string
}

