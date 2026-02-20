import type { AIShield, ShieldConfig, ScanContext, ScanResult } from "@ai-shield/core";

// ============================================================
// OpenAI Shield Wrapper — Drop-in replacement
// Wraps OpenAI SDK, scans input before & output after LLM call
// ============================================================

export interface ShieldedOpenAIConfig {
  /** AI Shield config (or pass existing AIShield instance) */
  shield?: ShieldConfig;
  /** Pre-created AIShield instance (takes precedence over shield config) */
  shieldInstance?: AIShield;
  /** Agent ID for tool policy / cost tracking */
  agentId?: string;
  /** Custom scan context factory */
  contextFactory?: (messages: ChatMessage[]) => ScanContext;
  /** Whether to scan output (response) too — default: false */
  scanOutput?: boolean;
  /** Callback when input is blocked */
  onBlocked?: (result: ScanResult, messages: ChatMessage[]) => void;
  /** Callback when input has warnings */
  onWarning?: (result: ScanResult, messages: ChatMessage[]) => void;
}

interface ChatMessage {
  role: string;
  content: string | null | Array<{ type: string; text?: string }>;
  tool_calls?: Array<{ function: { name: string; arguments: string } }>;
}

interface ChatCompletionParams {
  model: string;
  messages: ChatMessage[];
  tools?: Array<{ function: { name: string } }>;
  stream?: boolean;
  [key: string]: unknown;
}

interface ChatCompletion {
  choices: Array<{
    message: {
      content: string | null;
      tool_calls?: Array<{ function: { name: string; arguments: string } }>;
    };
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface OpenAILike {
  chat: {
    completions: {
      create(params: ChatCompletionParams): Promise<ChatCompletion>;
    };
  };
}

export class ShieldedOpenAI {
  private client: OpenAILike;
  private shield: AIShield | null = null;
  private shieldConfig: ShieldConfig;
  private config: ShieldedOpenAIConfig;
  private _shieldReady: Promise<AIShield> | null = null;

  constructor(client: OpenAILike, config: ShieldedOpenAIConfig = {}) {
    this.client = client;
    this.config = config;
    this.shieldConfig = config.shield ?? {};

    if (config.shieldInstance) {
      this.shield = config.shieldInstance;
    }
  }

  /** Lazy-init shield (avoid import at construction time) */
  private async getShield(): Promise<AIShield> {
    if (this.shield) return this.shield;
    if (this._shieldReady) return this._shieldReady;

    this._shieldReady = import("@ai-shield/core").then((mod) => {
      this.shield = new mod.AIShield(this.shieldConfig);
      return this.shield;
    });

    return this._shieldReady;
  }

  /** Build scan context from messages */
  private buildContext(params: ChatCompletionParams): ScanContext {
    if (this.config.contextFactory) {
      return this.config.contextFactory(params.messages);
    }

    const context: ScanContext = {};
    if (this.config.agentId) {
      context.agentId = this.config.agentId;
    }

    // Include tool names if tools are being called
    if (params.tools) {
      context.tools = params.tools.map((t) => ({ name: t.function.name }));
    }

    return context;
  }

  /** Extract text content from messages for scanning */
  private extractUserContent(messages: ChatMessage[]): string {
    const parts: string[] = [];

    for (const msg of messages) {
      // Only scan user messages (not system/assistant)
      if (msg.role !== "user") continue;

      if (typeof msg.content === "string") {
        parts.push(msg.content);
      } else if (Array.isArray(msg.content)) {
        for (const block of msg.content) {
          if (block.type === "text" && block.text) {
            parts.push(block.text);
          }
        }
      }
    }

    return parts.join("\n");
  }

  /** Create chat completion with Shield protection */
  async createChatCompletion(
    params: ChatCompletionParams,
  ): Promise<ChatCompletion & { _shield?: { input: ScanResult; output?: ScanResult } }> {
    const shieldInstance = await this.getShield();
    const context = this.buildContext(params);
    const userContent = this.extractUserContent(params.messages);

    // --- Scan input ---
    const inputResult = await shieldInstance.scan(userContent, context);

    if (inputResult.decision === "block") {
      this.config.onBlocked?.(inputResult, params.messages);
      throw new ShieldBlockError(
        "Input blocked by AI Shield",
        inputResult,
      );
    }

    if (inputResult.decision === "warn") {
      this.config.onWarning?.(inputResult, params.messages);
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
    const response = await this.client.chat.completions.create(finalParams);

    // --- Record cost ---
    if (this.config.agentId && response.usage) {
      await shieldInstance.recordCost(
        this.config.agentId,
        params.model,
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
      );
    }

    // --- Scan output ---
    let outputResult: ScanResult | undefined;
    if (this.config.scanOutput) {
      const outputText = response.choices[0]?.message?.content ?? "";
      if (outputText) {
        outputResult = await shieldInstance.scan(outputText, context);
      }
    }

    return {
      ...response,
      _shield: { input: inputResult, output: outputResult },
    };
  }

  /** Replace user message content with sanitized version */
  private replaceUserContent(
    params: ChatCompletionParams,
    sanitized: string,
  ): ChatCompletionParams {
    const messages = params.messages.map((msg) => {
      if (msg.role !== "user") return msg;

      if (typeof msg.content === "string") {
        return { ...msg, content: sanitized };
      }
      // For multi-part content, replace text blocks
      if (Array.isArray(msg.content)) {
        let remaining = sanitized;
        const newContent = msg.content.map((block) => {
          if (block.type === "text" && block.text) {
            const replacement = remaining.substring(0, block.text.length);
            remaining = remaining.substring(block.text.length + 1); // +1 for \n
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

  /** Access the underlying OpenAI client */
  get raw(): OpenAILike {
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
