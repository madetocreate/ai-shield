// ============================================================
// @ai-shield/middleware — Public API
// ============================================================

// Shared types and utilities
export { defaultGetInput, defaultBlockedResponse } from "./shared.js";
export type { ShieldMiddlewareConfig } from "./shared.js";

// Framework-specific exports
export { shieldMiddleware as expressShield } from "./express.js";
export { shieldMiddleware as honoShield } from "./hono.js";

export type { ScanResult } from "@ai-shield/core";
