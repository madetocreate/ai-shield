import { getActionDefinition } from './registry'
import { validateOutput } from './schemas'
import type {
  ActionId,
  ActionRunOptions,
  ActionRunResult,
  ActionModule,
  IdempotencyKey,
  ActionContext,
  JobStatus,
} from './types'
import { runLLM } from './adapters/stubLLM'
import { formatOutputText } from './utils/format'
import { buildInboxContext } from './contextBuilders/inbox'
import { buildCustomersContext } from './contextBuilders/customers'
import { buildGrowthContext } from './contextBuilders/growth'
import { buildStorageContext } from './contextBuilders/storage'
import { buildDocumentsContext } from './contextBuilders/documents'
import { getCache, setCache } from './cache'
import { recordAudit } from './audit'
import { redactObject } from './utils/redaction'

const contextBuilderByModule: Record<ActionModule, (options: ActionRunOptions) => Record<string, unknown>> = {
  inbox: buildInboxContext,
  customers: buildCustomersContext,
  growth: buildGrowthContext,
  storage: buildStorageContext,
  documents: buildDocumentsContext,
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const stableStringify = (value: unknown): string => {
  if (value === null || typeof value !== 'object') return JSON.stringify(value)
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`
  const entries = Object.entries(value as Record<string, unknown>).sort(([a], [b]) => a.localeCompare(b))
  return `{${entries.map(([k, v]) => `"${k}":${stableStringify(v)}`).join(',')}}`
}

const simpleHash = (input: string): string => {
  let hash = 0
  for (let i = 0; i < input.length; i += 1) {
    hash = (hash << 5) - hash + input.charCodeAt(i)
    hash |= 0
  }
  return Math.abs(hash).toString(16)
}

const makeId = () => Math.random().toString(36).slice(2, 10)

export async function runAction(actionId: ActionId, options: ActionRunOptions): Promise<ActionRunResult> {
  const action = getActionDefinition(actionId)
  if (!action) {
    throw new Error(`Aktion ${actionId} nicht registriert`)
  }

  if (!action.supportedModules.includes(options.target.module)) {
    throw new Error(`Aktion ${actionId} unterstützt Modul ${options.target.module} nicht`)
  }

  const builder = contextBuilderByModule[options.target.module]
  const context = builder ? (builder(options) as ActionContext) : { target: options.target }

  const contextHash = simpleHash(stableStringify(context))
  const optionHash = simpleHash(stableStringify(options.actionOverrides || {}))
  const idempotencyKey: IdempotencyKey = `${actionId}:${options.target.targetId || 'na'}:${contextHash}:${optionHash}`

  const cached = getCache(idempotencyKey)
  if (cached) {
    return { ...cached, fromCache: true }
  }

  const jobId = makeId()
  const jobStartedAt = Date.now()
  const job = {
    id: jobId,
    status: 'queued' as JobStatus,
    startedAt: jobStartedAt,
  }

  // Simulate async job lifecycle
  job.status = 'running'
  await delay(120)

  let validated
  let previewText = ''
  let safeErrorMessage: string | undefined
  try {
    const rawOutput = await runLLM(actionId, context)
    validated = validateOutput(action.outputType, rawOutput, action.outputLimits)
    previewText = formatOutputText(validated)
    job.status = 'completed'
  } catch (err) {
    job.status = 'failed'
    job.finishedAt = Date.now()
    safeErrorMessage = err instanceof Error ? err.message : 'Unbekannter Fehler'
    recordAudit({
      actionId,
      module: options.target.module,
      targetId: options.target.targetId,
      preview: safeErrorMessage,
      outputType: action.outputType,
      jobId,
      idempotencyKey,
      durationMs: job.finishedAt - jobStartedAt,
      status: 'failed',
      safeErrorMessage,
    })
    throw err
  }

  job.finishedAt = Date.now()
  const durationMs = job.finishedAt - jobStartedAt

  const result: ActionRunResult = {
    action: { ...action, ...options.actionOverrides },
    output: validated!,
    context: redactObject(context),
    previewText,
    job,
    idempotencyKey,
    durationMs,
  }

  setCache(idempotencyKey, result)

  recordAudit({
    actionId,
    module: options.target.module,
    targetId: options.target.targetId,
    preview: previewText,
    outputType: action.outputType,
    jobId,
    idempotencyKey,
    durationMs,
    status: 'success',
  })

  return result
}

