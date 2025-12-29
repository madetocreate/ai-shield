/**
 * Error Display - Bessere Fehlermeldungen & Help System
 * 
 * Features:
 * - Nutzerfreundliche Erklärungen
 * - "How to fix?" Anleitungen
 * - Help Center Integration
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle, HelpCircle, ExternalLink, ChevronDown, ChevronUp, X } from 'lucide-react';

interface ErrorInfo {
  code?: string;
  message: string;
  friendlyMessage: string;
  howToFix: string[];
  helpCenterLink?: string;
  suggestions?: string[];
}

interface ErrorDisplayProps {
  error: Error | string | ErrorInfo;
  onDismiss?: () => void;
  showHelp?: boolean;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onDismiss, showHelp = true }) => {
  const { t } = useTranslation();
  const [showDetails, setShowDetails] = useState(false);

  const getErrorInfo = (): ErrorInfo => {
    if (typeof error === 'string') {
      return {
        message: error,
        friendlyMessage: t('errors.genericError'),
        howToFix: [t('errors.tryAgain'), t('errors.checkConnection')]
      };
    }

    if (error instanceof Error) {
      const errorMessage = error.message.toLowerCase();
      
      // Network errors
      if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        return {
          code: 'NETWORK_ERROR',
          message: error.message,
          friendlyMessage: t('errors.networkError'),
          howToFix: [
            t('errors.checkInternet'),
            t('errors.checkFirewall'),
            t('errors.tryAgainLater')
          ],
          helpCenterLink: '/help/network-issues'
        };
      }

      // Authentication errors
      if (errorMessage.includes('auth') || errorMessage.includes('unauthorized') || errorMessage.includes('401')) {
        return {
          code: 'AUTH_ERROR',
          message: error.message,
          friendlyMessage: t('errors.authError'),
          howToFix: [
            t('errors.checkCredentials'),
            t('errors.reLogin'),
            t('errors.contactSupport')
          ],
          helpCenterLink: '/help/authentication'
        };
      }

      // Permission errors
      if (errorMessage.includes('permission') || errorMessage.includes('403') || errorMessage.includes('forbidden')) {
        return {
          code: 'PERMISSION_ERROR',
          message: error.message,
          friendlyMessage: t('errors.permissionError'),
          howToFix: [
            t('errors.checkPermissions'),
            t('errors.contactAdmin'),
            t('errors.upgradePlan')
          ],
          helpCenterLink: '/help/permissions'
        };
      }

      // Generic error
      return {
        message: error.message,
        friendlyMessage: t('errors.genericError'),
        howToFix: [
          t('errors.tryAgain'),
          t('errors.checkConnection'),
          t('errors.contactSupport')
        ]
      };
    }

    // Already ErrorInfo
    return error;
  };

  const errorInfo = getErrorInfo();

  return (
    <div className="p-4 bg-[var(--color-error-light)] border border-[var(--color-error)] rounded-lg">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-[var(--color-error)] flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <div className="font-medium text-[var(--color-error-dark)] mb-1">
            {errorInfo.friendlyMessage}
          </div>
          {showDetails && (
            <div className="text-sm text-[var(--color-text-secondary)] mb-3 font-mono">
              {errorInfo.message}
            </div>
          )}
          
          {/* How to Fix */}
          {errorInfo.howToFix && errorInfo.howToFix.length > 0 && (
            <div className="mt-3">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center gap-2 text-sm font-medium text-[var(--color-error-dark)] hover:underline"
              >
                <HelpCircle className="w-4 h-4" />
                {t('errors.howToFix')}
                {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {showDetails && (
                <ul className="mt-2 space-y-1 list-disc list-inside text-sm text-[var(--color-text-secondary)]">
                  {errorInfo.howToFix.map((fix, idx) => (
                    <li key={idx}>{fix}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Suggestions */}
          {errorInfo.suggestions && errorInfo.suggestions.length > 0 && (
            <div className="mt-3">
              <p className="text-sm font-medium text-[var(--color-text-primary)] mb-2">
                {t('errors.suggestions')}:
              </p>
              <div className="flex flex-wrap gap-2">
                {errorInfo.suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    className="px-3 py-1 text-xs bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md hover:bg-[var(--color-surface-elevated)] transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Help Center Link */}
          {errorInfo.helpCenterLink && (
            <div className="mt-3">
              <a
                href={errorInfo.helpCenterLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-[var(--color-primary)] hover:underline"
              >
                <ExternalLink className="w-4 h-4" />
                {t('errors.helpCenter')}
              </a>
            </div>
          )}
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors flex-shrink-0"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
