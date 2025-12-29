import type { ActionContext, ActionRunOptions } from '../types'
import { redactPII } from '../utils/redaction'

type StorageContextInput = {
  item?: {
    id?: string
    title?: string
    summary?: string
    source?: string
    tags?: string[]
    type?: string
  }
}

export function buildStorageContext(options: ActionRunOptions): ActionContext {
  const moduleContext = (options.moduleContext || {}) as StorageContextInput
  const item = moduleContext.item || {}
  return {
    target: options.target,
    title: item.title || options.target.title,
    summary: redactPII(item.summary),
    source: item.source,
    tags: item.tags,
    type: item.type,
  }
}

