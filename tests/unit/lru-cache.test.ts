import { describe, it, expect, vi, beforeEach } from "vitest";
import { ScanLRUCache } from "../../packages/core/src/cache/lru.js";

describe("ScanLRUCache", () => {
  let cache: ScanLRUCache<string>;

  beforeEach(() => {
    cache = new ScanLRUCache({ maxSize: 3, ttlMs: 1000 });
  });

  // --- Basic get/set ---

  it("returns undefined on cache miss", () => {
    expect(cache.get("missing")).toBeUndefined();
  });

  it("stores and retrieves a value", () => {
    cache.set("key1", "value1");
    expect(cache.get("key1")).toBe("value1");
  });

  it("stores multiple values independently", () => {
    cache.set("a", "alpha");
    cache.set("b", "beta");
    expect(cache.get("a")).toBe("alpha");
    expect(cache.get("b")).toBe("beta");
  });

  it("overwrites existing key with new value", () => {
    cache.set("key", "first");
    cache.set("key", "second");
    expect(cache.get("key")).toBe("second");
  });

  // --- LRU eviction ---

  it("evicts least recently used entry when at capacity", () => {
    cache.set("a", "alpha");
    cache.set("b", "beta");
    cache.set("c", "gamma");
    // Capacity = 3, now add 4th entry → "a" should be evicted
    cache.set("d", "delta");
    expect(cache.get("a")).toBeUndefined();
    expect(cache.get("b")).toBe("beta");
    expect(cache.get("c")).toBe("gamma");
    expect(cache.get("d")).toBe("delta");
  });

  it("promotes accessed entry to MRU position", () => {
    cache.set("a", "alpha");
    cache.set("b", "beta");
    cache.set("c", "gamma");
    // Access "a" to promote it
    cache.get("a");
    // Now "b" is oldest — add new entry → "b" evicted
    cache.set("d", "delta");
    expect(cache.get("b")).toBeUndefined();
    expect(cache.get("a")).toBe("alpha");
  });

  it("reports correct size", () => {
    expect(cache.size).toBe(0);
    cache.set("a", "alpha");
    expect(cache.size).toBe(1);
    cache.set("b", "beta");
    expect(cache.size).toBe(2);
  });

  // --- TTL expiry ---

  it("returns undefined for expired entries", async () => {
    const shortCache = new ScanLRUCache<string>({ maxSize: 10, ttlMs: 10 });
    shortCache.set("key", "value");
    await new Promise((r) => setTimeout(r, 20));
    expect(shortCache.get("key")).toBeUndefined();
  });

  it("does not return expired entries from has()", async () => {
    const shortCache = new ScanLRUCache<string>({ maxSize: 10, ttlMs: 10 });
    shortCache.set("key", "value");
    await new Promise((r) => setTimeout(r, 20));
    expect(shortCache.has("key")).toBe(false);
  });

  it("prune() removes expired entries and returns count", async () => {
    const shortCache = new ScanLRUCache<string>({ maxSize: 10, ttlMs: 10 });
    shortCache.set("a", "alpha");
    shortCache.set("b", "beta");
    await new Promise((r) => setTimeout(r, 20));
    shortCache.set("c", "gamma"); // fresh entry
    const removed = shortCache.prune();
    expect(removed).toBe(2);
    expect(shortCache.size).toBe(1);
  });

  // --- delete / clear ---

  it("delete() removes a specific key", () => {
    cache.set("key", "value");
    expect(cache.delete("key")).toBe(true);
    expect(cache.get("key")).toBeUndefined();
  });

  it("delete() returns false for non-existent key", () => {
    expect(cache.delete("missing")).toBe(false);
  });

  it("clear() removes all entries", () => {
    cache.set("a", "alpha");
    cache.set("b", "beta");
    cache.clear();
    expect(cache.size).toBe(0);
    expect(cache.get("a")).toBeUndefined();
  });

  // --- defaults ---

  it("uses defaults when no config provided", () => {
    const defaultCache = new ScanLRUCache();
    defaultCache.set("x", "y");
    expect(defaultCache.get("x")).toBe("y");
    expect(defaultCache.size).toBe(1);
  });
});

// --- AIShield cache integration ---

describe("AIShield cache integration", () => {
  it("returns cached: false on first scan", async () => {
    const { AIShield } = await import("../../packages/core/src/index.js");
    const s = new AIShield({ cache: {} });
    const result = await s.scan("hello world");
    expect(result.meta.cached).toBe(false);
    await s.close();
  });

  it("returns cached: true on repeat scan", async () => {
    const { AIShield } = await import("../../packages/core/src/index.js");
    const s = new AIShield({ cache: {} });
    await s.scan("hello world");
    const cached = await s.scan("hello world");
    expect(cached.meta.cached).toBe(true);
    await s.close();
  });

  it("different inputs produce different cache entries", async () => {
    const { AIShield } = await import("../../packages/core/src/index.js");
    const s = new AIShield({ cache: {} });
    const r1 = await s.scan("input one");
    const r2 = await s.scan("input two");
    // Both miss cache on first scan
    expect(r1.meta.cached).toBe(false);
    expect(r2.meta.cached).toBe(false);
    // Second scan of "input one" hits cache
    const r1again = await s.scan("input one");
    expect(r1again.meta.cached).toBe(true);
    await s.close();
  });

  it("cacheSize reflects stored entries", async () => {
    const { AIShield } = await import("../../packages/core/src/index.js");
    const s = new AIShield({ cache: {} });
    expect(s.cacheSize).toBe(0);
    await s.scan("entry one");
    expect(s.cacheSize).toBe(1);
    await s.scan("entry two");
    expect(s.cacheSize).toBe(2);
    s.clearCache();
    expect(s.cacheSize).toBe(0);
    await s.close();
  });

  it("no cache when cache config not provided", async () => {
    const { AIShield } = await import("../../packages/core/src/index.js");
    const s = new AIShield();
    await s.scan("hello");
    const r2 = await s.scan("hello");
    expect(r2.meta.cached).toBe(false);
    await s.close();
  });

  it("different presets use different cache keys", async () => {
    const { AIShield } = await import("../../packages/core/src/index.js");
    const s = new AIShield({ cache: {} });
    const r1 = await s.scan("hello", { preset: "public_website" });
    const r2 = await s.scan("hello", { preset: "ops_agent" });
    // Should both be cache misses (different presets = different keys)
    expect(r1.meta.cached).toBe(false);
    expect(r2.meta.cached).toBe(false);
    await s.close();
  });
});
