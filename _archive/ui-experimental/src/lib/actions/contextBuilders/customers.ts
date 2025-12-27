import type { ActionContext, ActionRunOptions } from '../types'
import { redactPII } from '../utils/redaction'

type CustomerContextInput = {
  customer?: {
    id?: string
    name?: string
    company?: string
    segment?: string
    lastContact?: string
    notes?: string
    tags?: string[]
  }
}

export function buildCustomersContext(options: ActionRunOptions): ActionContext {
  const moduleContext = (options.moduleContext || {}) as CustomerContextInput
  const customer = moduleContext.customer || {}
  return {
    target: options.target,
    title: customer.name || options.target.title,
    company: customer.company,
    segment: customer.segment,
    lastContact: customer.lastContact,
    notes: redactPII(customer.notes),
    tags: customer.tags,
  }
}

