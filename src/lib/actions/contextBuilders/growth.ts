import type { ActionContext, ActionRunOptions } from '../types'

type GrowthContextInput = {
  mode?: string
  campaignType?: string
  draft?: string
  audience?: string
}

export function buildGrowthContext(options: ActionRunOptions): ActionContext {
  const moduleContext = (options.moduleContext || {}) as GrowthContextInput
  return {
    target: options.target,
    mode: moduleContext.mode,
    campaignType: moduleContext.campaignType,
    draft: moduleContext.draft,
    audience: moduleContext.audience,
  }
}

