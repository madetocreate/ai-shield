"use client";

import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

interface Connection {
  tenant_id: string;
  provider: string;
  status: "connected" | "disconnected" | "pending" | "error";
  nango_connection_id?: string;
  scopes: string[];
  auth_url?: string;
  created_at?: string;
  updated_at?: string;
}

interface ProviderInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

const PROVIDERS: ProviderInfo[] = [
  {
    id: "google",
    name: "Google Calendar",
    description: "Kalender-Events lesen und erstellen",
    icon: "📅",
    color: "bg-blue-50 border-blue-200",
  },
  {
    id: "shopify",
    name: "Shopify",
    description: "Bestellungen und Kunden verwalten",
    icon: "🛒",
    color: "bg-green-50 border-green-200",
  },
  {
    id: "woocommerce",
    name: "WooCommerce",
    description: "WooCommerce Bestellungen verwalten",
    icon: "🛍️",
    color: "bg-purple-50 border-purple-200",
  },
  {
    id: "whatsapp",
    name: "WhatsApp Business",
    description: "Nachrichten senden und empfangen",
    icon: "💬",
    color: "bg-green-50 border-green-200",
  },
];

const API_BASE_URL = process.env.NEXT_PUBLIC_CONTROL_PLANE_URL || "http://localhost:4051";

export default function IntegrationsDashboard() {
  const { t } = useTranslation();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tenantId] = useState("default-tenant"); // TODO: Get from context/auth

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/v1/integrations/`, {
        headers: {
          "x-tenant-id": tenantId,
          "x-ai-shield-admin-key": process.env.NEXT_PUBLIC_ADMIN_KEY || "",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load connections: ${response.statusText}`);
      }

      const data = await response.json();
      setConnections(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      console.error("Failed to load connections:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (provider: string) => {
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/v1/integrations/${provider}/connect`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-ai-shield-admin-key": process.env.NEXT_PUBLIC_ADMIN_KEY || "",
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          provider: provider,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to initiate connection: ${response.statusText}`);
      }

      const data = await response.json();
      
      // If auth_url is provided, redirect user
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        // Reload connections
        await loadConnections();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect");
      console.error("Failed to connect:", err);
    }
  };

  const handleDisconnect = async (provider: string) => {
    if (!confirm(`Möchten Sie ${provider} wirklich trennen?`)) {
      return;
    }

    try {
      setError(null);
      const response = await fetch(
        `${API_BASE_URL}/v1/integrations/${provider}/disconnect?tenant_id=${tenantId}`,
        {
          method: "POST",
          headers: {
            "x-ai-shield-admin-key": process.env.NEXT_PUBLIC_ADMIN_KEY || "",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to disconnect: ${response.statusText}`);
      }

      await loadConnections();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to disconnect");
      console.error("Failed to disconnect:", err);
    }
  };

  const getConnectionStatus = (provider: string): Connection | undefined => {
    return connections.find((c) => c.provider === provider);
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      connected: "bg-green-100 text-green-800 border-green-200",
      disconnected: "bg-gray-100 text-gray-800 border-gray-200",
      pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
      error: "bg-red-100 text-red-800 border-red-200",
    };

    const labels = {
      connected: t('integrations.statusConnected'),
      disconnected: t('integrations.statusDisconnected'),
      pending: t('integrations.statusPending'),
      error: t('common.error'),
    };

    return (
      <span
        className={`px-2 py-1 text-xs font-medium rounded border ${styles[status as keyof typeof styles] || styles.disconnected}`}
      >
        {labels[status as keyof typeof labels] || status}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6 text-[var(--color-text-primary)]">{t('integrations.title')}</h1>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)] mx-auto"></div>
          <p className="mt-4 text-[var(--color-text-secondary)]">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2 text-[var(--color-text-primary)]">{t('integrations.title')}</h1>
        <p className="text-[var(--color-text-secondary)]">
          {t('integrations.description')}
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-[var(--color-error-light)] border border-[var(--color-error)] rounded-lg text-[var(--color-error-dark)]">
          <strong>{t('common.error')}:</strong> {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {PROVIDERS.map((provider) => {
          const connection = getConnectionStatus(provider.id);
          const isConnected = connection?.status === "connected";

          return (
            <div
              key={provider.id}
              className={`p-6 rounded-lg border-2 ${provider.color} transition-shadow hover:shadow-lg`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{provider.icon}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">{provider.name}</h3>
                    <p className="text-sm text-[var(--color-text-secondary)]">{provider.description}</p>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                {getStatusBadge(connection?.status || "disconnected")}
                {connection?.scopes && connection.scopes.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-[var(--color-text-secondary)] mb-1">{t('integrations.permissions')}:</p>
                    <div className="flex flex-wrap gap-1">
                      {connection.scopes.map((scope, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 text-xs bg-[var(--color-surface-elevated)] rounded border border-[var(--color-border)] text-[var(--color-text-primary)]"
                        >
                          {scope}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                {isConnected ? (
                  <button
                    onClick={() => handleDisconnect(provider.id)}
                    className="flex-1 px-4 py-2 bg-[var(--color-error)] text-white rounded hover:bg-[var(--color-error-dark)] transition-colors"
                  >
                    {t('integrations.disconnect')}
                  </button>
                ) : (
                  <button
                    onClick={() => handleConnect(provider.id)}
                    className="flex-1 px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary-hover)] transition-colors"
                  >
                    {t('integrations.connect')}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
