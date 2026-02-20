import { createHash } from "node:crypto";
import type {
  Scanner,
  ScannerResult,
  ScanContext,
  Violation,
  ToolCall,
  ToolPermissions,
  ToolPolicy,
  ToolManifestPin,
} from "../types.js";

// ============================================================
// Tool Policy Scanner — MCP Tool Permission Enforcement
// Validates: permissions, rate limits, manifest integrity
// ============================================================

export class ToolPolicyScanner implements Scanner {
  readonly name = "tool_policy";
  private policy: ToolPolicy;
  private pins: Map<string, ToolManifestPin>;

  constructor(policy: ToolPolicy, pins: ToolManifestPin[] = []) {
    this.policy = policy;
    this.pins = new Map(pins.map((p) => [p.serverId, p]));
  }

  async scan(_input: string, context: ScanContext): Promise<ScannerResult> {
    const start = performance.now();
    const violations: Violation[] = [];

    if (!context.tools || context.tools.length === 0) {
      return { decision: "allow", violations: [], durationMs: performance.now() - start };
    }

    const agentId = context.agentId ?? "default";
    const permissions = this.policy.permissions[agentId];

    for (const tool of context.tools) {
      // Check global dangerous patterns
      if (this.isGloballyDangerous(tool.name)) {
        violations.push({
          type: "tool_denied",
          scanner: this.name,
          score: 1.0,
          threshold: 0,
          message: `Tool '${tool.name}' matches global dangerous pattern`,
          detail: "Matched global.dangerousPatterns",
        });
        continue;
      }

      // Check read-only mode
      if (this.policy.global?.readOnlyMode) {
        violations.push({
          type: "tool_denied",
          scanner: this.name,
          score: 1.0,
          threshold: 0,
          message: `Tool '${tool.name}' blocked: read-only mode active`,
        });
        continue;
      }

      // Check agent-specific permissions
      if (permissions) {
        const denied = this.isDenied(tool.name, permissions);
        if (denied) {
          violations.push({
            type: "tool_denied",
            scanner: this.name,
            score: 1.0,
            threshold: 0,
            message: `Tool '${tool.name}' denied for agent '${agentId}'`,
            detail: `Matched deny pattern: ${denied}`,
          });
          continue;
        }

        const allowed = this.isAllowed(tool.name, permissions);
        if (!allowed) {
          violations.push({
            type: "tool_denied",
            scanner: this.name,
            score: 1.0,
            threshold: 0,
            message: `Tool '${tool.name}' not in allow list for agent '${agentId}'`,
          });
        }
      }

      // Check manifest pin integrity
      if (tool.serverId) {
        const driftViolation = this.checkManifestDrift(tool);
        if (driftViolation) violations.push(driftViolation);
      }
    }

    const decision = violations.length > 0 ? "block" : "allow";
    return { decision, violations, durationMs: performance.now() - start };
  }

  /** Check if tool matches global dangerous patterns */
  private isGloballyDangerous(toolName: string): boolean {
    const patterns = this.policy.global?.dangerousPatterns ?? [];
    return patterns.some((p) => matchWildcard(p, toolName));
  }

  /** Check if tool is explicitly denied */
  private isDenied(
    toolName: string,
    permissions: ToolPermissions,
  ): string | null {
    if (!permissions.denied) return null;
    for (const pattern of permissions.denied) {
      if (matchWildcard(pattern, toolName)) return pattern;
    }
    return null;
  }

  /** Check if tool is in the allow list */
  private isAllowed(toolName: string, permissions: ToolPermissions): boolean {
    return permissions.allowed.some((p) => matchWildcard(p, toolName));
  }

  /** Check manifest pin for drift */
  private checkManifestDrift(tool: ToolCall): Violation | null {
    if (!tool.serverId) return null;
    const pin = this.pins.get(tool.serverId);
    if (!pin) return null;

    if (!pin.knownTools.includes(tool.name)) {
      return {
        type: "manifest_drift",
        scanner: this.name,
        score: 1.0,
        threshold: 0,
        message: `Tool '${tool.name}' not in pinned manifest for server '${tool.serverId}'`,
        detail: `Known tools: ${pin.knownTools.join(", ")}`,
      };
    }
    return null;
  }

  /** Pin a server's tool manifest */
  static pinManifest(serverId: string, toolNames: string[]): ToolManifestPin {
    const sorted = [...toolNames].sort();
    const hash = createHash("sha256").update(sorted.join(",")).digest("hex");

    return {
      serverId,
      toolsHash: hash,
      toolCount: toolNames.length,
      knownTools: sorted,
      pinnedAt: new Date(),
    };
  }

  /** Verify a manifest against a pin */
  static verifyManifest(
    pin: ToolManifestPin,
    currentTools: string[],
  ): { valid: boolean; added: string[]; removed: string[] } {
    const sorted = [...currentTools].sort();
    const hash = createHash("sha256").update(sorted.join(",")).digest("hex");

    if (hash === pin.toolsHash) {
      return { valid: true, added: [], removed: [] };
    }

    const current = new Set(sorted);
    const pinned = new Set(pin.knownTools);
    const added = sorted.filter((t) => !pinned.has(t));
    const removed = pin.knownTools.filter((t) => !current.has(t));

    return { valid: false, added, removed };
  }
}

/** Match wildcard pattern (e.g., "delete_*" matches "delete_user") */
function matchWildcard(pattern: string, value: string): boolean {
  if (pattern === "*") return true;
  if (!pattern.includes("*")) return pattern === value;

  const regex = new RegExp(
    "^" + pattern.replace(/\*/g, ".*").replace(/\?/g, ".") + "$",
  );
  return regex.test(value);
}
