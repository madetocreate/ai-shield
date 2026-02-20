import type { AIShield, ShieldConfig, ScanContext, ScanResult } from "@ai-shield/core";

// ============================================================
// Anthropic Shield Wrapper — Drop-in replacement
// Wraps Anthropic SDK, scans input before & output after
// ============================================================

export interface ShieldedAnthropicConfig {
  /** AI Shield config */
  shield?: ShieldConfig;
  /** Pre-created AIShield instance */
  shieldInstance?: AIShield;
  /** Agent ID for tool policy / cost tracking */
  agentId?: string;
  /** Custom scan context factory */
  contextFactory?: (messages: AnthropicMessage[]) => ScanContext;
  /** Whether to scan output too — default: false */
  scanOutput?: boolean;
  /** Callback when input is blocked */
  onBlocked?: (result: ScanResult, messages: AnthropicMessage[]) => void;
  /** Callback when input has warnings */
  onWarning?: (result: ScanResult, messages: AnthropicMessage[]) => void;
}

// --- Anthropic SDK types (minimal, avoids hard dependency) ---

interface ContentBlockText {
  type: "text";
  text: string;
}

interface ContentBlockToolUse {
  type: "tool_use";
  id: string;
  name: string;
  input: Record<string, unknown>;
}

type ContentBlock = ContentBlockText | ContentBlockToolUse | { type: string; [key: string]: unknown };

export interface AnthropicMessage {
  role: "user" | "assistant";
  content: string | ContentBlock[];
}

interface AnthropicTool {
  name: string;
  description?: string;
  input_schema: Record<string, unknown>;
}

export interface AnthropicCreateParams {
  model: string;
  messages: AnthropicMessage[];
  system?: string | Array<{ type: "text"; text: string }>;
  max_tokens: number;
  tools?: AnthropicTool[];
  stream?: boolean;
  [key: string]: unknown;
}

interface AnthropicResponse {
  content: ContentBlock[];
  model: string;
  stop_reason: string | null;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
}

interface AnthropicLike {
  messages: {
    create(params: AnthropicCreateParams): Promise<AnthropicResponse>;
  };
}

export class ShieldedAnthropic {
  private client: AnthropicLike;
  private shield: AIShield | null = null;
  private shieldConfig: ShieldConfig;
  private config: ShieldedAnthropicConfig;
  private _shieldReady: Promise<AIShield> | null = null;

  constructor(client: AnthropicLike, config: ShieldedAnthropicConfig = {}) {
    this.client = client;
    this.config = config;
    this.shieldConfig = config.shield ?? {};

    if (config.shieldInstance) {
      this.shield = config.shieldInstance;
    }
  }

  /** Lazy-init shield */
  private async getShield(): Promise<AIShield> {
    if (this.shield) return this.shield;
    if (this._shieldReady) return this._shieldReady;

    this._shieldReady = import("@ai-shield/core").then((mod) => {
      this.shield = new mod.AIShield(this.shieldConfig);
      return this.shield;
    });

    return this._shieldReady;
  }

  /** Build scan context from params */
  private buildContext(params: AnthropicCreateParams): ScanContext {
    if (this.config.contextFactory) {
      return this.config.contextFactory(params.messages);
    }

    const context: ScanContext = {};
    if (this.config.agentId) {
      context.agentId = this.config.agentId;
    }

    // Include tool names if tools are declared
    if (params.tools) {
      context.tools = params.tools.map((t) => ({ name: t.name }));
    }

    return context;
  }

  /** Extract text content from user messages */
  private extractUserContent(messages: AnthropicMessage[]): string {
    const parts: string[] = [];

    for (const msg of messages) {
      if (msg.role !== "user") continue;

      if (typeof msg.content === "string") {
        parts.push(msg.content);
      } else if (Array.isArray(msg.content)) {
        for (const block of msg.content) {
          if (block.type === "text" && "text" in block) {
            parts.push((block as ContentBlockText).text);
          }
        }
      }
    }

    return parts.join("\n");
  }

  /** Extract text from response content blocks */
  private extractResponseText(content: ContentBlock[]): string {
    return content
      .filter((b): b is ContentBlockText => b.type === "text")
      .map((b) => b.text)
      .join("\n");
  }

