/**
 * AI Shield SDK - TypeScript SDK für AI Shield Agents API
 */

export interface AIShieldClientConfig {
  baseUrl?: string;
  apiKey?: string;
}

export class AIShieldClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(config: AIShieldClientConfig = {}) {
    this.baseUrl = config.baseUrl || 'http://localhost:8000';
    this.apiKey = config.apiKey;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: any
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Unauthorized');
      }
      throw new Error(`API Error: ${response.status} - ${await response.text()}`);
    }

    return response.json();
  }

  // Marketplace
  async searchAgents(params?: {
    query?: string;
    category?: string;
    minRating?: number;
  }): Promise<any[]> {
    const queryParams = new URLSearchParams();
    if (params?.query) queryParams.append('query', params.query);
    if (params?.category) queryParams.append('category', params.category);
    if (params?.minRating) queryParams.append('min_rating', params.minRating.toString());

    return this.request<any[]>(
      'GET',
      `/api/v1/marketplace/agents?${queryParams}`
    );
  }

  async installAgent(agentId: string, accountId: string): Promise<any> {
    return this.request('POST', `/api/v1/marketplace/agents/${agentId}/install`, {
      account_id: accountId,
    });
  }

  // Analytics
  async trackMetric(
    metricName: string,
    value: number,
    metadata?: Record<string, any>
  ): Promise<any> {
    return this.request('POST', '/api/v1/analytics/track', {
      metric_name: metricName,
      value,
      metadata: metadata || {},
    });
  }

  async getInsights(metricName: string): Promise<any> {
    return this.request('GET', `/api/v1/analytics/insights/${metricName}`);
  }

  // Configuration
  async isFeatureEnabled(
    featureName: string,
    accountId?: string
  ): Promise<boolean> {
    const params = accountId ? `?account_id=${accountId}` : '';
    const result = await this.request<{ enabled: boolean }>(
      'GET',
      `/api/v1/config/features/${featureName}/check${params}`
    );
    return result.enabled;
  }

  // Webhooks
  async createWebhook(
    url: string,
    events: string[],
    secret?: string
  ): Promise<any> {
    return this.request('POST', '/api/v1/webhooks', {
      url,
      events,
      secret,
    });
  }

  // Costs
  async trackCost(
    accountId: string,
    costType: string,
    amount: number,
    agentName?: string
  ): Promise<any> {
    return this.request('POST', '/api/v1/costs/track', {
      account_id: accountId,
      cost_type: costType,
      amount,
      agent_name: agentName,
    });
  }

  async getCosts(accountId: string, period: string = 'monthly'): Promise<any> {
    return this.request('GET', `/api/v1/costs/${accountId}?period=${period}`);
  }

  // Export
  async exportAgents(format: string = 'json'): Promise<string> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/export/agents?format=${format}`,
      {
        headers: this.apiKey
          ? { Authorization: `Bearer ${this.apiKey}` }
          : {},
      }
    );
    return response.text();
  }
}
