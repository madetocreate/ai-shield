import { z } from 'zod'
import type { ActionOutputType, ActionOutput, ActionSchema, ActionOutputLimits } from './types'

const summarySchema = z.object({
  type: z.literal('summary'),
  summary: z.string().trim().min(1),
})

const draftSchema = z.object({
  type: z.literal('draft'),
  draft: z.string().trim().min(1),
})

const tasksSchema = z.object({
  type: z.literal('tasks'),
  tasks: z.array(z.string().trim().min(1)).min(1),
})

const planSchema = z.object({
  type: z.literal('plan'),
  title: z.string().trim().optional(),
  steps: z.array(z.string().trim().min(1)).min(1),
})

const tagsSchema = z.object({
  type: z.literal('tags'),
  tags: z.array(z.string().trim().min(1)).min(1),
})

const extractionSchema = z.object({
  type: z.literal('extraction'),
  fields: z.record(z.string().trim().min(1), z.string().trim()),
  highlights: z.array(z.string().trim()).optional(),
})

const classificationSchema = z.object({
  type: z.literal('classification'),
  label: z.string().trim().min(1),
  confidence: z.number().min(0).max(1).optional(),
  details: z.string().trim().optional(),
})

const replySchema = z.object({
  type: z.literal('reply'),
  reply: z.string().trim().min(1),
})

const riskFlagsSchema = z.object({
  type: z.literal('riskFlags'),
  flags: z.array(z.string().trim().min(1)).min(1),
  severity: z.enum(['low', 'medium', 'high']).optional(),
})

const schemaByType: Record<ActionOutputType, ActionSchema> = {
  summary: summarySchema,
  draft: draftSchema,
  tasks: tasksSchema,
  plan: planSchema,
  tags: tagsSchema,
  extraction: extractionSchema,
  classification: classificationSchema,
  reply: replySchema,
  riskFlags: riskFlagsSchema,
}

const normalizeTasks = (tasks: string[], limits?: ActionOutputLimits) => {
  const max = limits?.maxItems ?? 8
  return tasks
    .map((task) => task.trim())
    .filter(Boolean)
    .slice(0, max)
}

const normalizeTags = (tags: string[], limits?: ActionOutputLimits) => {
  const max = limits?.maxItems ?? 12
  return tags
    .map((tag) => tag.trim().replace(/^#/, ''))
    .filter(Boolean)
    .slice(0, max)
}

const clampString = (value: string, max?: number) => (max ? value.slice(0, max) : value)

const normalizeFields = (fields: Record<string, string>, limits?: ActionOutputLimits) => {
  const maxFields = limits?.maxFields ?? 12
  const entries = Object.entries(fields)
    .map(([k, v]) => [k.trim(), v.trim()] as const)
    .filter(([k, v]) => !!k && !!v)
    .slice(0, maxFields)
  return Object.fromEntries(entries)
}

const normalizeList = (items: string[], max?: number) => items.map((i) => i.trim()).filter(Boolean).slice(0, max)

export function validateOutput(outputType: ActionOutputType, raw: unknown, limits?: ActionOutputLimits): ActionOutput {
  const schema = schemaByType[outputType]
  if (!schema) {
    throw new Error(`Kein Schema für Output-Typ ${outputType} hinterlegt`)
  }

  const hydrated = hydrateDefaults(outputType, raw)
  const parsed = schema.parse(hydrated)

  if (parsed.type === 'tasks') {
    return { ...parsed, tasks: normalizeTasks(parsed.tasks, { maxItems: limits?.maxItems ?? 6 }) }
  }

  if (parsed.type === 'tags') {
    return { ...parsed, tags: normalizeTags(parsed.tags, { maxItems: limits?.maxItems ?? 12 }) }
  }

  if (parsed.type === 'extraction') {
    return { ...parsed, fields: normalizeFields(parsed.fields, { maxFields: limits?.maxFields ?? 12 }) }
  }

  if (parsed.type === 'summary') {
    const maxChars = limits?.maxChars ?? 600
    const normalized = clampString(parsed.summary.trim(), maxChars)
    return { ...parsed, summary: normalized }
  }

  if (parsed.type === 'draft' || parsed.type === 'reply') {
    const maxChars = limits?.maxChars ?? 900
    const body = parsed.type === 'draft' ? parsed.draft : parsed.reply
    const trimmed = clampString(body.trim(), maxChars)
    return parsed.type === 'draft' ? { ...parsed, draft: trimmed } : { ...parsed, reply: trimmed }
  }

  if (parsed.type === 'plan') {
    const steps = normalizeList(parsed.steps, limits?.maxItems ?? 10)
    const title = parsed.title ? clampString(parsed.title, limits?.maxChars ?? 120) : undefined
    return { ...parsed, title, steps }
  }

  if (parsed.type === 'riskFlags') {
    return { ...parsed, flags: normalizeList(parsed.flags, limits?.maxItems ?? 10) }
  }

  return parsed
}

function hydrateDefaults(outputType: ActionOutputType, raw: unknown): unknown {
  if (typeof raw !== 'object' || raw === null) return raw
  const base = raw as Record<string, unknown>
  if (!('type' in base)) {
    return { ...base, type: outputType }
  }
  return raw
}

