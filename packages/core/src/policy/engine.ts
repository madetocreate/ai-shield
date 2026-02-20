import type { ScanDecision, PresetName, PIIAction } from "../types.js";

// ============================================================
// Policy Engine — Maps presets to scanner configurations
// 3 presets: public_website, internal_support, ops_agent
// ============================================================

export interface PolicyPreset {
  name: PresetName;
  injection: {
    threshold: number;
    action: ScanDecision;
  };
  pii: {
    action: PIIAction;
    emailAction: PIIAction;
    phoneAction: PIIAction;
    creditCardAction: PIIAction;
    ibanAction: PIIAction;
  };
  tools: {
    dangerousPatterns: string[];
    maxChainDepth: number;
  };
  cost: {
    defaultDailyBudget: number;
    warnAtPercent: number;
  };
}

const PRESETS: Record<PresetName, PolicyPreset> = {
  public_website: {
    name: "public_website",
    injection: {
      threshold: 0.25, // Strictest — public-facing
      action: "block",
    },
    pii: {
      action: "mask",
      emailAction: "mask",
      phoneAction: "mask",
      creditCardAction: "block",
      ibanAction: "block",
    },
    tools: {
      dangerousPatterns: [
        "delete_*",
        "remove_*",
        "drop_*",
        "destroy_*",
        "admin_*",
        "execute_*",
        "send_email",
        "payment_*",
        "transfer_*",
        "write_*",
        "create_*",
        "update_*",
      ],
      maxChainDepth: 3,
    },
    cost: {
      defaultDailyBudget: 10, // USD
      warnAtPercent: 80,
    },
  },

  internal_support: {
    name: "internal_support",
    injection: {
      threshold: 0.35, // Medium — trusted users
      action: "block",
    },
    pii: {
      action: "mask",
      emailAction: "mask",
      phoneAction: "mask",
      creditCardAction: "mask",
      ibanAction: "mask",
    },
    tools: {
      dangerousPatterns: [
        "delete_*",
        "remove_*",
        "drop_*",
        "destroy_*",
        "admin_*",
        "payment_*",
        "transfer_*",
      ],
      maxChainDepth: 5,
    },
    cost: {
      defaultDailyBudget: 50,
      warnAtPercent: 70,
    },
  },

  ops_agent: {
    name: "ops_agent",
    injection: {
      threshold: 0.5, // Relaxed — internal agents
      action: "warn",
    },
    pii: {
      action: "mask",
      emailAction: "allow",
      phoneAction: "allow",
      creditCardAction: "mask",
      ibanAction: "mask",
    },
    tools: {
      dangerousPatterns: ["drop_*", "destroy_*", "wipe_*", "shutdown_*"],
      maxChainDepth: 8,
    },
    cost: {
      defaultDailyBudget: 100,
      warnAtPercent: 60,
    },
  },
};

export class PolicyEngine {
  private preset: PolicyPreset;

  constructor(presetName: PresetName = "public_website") {
    this.preset = PRESETS[presetName];
  }

  getPreset(): PolicyPreset {
    return this.preset;
  }

  getInjectionThreshold(): number {
    return this.preset.injection.threshold;
  }

  getPIIAction(type?: string): PIIAction {
    if (!type) return this.preset.pii.action;
    const key = `${type}Action` as keyof PolicyPreset["pii"];
    return (this.preset.pii[key] as PIIAction | undefined) ?? this.preset.pii.action;
  }

  getDangerousToolPatterns(): string[] {
    return this.preset.tools.dangerousPatterns;
  }

  getMaxToolChainDepth(): number {
    return this.preset.tools.maxChainDepth;
  }

  getDailyBudget(): number {
    return this.preset.cost.defaultDailyBudget;
  }

  static getPresetNames(): PresetName[] {
    return Object.keys(PRESETS) as PresetName[];
  }

  static getPreset(name: PresetName): PolicyPreset {
    return PRESETS[name];
  }
}
