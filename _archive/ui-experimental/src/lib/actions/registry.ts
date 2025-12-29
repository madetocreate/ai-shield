import type { ActionDefinition, ActionId, ActionModule, ActionOutputType, ActionOutputLimits } from './types'

const defaultPermissions = { roles: ['owner', 'admin', 'member'] as const }

const defaultLimitsByType: Partial<Record<ActionOutputType, ActionOutputLimits>> = {
  summary: { maxChars: 600, maxBullets: 5 },
  draft: { maxChars: 900 },
  tasks: { maxItems: 6 },
  plan: { maxItems: 10 },
  tags: { maxItems: 12 },
  extraction: { maxFields: 12 },
  classification: { maxChars: 240 },
  riskFlags: { maxItems: 10 },
}

const def = (
  id: ActionId,
  label: string,
  module: ActionModule,
  outputType: ActionOutputType,
  options: Partial<Omit<ActionDefinition, 'id' | 'label' | 'supportedModules' | 'outputType'>> = {},
): ActionDefinition => ({
  id,
  label,
  supportedModules: [module],
  outputType,
  requiresApproval: options.requiresApproval ?? true,
  uiPlacement: 'primary',
  riskLevel: options.riskLevel ?? 'low',
  permissions: options.permissions ?? defaultPermissions,
  dataAccess: options.dataAccess ?? [],
  outputLimits: options.outputLimits ?? defaultLimitsByType[outputType],
  ...options,
})

export const ACTION_REGISTRY: Record<ActionId, ActionDefinition> = {
  // Inbox
  'inbox.summarize': def('inbox.summarize', 'Posteingang zusammenfassen', 'inbox', 'summary', { defaultTone: 'neutral' }),
  'inbox.top3': def('inbox.top3', 'Top 3 Punkte', 'inbox', 'summary', { description: 'Priorisierte Liste', defaultTone: 'short' }),
  'inbox.draftReply': def('inbox.draftReply', 'Antwortentwurf', 'inbox', 'draft', { defaultTone: 'locker' }),
  'inbox.nextSteps': def('inbox.nextSteps', 'Nächste Schritte', 'inbox', 'tasks'),
  'inbox.assignCase': def('inbox.assignCase', 'Fall zuordnen', 'inbox', 'classification', { uiPlacement: 'secondary' }),
  'inbox.setNotifications': def('inbox.setNotifications', 'Benachrichtigungen', 'inbox', 'riskFlags', { uiPlacement: 'secondary' }),

  // Customers
  'customers.profileShort': def('customers.profileShort', 'Profil Kurzfassung', 'customers', 'summary'),
  'customers.top3Open': def('customers.top3Open', 'Top 3 offene Punkte', 'customers', 'tasks'),
  'customers.nextSteps': def('customers.nextSteps', 'Nächste Schritte', 'customers', 'tasks'),
  'customers.followupDraft': def('customers.followupDraft', 'Follow-up Entwurf', 'customers', 'draft', { defaultTone: 'locker' }),
  'customers.timelineSummary': def('customers.timelineSummary', 'Verlauf zusammenfassen', 'customers', 'summary'),
  'customers.risksBlockers': def('customers.risksBlockers', 'Risiken & Blocker', 'customers', 'riskFlags', { uiPlacement: 'secondary' }),
  'customers.suggestTags': def('customers.suggestTags', 'Tags vorschlagen', 'customers', 'tags', { uiPlacement: 'secondary' }),

  // Growth
  'growth.variants3': def('growth.variants3', '3 Varianten erstellen', 'growth', 'draft', { defaultTone: 'short' }),
  'growth.hookImprove': def('growth.hookImprove', 'Hook verbessern', 'growth', 'draft'),
  'growth.ctaSuggestions': def('growth.ctaSuggestions', 'CTA Vorschläge', 'growth', 'draft'),
  'growth.translate': def('growth.translate', 'Übersetzen (Stub)', 'growth', 'draft'),
  'growth.campaignPlan': def('growth.campaignPlan', 'Kampagnenplan', 'growth', 'plan'),
  'growth.newsletterStart': def('growth.newsletterStart', 'Newsletter starten', 'growth', 'plan'),
  'growth.keywordCluster': def('growth.keywordCluster', 'Keyword Cluster', 'growth', 'tags'),

  // Storage
  'storage.summarize': def('storage.summarize', 'Speicher zusammenfassen', 'storage', 'summary'),
  'storage.extractFacts': def('storage.extractFacts', 'Fakten extrahieren', 'storage', 'extraction'),
  'storage.saveAsMemory': def('storage.saveAsMemory', 'Als Memory speichern', 'storage', 'classification'),
  'storage.suggestTags': def('storage.suggestTags', 'Tags vorschlagen', 'storage', 'tags', { uiPlacement: 'secondary' }),
  'storage.editMemory': def('storage.editMemory', 'Memory bearbeiten', 'storage', 'summary', { uiPlacement: 'secondary' }),

  // Documents
  'documents.summarize': def('documents.summarize', 'Dokument zusammenfassen', 'documents', 'summary'),
  'documents.extractKeyFields': def('documents.extractKeyFields', 'Schlüsselfelder extrahieren', 'documents', 'extraction'),
  'documents.classify': def('documents.classify', 'Dokument klassifizieren', 'documents', 'classification', { uiPlacement: 'secondary' }),
  'documents.suggestNextSteps': def('documents.suggestNextSteps', 'Nächste Schritte', 'documents', 'tasks'),
  'documents.saveAsMemory': def('documents.saveAsMemory', 'Als Memory speichern', 'documents', 'classification', { uiPlacement: 'secondary' }),
  'documents.routeToCase': def('documents.routeToCase', 'Fall zuordnen', 'documents', 'classification', { uiPlacement: 'secondary' }),
}

export const listActionsForModule = (module: ActionModule): ActionDefinition[] =>
  Object.values(ACTION_REGISTRY).filter((action) => action.supportedModules.includes(module))

export const getActionDefinition = (id: ActionId): ActionDefinition | undefined => ACTION_REGISTRY[id]

