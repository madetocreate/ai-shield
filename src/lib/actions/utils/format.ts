import type { ActionOutput } from '../types'

export function formatOutputText(output: ActionOutput): string {
  switch (output.type) {
    case 'summary':
      return output.summary.trim()
    case 'draft':
      return output.draft.trim()
    case 'tasks':
      return output.tasks.map((task) => `- ${task.trim()}`).join('\n')
    case 'plan':
      return [output.title ? `Plan: ${output.title}` : 'Plan', ...output.steps.map((s) => `- ${s.trim()}`)]
        .filter(Boolean)
        .join('\n')
    case 'tags':
      return output.tags.map((tag) => `#${tag.replace(/^#/, '')}`).join(' ')
    case 'extraction':
      return Object.entries(output.fields)
        .map(([key, value]) => `${key}: ${value}`)
        .join('\n')
    case 'classification':
      return `${output.label}${output.confidence ? ` (${Math.round(output.confidence * 100)}%)` : ''}${output.details ? `\n${output.details}` : ''}`
    case 'reply':
      return output.reply.trim()
    case 'riskFlags':
      return `${output.flags.map((flag) => `- ${flag}`).join('\n')}${output.severity ? `\nPriorität: ${output.severity}` : ''}`
    default:
      return ''
  }
}