  /** Create message with Shield protection */
  async createMessage(
    params: AnthropicCreateParams,
  ): Promise<AnthropicResponse & { _shield?: { input: ScanResult; output?: ScanResult } }> {
    const shieldInstance = await this.getShield();
    const context = this.buildContext(params);

    // --- Scan user input ---
    const userContent = this.extractUserContent(params.messages);
    const inputResult = await shieldInstance.scan(userContent, context);

    if (inputResult.decision === "block") {
      this.config.onBlocked?.(inputResult, params.messages);
      throw new ShieldBlockError("Input blocked by AI Shield", inputResult);
    }

    if (inputResult.decision === "warn") {
      this.config.onWarning?.(inputResult, params.messages);
    }

    // --- Also scan system prompt if present ---
    if (params.system) {
      const systemText = typeof params.system === "string"
        ? params.system
        : params.system.map((b) => b.text).join("\n");

      // System prompt scan is informational only (don't block our own system prompt)
      // But DO scan it for PII leaks
      await shieldInstance.scan(systemText, { ...context, preset: "ops_agent" });
    }

    // --- Replace sanitized content if PII was masked ---
    let finalParams = params;
    if (inputResult.sanitized !== userContent) {
      finalParams = this.replaceUserContent(params, inputResult.sanitized);
    }

    // --- Cost pre-check ---
    if (this.config.agentId) {
      const estimate = await shieldInstance.checkBudget(
        this.config.agentId,
        params.model,
        userContent.length * 0.75, // rough token estimate
      );
      if (!estimate.allowed) {
        throw new ShieldBudgetError(
          `Budget exceeded: $${estimate.currentSpend.toFixed(4)} / $${(estimate.currentSpend + estimate.remainingBudget).toFixed(4)}`,
          estimate,
        );
      }
    }

    // --- Make the actual API call ---
    const response = await this.client.messages.create(finalParams);

    // --- Record actual cost ---
    if (this.config.agentId && response.usage) {
      await shieldInstance.recordCost(
        this.config.agentId,
        params.model,
        response.usage.input_tokens,
        response.usage.output_tokens,
      );
    }

    // --- Scan output ---
    let outputResult: ScanResult | undefined;
    if (this.config.scanOutput) {
      const outputText = this.extractResponseText(response.content);
      if (outputText) {
        outputResult = await shieldInstance.scan(outputText, context);
      }
    }

    return {
      ...response,
      _shield: { input: inputResult, output: outputResult },
    };
  }

  /** Replace user content with sanitized version */
  private replaceUserContent(
    params: AnthropicCreateParams,
    sanitized: string,
  ): AnthropicCreateParams {
    const messages = params.messages.map((msg) => {
      if (msg.role !== "user") return msg;

      if (typeof msg.content === "string") {
        return { ...msg, content: sanitized };
      }

      // Multi-block: replace text blocks
      if (Array.isArray(msg.content)) {
        let remaining = sanitized;
        const newContent = msg.content.map((block) => {
          if (block.type === "text" && "text" in block) {
            const original = (block as ContentBlockText).text;
            const replacement = remaining.substring(0, original.length);
            remaining = remaining.substring(original.length + 1);
            return { ...block, text: replacement };
          }
          return block;
        });
        return { ...msg, content: newContent };
      }

      return msg;
    });

    return { ...params, messages };
  }

  /** Access underlying Anthropic client */
  get raw(): AnthropicLike {
    return this.client;
  }

  /** Graceful shutdown */
  async close(): Promise<void> {
    if (this.shield) {
      await this.shield.close();
    }
  }
}

// --- Error types ---

export class ShieldBlockError extends Error {
  constructor(
    message: string,
    public readonly scanResult: ScanResult,
  ) {
    super(message);
    this.name = "ShieldBlockError";
  }
}

export class ShieldBudgetError extends Error {
  constructor(
    message: string,
    public readonly budgetCheck: { allowed: boolean; currentSpend: number; remainingBudget: number },
  ) {
    super(message);
    this.name = "ShieldBudgetError";
  }
}
