import type { ActionRunResult, IdempotencyKey } from './types'

type CacheEntry = {
  result: ActionRunResult
  expiresAt: number
}

const store = new Map<IdempotencyKey, CacheEntry>()
const DEFAULT_TTL_MS = 1000 * 60 * 5 // 5 Minuten

export function setCache(key: IdempotencyKey, result: ActionRunResult, ttlMs: number = DEFAULT_TTL_MS) {
  store.set(key, { result, expiresAt: Date.now() + ttlMs })
}

export function getCache(key: IdempotencyKey): ActionRunResult | null {
  const entry = store.get(key)
  if (!entry) return null
  if (Date.now() > entry.expiresAt) {
    store.delete(key)
    return null
  }
  return entry.result
}

export function invalidateCache(key: IdempotencyKey) {
  store.delete(key)
}

export function clearCache() {
  store.clear()
}

