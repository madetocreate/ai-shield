import type { ActionContext, ActionRunOptions } from '../types'
import { redactPII } from '../utils/redaction'

type InboxModuleContext = {
  item?: {
    id?: string
    title?: string
    snippet?: string
    sender?: string
    channel?: string
    body?: string
  }
}

export function buildInboxContext(options: ActionRunOptions): ActionContext {
  const moduleContext = (options.moduleContext || {}) as InboxModuleContext
  const item = moduleContext.item || {}
  return {
    target: options.target,
    title: item.title || options.target.title,
    channel: item.channel,
    sender: redactPII(item.sender),
    preview: redactPII(item.snippet || item.body || ''),
  }
}

