import type { Scanner, ScanResult, ScanContext, ScanDecision } from "../types.js";

// ============================================================
// Scanner Chain — Orchestrates all scanners in sequence
// Early-exit on BLOCK, collects all violations
// ============================================================

export interface ChainConfig {
  /** Stop chain on first BLOCK result */
  earlyExit?: boolean;
}

export class ScannerChain {
  private scanners: Scanner[] = [];
  private earlyExit: boolean;

  constructor(config: ChainConfig = {}) {
    this.earlyExit = config.earlyExit ?? true;
  }

  /** Add scanner to the chain */
  add(scanner: Scanner): this {
    this.scanners.push(scanner);
    return this;
  }

  /** Run all scanners in sequence */
  async run(input: string, context: ScanContext = {}): Promise<ScanResult> {
    const chainStart = performance.now();
    let highestDecision: ScanDecision = "allow";
    let sanitized = input;
    const allViolations: ScanResult["violations"] = [];
    const scannersRun: string[] = [];

    for (const scanner of this.scanners) {
      const result = await scanner.scan(sanitized, context);
      scannersRun.push(scanner.name);

      // Collect violations
      allViolations.push(...result.violations);

      // Update sanitized text if scanner modified it
      if (result.sanitized !== undefined) {
        sanitized = result.sanitized;
      }

      // Escalate decision (allow < warn < block)
      if (decisionPriority(result.decision) > decisionPriority(highestDecision)) {
        highestDecision = result.decision;
      }

      // Early exit on block
      if (this.earlyExit && highestDecision === "block") {
        break;
      }
    }

    const totalDuration = performance.now() - chainStart;

    return {
      safe: highestDecision === "allow",
      decision: highestDecision,
      sanitized,
      violations: allViolations,
      meta: {
        scanDurationMs: totalDuration,
        scannersRun,
        cached: false,
      },
    };
  }

  /** Get scanner count */
  get length(): number {
    return this.scanners.length;
  }
}

function decisionPriority(d: ScanDecision): number {
  switch (d) {
    case "allow":
      return 0;
    case "warn":
      return 1;
    case "block":
      return 2;
  }
}
