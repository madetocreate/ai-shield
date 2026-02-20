# CLAUDE.md — AI Shield

## Project Overview

LLM Security Middleware SDK in TypeScript. Monorepo with 4 packages.

## Tech Stack

- TypeScript (strict), Node.js
- npm workspaces monorepo
- Vitest for testing
- Optional: ioredis, pg (peer dependencies)

## Packages

| Package | Path | Purpose |
|---------|------|---------|
| `@ai-shield/core` | `packages/core/` | Scanner chain, heuristic injection, PII, tool policy, cost, audit |
| `@ai-shield/openai` | `packages/openai/` | OpenAI SDK wrapper |
| `@ai-shield/anthropic` | `packages/anthropic/` | Anthropic SDK wrapper |
| `@ai-shield/middleware` | `packages/middleware/` | Express + Hono middleware |

## Commands

```bash
npm test                                    # 87 tests, <600ms
npm run build --workspaces                  # Build all packages
npm run typecheck --workspaces              # TypeCheck all packages
npx tsc -p packages/core/tsconfig.json      # Build single package
npx vitest run tests/unit/heuristic.test.ts # Run single test file
```

## Architecture

- Scanner Chain pattern: scanners run in sequence, early-exit on BLOCK
- Score-based injection detection (0.0-1.0), not binary
- PII: German/EU-first, validators (Luhn, IBAN Mod-97) for low false positives
- Tool Policy: wildcard matching, SHA-256 manifest pinning
- Cost: Redis-backed budget enforcement, in-memory fallback
- Audit: batched PostgreSQL writes, stores hashes not raw content (DSGVO)

## Key Files

- `packages/core/src/types.ts` — All shared types
- `packages/core/src/shield.ts` — Main AIShield class
- `packages/core/src/scanner/heuristic.ts` — 40+ injection patterns
- `packages/core/src/scanner/pii.ts` — PII detection with validators
- `packages/core/src/policy/tools.ts` — MCP tool permission enforcement
- `packages/core/src/cost/tracker.ts` — Budget enforcement

## Rules

- Zero runtime dependencies in core (everything optional via peer deps)
- TypeScript strict: noUncheckedIndexedAccess, noUnusedLocals, noUnusedParameters
- All scanners implement the `Scanner` interface from types.ts
- Tests must pass before any commit
- No secrets in code — use environment variables
