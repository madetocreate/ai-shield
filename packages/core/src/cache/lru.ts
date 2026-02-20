// ============================================================
// LRU Cache — O(1) scan result caching with TTL
// Uses Map insertion-order for LRU eviction
// ============================================================

export interface LRUCacheConfig {
  /** Maximum number of cached entries (default: 1000) */
  maxSize?: number;
  /** Time-to-live in milliseconds (default: 300_000 = 5 minutes) */
  ttlMs?: number;
}

interface CacheEntry<V> {
  value: V;
  expiresAt: number;
}

export class ScanLRUCache<V = unknown> {
  private cache = new Map<string, CacheEntry<V>>();
  private readonly maxSize: number;
  private readonly ttlMs: number;

  constructor(config: LRUCacheConfig = {}) {
    this.maxSize = config.maxSize ?? 1000;
    this.ttlMs = config.ttlMs ?? 300_000;
  }

  /** Get a cached value. Returns undefined on miss or expiry. Promotes to MRU on hit. */
  get(key: string): V | undefined {
    const entry = this.cache.get(key);
    if (!entry) return undefined;

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return undefined;
    }

    // Promote to most-recently-used (Map maintains insertion order)
    this.cache.delete(key);
    this.cache.set(key, entry);
    return entry.value;
  }

  /** Store a value. Evicts LRU entry if at capacity. */
  set(key: string, value: V): void {
    // Remove existing to update position
    this.cache.delete(key);

    // Evict oldest (first in Map) if at capacity
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value as string;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      value,
      expiresAt: Date.now() + this.ttlMs,
    });
  }

  /** Check if key exists and is not expired */
  has(key: string): boolean {
    return this.get(key) !== undefined;
  }

  /** Delete a specific key */
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  /** Clear all entries */
  clear(): void {
    this.cache.clear();
  }

  /** Current number of entries (may include expired) */
  get size(): number {
    return this.cache.size;
  }

  /** Remove all expired entries. Returns count of removed entries. */
  prune(): number {
    const now = Date.now();
    let removed = 0;
    for (const [key, entry] of this.cache) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
        removed++;
      }
    }
    return removed;
  }
}
