"use client";

import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { ErrorDisplay } from "@/components/error-handling/ErrorDisplay";
import { useToast } from "@/hooks/useToast";

interface ApprovalRequest {
  request_id: string;
  tenant_id: string;
  provider: string;
  operation: string;
  preview?: {
    action?: string;
    [key: string]: any;
  };
  status: "pending" | "approved" | "rejected";
  created_at?: string;
  approved_at?: string;
  approved_by?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_CONTROL_PLANE_URL || "http://localhost:4051";

export default function ApprovalQueue() {
  const { t, i18n } = useTranslation();
  const { success, error: showError } = useToast();
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tenantId] = useState("default-tenant"); // TODO: Get from context/auth

  useEffect(() => {
    loadApprovalRequests();
    // Poll for new requests
    const interval = setInterval(loadApprovalRequests, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadApprovalRequests = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/v1/integrations/approvals?tenant_id=${tenantId}`, {
        headers: {
          "x-tenant-id": tenantId,
          "x-ai-shield-admin-key": process.env.NEXT_PUBLIC_ADMIN_KEY || "",
        },
      });

      if (!response.ok) {
        // Endpoint might not exist yet, that's ok
        if (response.status === 404) {
          setRequests([]);
          return;
        }
        throw new Error(`Failed to load approvals: ${response.statusText}`);
      }

      const data = await response.json();
      setRequests(data.filter((r: ApprovalRequest) => r.status === "pending"));
    } catch (err) {
      // Silently fail if endpoint doesn't exist yet
      if (err instanceof Error && err.message.includes("404")) {
        setRequests([]);
        return;
      }
      setError(err instanceof Error ? err.message : "Unknown error");
      console.error("Failed to load approval requests:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId: string) => {
    try {
      setError(null);
      const response = await fetch(
        `${API_BASE_URL}/v1/integrations/approvals/${requestId}/approve`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-ai-shield-admin-key": process.env.NEXT_PUBLIC_ADMIN_KEY || "",
          },
          body: JSON.stringify({
            tenant_id: tenantId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to approve: ${response.statusText}`);
      }

      success(t('integrations.approveSuccess'));
      await loadApprovalRequests();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve");
      console.error("Failed to approve:", err);
    }
  };

  const handleReject = async (requestId: string) => {
    try {
      setError(null);
      const response = await fetch(
        `${API_BASE_URL}/v1/integrations/approvals/${requestId}/reject`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-ai-shield-admin-key": process.env.NEXT_PUBLIC_ADMIN_KEY || "",
          },
          body: JSON.stringify({
            tenant_id: tenantId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to reject: ${response.statusText}`);
      }

      success(t('integrations.rejectSuccess'));
      await loadApprovalRequests();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject");
      console.error("Failed to reject:", err);
    }
  };

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      google: "📅",
      shopify: "🛒",
      woocommerce: "🛍️",
      whatsapp: "💬",
    };
    return icons[provider] || "🔗";
  };

  if (loading) {
    return (
      <div className="p-6">
        <h2 className="text-xl font-bold mb-4">{t('integrations.approvalQueue')}</h2>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-6 bg-[var(--color-surface-elevated)] rounded-lg border border-[var(--color-border)]">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-[var(--color-surface)] rounded-full animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-[var(--color-surface)] rounded w-3/4 animate-pulse" />
                  <div className="h-3 bg-[var(--color-surface)] rounded w-1/2 animate-pulse" />
                  <div className="h-3 bg-[var(--color-surface)] rounded w-2/3 animate-pulse" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (requests.length === 0) {
    return (
      <div className="p-6">
        <h2 className="text-xl font-bold mb-4">{t('integrations.approvalQueue')}</h2>
        <div className="text-center py-12 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
          <p className="text-[var(--color-text-secondary)]">{t('integrations.noPendingApprovals')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">{t('integrations.approvalQueue')}</h2>
      <p className="text-sm text-[var(--color-text-secondary)] mb-6">
        {t('integrations.pendingApprovals')}
      </p>

      {error && (
        <div className="mb-6">
          <ErrorDisplay error={error} onDismiss={() => setError(null)} />
        </div>
      )}

      <div className="space-y-4">
        {requests.map((request) => (
          <div
            key={request.request_id}
            className="p-6 bg-[var(--color-surface-elevated)] rounded-lg border-2 border-[var(--color-warning)] shadow-sm"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getProviderIcon(request.provider)}</span>
                <div>
                  <h3 className="font-semibold text-lg">
                    {request.preview?.action || request.operation}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {request.provider} • {request.operation}
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 bg-[var(--color-warning-light)] text-[var(--color-warning-dark)] text-xs font-medium rounded border border-[var(--color-warning)]">
                {t('integrations.status')}
              </span>
            </div>

            {request.preview && (
              <div className="mb-4 p-4 bg-[var(--color-surface)] rounded border border-[var(--color-border)]">
                <p className="text-sm font-medium mb-2 text-[var(--color-text-primary)]">{t('common.preview') || 'Preview'}:</p>
                <pre className="text-xs text-[var(--color-text-primary)] whitespace-pre-wrap">
                  {JSON.stringify(request.preview, null, 2)}
                </pre>
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={() => handleApprove(request.request_id)}
                className="flex-1 px-4 py-2 bg-[var(--color-success)] text-white rounded hover:bg-[var(--color-success-dark)] transition-colors"
              >
                {t('integrations.approve')}
              </button>
              <button
                onClick={() => handleReject(request.request_id)}
                className="flex-1 px-4 py-2 bg-[var(--color-error)] text-white rounded hover:bg-[var(--color-error-dark)] transition-colors"
              >
                {t('integrations.reject')}
              </button>
            </div>

            {request.created_at && (
              <p className="mt-2 text-xs text-[var(--color-text-tertiary)]">
                {t('integrations.created')}: {new Date(request.created_at).toLocaleString(
                  i18n.language === 'de' ? 'de-DE' : 
                  i18n.language === 'es' ? 'es-ES' : 
                  i18n.language === 'fr' ? 'fr-FR' : 
                  i18n.language === 'it' ? 'it-IT' : 
                  'en-US'
                )}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
