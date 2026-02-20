import type {
  BudgetConfig,
  BudgetCheckResult,
  BudgetPeriod,
  CostRecord,
} from "../types.js";
import { estimateCost } from "./pricing.js";

// ============================================================
// Cost Tracker — Token counting + budget enforcement
// Uses Redis for distributed budget tracking (optional)
// Falls back to in-memory for standalone use
// ============================================================

/** Minimal Redis interface (compatible with ioredis) */
export interface RedisLike {
  get(key: string): Promise<string | null>;
  incrbyfloat(key: string, increment: number): Promise<string>;
  expire(key: string, seconds: number): Promise<number>;
}

/** In-memory fallback store */
class MemoryStore implements RedisLike {
  private data = new Map<string, { value: string; expiresAt?: number }>();

  async get(key: string): Promise<string | null> {
    const entry = this.data.get(key);
    if (!entry) return null;
    if (entry.expiresAt && Date.now() > entry.expiresAt) {
      this.data.delete(key);
      return null;
    }
    return entry.value;
  }

  async incrbyfloat(key: string, increment: number): Promise<string> {
    const current = parseFloat((await this.get(key)) ?? "0");
    const newValue = (current + increment).toString();
    const entry = this.data.get(key);
    this.data.set(key, { value: newValue, expiresAt: entry?.expiresAt });
    return newValue;
  }

  async expire(key: string, seconds: number): Promise<number> {
    const entry = this.data.get(key);
    if (!entry) return 0;
    entry.expiresAt = Date.now() + seconds * 1000;
    return 1;
  }
}

export class CostTracker {
  private store: RedisLike;
  private budgets: Map<string, BudgetConfig>;
  private records: CostRecord[] = [];

  constructor(
    budgets: Record<string, BudgetConfig> = {},
    redis?: RedisLike,
  ) {
    this.store = redis ?? new MemoryStore();
    this.budgets = new Map(Object.entries(budgets));
  }

  /** Check if a request is within budget BEFORE sending to LLM */
  async checkBudget(
    entityId: string,
    model: string,
    estimatedInputTokens: number,
    estimatedOutputTokens: number = 500,
  ): Promise<BudgetCheckResult> {
    const budget = this.budgets.get(entityId);
    if (!budget) {
      return { allowed: true, currentSpend: 0, remainingBudget: Infinity };
    }

    const estimated = estimateCost(model, estimatedInputTokens, estimatedOutputTokens);
    const key = this.budgetKey(entityId, budget.period);
    const currentSpend = parseFloat((await this.store.get(key)) ?? "0");

    if (currentSpend + estimated > budget.hardLimit) {
      return {
        allowed: false,
        currentSpend,
        remainingBudget: Math.max(0, budget.hardLimit - currentSpend),
        warning: `Hard budget limit reached: $${currentSpend.toFixed(2)} / $${budget.hardLimit}`,
      };
    }

    const warning =
      currentSpend + estimated > budget.softLimit
        ? `Approaching budget: $${currentSpend.toFixed(2)} / $${budget.hardLimit} (${Math.round((currentSpend / budget.hardLimit) * 100)}%)`
        : undefined;

    return {
      allowed: true,
      currentSpend,
      remainingBudget: budget.hardLimit - currentSpend,
      warning,
    };
  }

  /** Record actual cost AFTER receiving response */
  async recordCost(
    entityId: string,
    model: string,
    inputTokens: number,
    outputTokens: number,
  ): Promise<CostRecord> {
    const cost = estimateCost(model, inputTokens, outputTokens);
    const record: CostRecord = {
      entityId,
      model,
      inputTokens,
      outputTokens,
      cost,
      timestamp: new Date(),
    };

    // Update budget counter
    const budget = this.budgets.get(entityId);
    if (budget) {
      const key = this.budgetKey(entityId, budget.period);
      await this.store.incrbyfloat(key, cost);
      await this.store.expire(key, this.periodSeconds(budget.period) * 2);
    }

    // Also update any matching broader budgets (global, etc.)
    const globalBudget = this.budgets.get("global");
    if (globalBudget && entityId !== "global") {
      const globalKey = this.budgetKey("global", globalBudget.period);
      await this.store.incrbyfloat(globalKey, cost);
      await this.store.expire(globalKey, this.periodSeconds(globalBudget.period) * 2);
    }

    this.records.push(record);
    return record;
  }

  /** Get current spend for an entity */
  async getCurrentSpend(entityId: string): Promise<number> {
    const budget = this.budgets.get(entityId);
    if (!budget) return 0;
    const key = this.budgetKey(entityId, budget.period);
    return parseFloat((await this.store.get(key)) ?? "0");
  }

  /** Get all recorded costs (for export/audit) */
  getRecords(): CostRecord[] {
    return [...this.records];
  }

  private budgetKey(entityId: string, period: BudgetPeriod): string {
    const now = new Date();
    let periodKey: string;

    switch (period) {
      case "hourly":
        periodKey = `${now.getUTCFullYear()}-${now.getUTCMonth()}-${now.getUTCDate()}-${now.getUTCHours()}`;
        break;
      case "daily":
        periodKey = `${now.getUTCFullYear()}-${now.getUTCMonth()}-${now.getUTCDate()}`;
        break;
      case "monthly":
        periodKey = `${now.getUTCFullYear()}-${now.getUTCMonth()}`;
        break;
    }

    return `ai-shield:cost:${entityId}:${periodKey}`;
  }

  private periodSeconds(period: BudgetPeriod): number {
    switch (period) {
      case "hourly":
        return 3600;
      case "daily":
        return 86400;
      case "monthly":
        return 86400 * 31;
    }
  }
}
