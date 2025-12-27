import type { ActionId, ActionContext, ActionOutput } from '../types'

const fallbackText = 'Dies ist ein deterministischer Stub-Output. Die echte LLM-Integration wird später ersetzt.'

const bullet = (items: string[]) => items.map((item) => `- ${item}`).join('\n')

export async function runLLM(actionId: ActionId, context: ActionContext): Promise<ActionOutput> {
  const subject = context.title || context.target?.title || 'Fall'
  switch (actionId) {
    // Inbox
    case 'inbox.summarize':
      return { type: 'summary', summary: `Kurzfassung zu "${subject}": Anfrage geklärt, Fokus auf Antwort und nächster Schritt.` }
    case 'inbox.top3':
      return {
        type: 'summary',
        summary: bullet(['Priorität 1: Rückmeldung senden', 'Priorität 2: Termin bestätigen', 'Priorität 3: Status im System aktualisieren']),
      }
    case 'inbox.draftReply':
      return { type: 'draft', draft: `Hallo,\n\ndanke für deine Nachricht zu "${subject}". Ich kümmere mich darum und melde mich asap.\n\nLG` }
    case 'inbox.nextSteps':
      return { type: 'tasks', tasks: ['Antwort formulieren', 'Interne Rückfrage klären', 'Follow-up für morgen setzen'] }
    case 'inbox.assignCase':
      return { type: 'classification', label: 'Support-Fall', confidence: 0.82, details: 'Passt zu bestehendem Ticket-Workflow.' }
    case 'inbox.setNotifications':
      return { type: 'riskFlags', flags: ['Erinnerung in 24h', 'Dringlichkeit: mittel'], severity: 'medium' }

    // Customers
    case 'customers.profileShort':
      return { type: 'summary', summary: `Kunde ${subject}: schätzt proaktive Kommunikation, Fokus auf Zuverlässigkeit.` }
    case 'customers.top3Open':
      return { type: 'tasks', tasks: ['Offenes Angebot nachfassen', 'Review-Termin planen', 'Feedback zur letzten Lieferung holen'] }
    case 'customers.nextSteps':
      return { type: 'tasks', tasks: ['Nächste Demo zusagen', 'Blocker ausräumen', 'Status-Update in CRM schreiben'] }
    case 'customers.followupDraft':
      return { type: 'draft', draft: `Hi ${subject},\nkurzes Follow-up: Passt der vorgeschlagene Termin? Gern kurz bestätigen.` }
    case 'customers.timelineSummary':
      return { type: 'summary', summary: 'Letzte 30 Tage: Kickoff abgeschlossen, zwei Iterationen geliefert, Feedback positiv.' }
    case 'customers.risksBlockers':
      return { type: 'riskFlags', flags: ['Abhängigkeit von externer Freigabe', 'Urlaubszeit im Team'], severity: 'medium' }
    case 'customers.suggestTags':
      return { type: 'tags', tags: ['VIP', 'Renewal-Q1', 'Strategic'] }

    // Growth
    case 'growth.variants3':
      return { type: 'draft', draft: bullet(['Variante 1: Kurz & knackig', 'Variante 2: Vertrauensaufbau', 'Variante 3: Dringlichkeit'])) }
    case 'growth.hookImprove':
      return { type: 'draft', draft: 'Hook-Idee: Starte mit einem klaren Ergebnis und einer provozierenden Frage.' }
    case 'growth.ctaSuggestions':
      return { type: 'draft', draft: bullet(['CTA 1: Jetzt Demo sichern', 'CTA 2: Kurzes Beratungsgespräch buchen', 'CTA 3: Beispiel ansehen'])) }
    case 'growth.translate':
      return { type: 'draft', draft: 'English draft: Quick recap of the offer with a polite CTA to book a call.' }
    case 'growth.campaignPlan':
      return { type: 'plan', title: 'Newsletter Launch', steps: ['Zielgruppe definieren', 'Kernbotschaft schärfen', '3 Betreffzeilen testen', 'Rollout in Kalender einplanen'] }
    case 'growth.newsletterStart':
      return { type: 'plan', title: 'Kickoff Woche 1', steps: ['Willkommensmail', 'Story-Case teilen', 'Mini-CTA zum Termin'] }
    case 'growth.keywordCluster':
      return { type: 'tags', tags: ['ai automation', 'customer success', 'playbooks'] }

    // Storage
    case 'storage.summarize':
      return { type: 'summary', summary: `Memory: ${subject} – zentrales Learning zusammengefasst.` }
    case 'storage.extractFacts':
      return { type: 'extraction', fields: { datum: '2025-01-12', status: 'offen', owner: 'Team Inbox' } }
    case 'storage.saveAsMemory':
      return { type: 'classification', label: 'Memory gespeichert', confidence: 0.9 }
    case 'storage.suggestTags':
      return { type: 'tags', tags: ['memory', 'customer', 'follow-up'] }
    case 'storage.editMemory':
      return { type: 'summary', summary: 'Memory angepasst: Formulierung gestrafft und Quelle ergänzt.' }

    // Documents
    case 'documents.summarize':
      return { type: 'summary', summary: `Kurzfassung für "${subject}": Standardvertrag mit 12 Monaten Laufzeit, Kündigungsfrist 3 Monate.` }
    case 'documents.extractKeyFields':
      return { type: 'extraction', fields: { betrag: '1.200 EUR/Monat', laufzeit: '12 Monate', parteien: 'Acme Corp / Kunde' } }
    case 'documents.classify':
      return { type: 'classification', label: 'Vertrag', confidence: 0.78, details: 'Erfüllt Muster-Klauseln.' }
    case 'documents.suggestNextSteps':
      return { type: 'tasks', tasks: ['Unterschrift anfordern', 'Review durch Legal', 'Kunde über Fristen informieren'] }
    case 'documents.saveAsMemory':
      return { type: 'classification', label: 'Memory-Eintrag erzeugt', confidence: 0.88 }
    case 'documents.routeToCase':
      return { type: 'classification', label: 'Case #D-102 zugeordnet', confidence: 0.76 }
    default:
      return { type: 'summary', summary: fallbackText }
  }
}

