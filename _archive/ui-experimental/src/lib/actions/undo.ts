import type { ActionId, ActionTargetRef } from './types'

type UndoEntry = {
  id: string
  actionId: ActionId
  target: ActionTargetRef
  label: string
  undo: () => void
  createdAt: number
}

const stack = new Map<string, UndoEntry[]>()

const makeId = () => Math.random().toString(36).slice(2, 10)

export function pushUndo(entry: Omit<UndoEntry, 'id' | 'createdAt'>): string {
  const id = makeId()
  const targetId = entry.target.targetId || 'global'
  const list = stack.get(targetId) ?? []
  const full: UndoEntry = { ...entry, id, createdAt: Date.now() }
  stack.set(targetId, [full, ...list].slice(0, 20))
  return id
}

export function undoLast(target: ActionTargetRef): boolean {
  const key = target.targetId || 'global'
  const list = stack.get(key)
  if (!list || list.length === 0) return false
  const [entry, ...rest] = list
  entry.undo()
  stack.set(key, rest)
  return true
}

export function undoById(undoId: string): boolean {
  for (const [key, entries] of stack.entries()) {
    const idx = entries.findIndex((e) => e.id === undoId)
    if (idx >= 0) {
      const entry = entries[idx]
      entry.undo()
      const next = [...entries.slice(0, idx), ...entries.slice(idx + 1)]
      stack.set(key, next)
      return true
    }
  }
  return false
}

