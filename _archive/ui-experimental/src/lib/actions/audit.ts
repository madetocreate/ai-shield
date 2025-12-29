import type { ActionId, AuditEntry, ActionModule, ActionOutputType, IdempotencyKey } from './types'

const auditLog: AuditEntry[] = []

const makeId = () => Math.random().toString(36).slice(2, 10)

type AuditParams = {
  actionId: ActionId
  module: ActionModule
  targetId?: string
  preview: string
  outputType: ActionOutputType
  jobId?: string
  idempotencyKey?: IdempotencyKey
  durationMs?: number
  status: 'success' | 'failed' | 'canceled'
  safeErrorMessage?: string
}

export function recordAudit(params: AuditParams): AuditEntry {
  const entry: AuditEntry = {
    id: makeId(),
    actionId: params.actionId,
    module: params.module,
    targetId: params.targetId,
    preview: params.preview,
    outputType: params.outputType,
    createdAt: new Date().toISOString(),
    jobId: params.jobId,
    idempotencyKey: params.idempotencyKey,
    durationMs: params.durationMs,
    status: params.status,
    safeErrorMessage: params.safeErrorMessage,
  }
  auditLog.unshift(entry)
  return entry
}

export function getAuditLog(): AuditEntry[] {
  return [...auditLog]
}

