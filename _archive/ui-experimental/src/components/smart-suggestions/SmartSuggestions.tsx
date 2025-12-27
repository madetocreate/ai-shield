/**
 * Smart Suggestions - AI-powered Suggestions System
 * 
 * Features:
 * - Context-aware suggestions
 * - Proactive tips
 * - Usage-based recommendations
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Lightbulb, X, Sparkles, TrendingUp, Zap, ArrowRight } from 'lucide-react';

interface Suggestion {
  id: string;
  type: 'tip' | 'recommendation' | 'insight' | 'action';
  title: string;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon: React.ReactNode;
  priority: 'high' | 'medium' | 'low';
  dismissible: boolean;
}

interface SmartSuggestionsProps {
  context?: {
    currentPage?: string;
    userActions?: string[];
    accountId?: string;
  };
}

export const SmartSuggestions: React.FC<SmartSuggestionsProps> = ({ context }) => {
  const { t } = useTranslation();
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Generate suggestions based on context
    const generateSuggestions = (): Suggestion[] => {
      const newSuggestions: Suggestion[] = [];

      // Context-based suggestions
      if (context?.currentPage === 'marketplace') {
        newSuggestions.push({
          id: 'marketplace-tip-1',
          type: 'tip',
          title: t('suggestions.marketplaceTip'),
          message: t('suggestions.marketplaceTipDesc'),
          icon: <Zap className="w-5 h-5" />,
          priority: 'medium',
          dismissible: true
        });
      }

      if (context?.currentPage === 'analytics' && !context.userActions?.includes('created_report')) {
        newSuggestions.push({
          id: 'analytics-report',
          type: 'recommendation',
          title: t('suggestions.createReport'),
          message: t('suggestions.createReportDesc'),
          icon: <TrendingUp className="w-5 h-5" />,
          priority: 'high',
          dismissible: true,
          action: {
            label: t('suggestions.createNow'),
            onClick: () => {
              window.location.href = '/analytics?action=create-report';
            }
          }
        });
      }

      // General suggestions
      if (!localStorage.getItem('has_installed_agent')) {
        newSuggestions.push({
          id: 'first-agent',
          type: 'action',
          title: t('suggestions.firstAgent'),
          message: t('suggestions.firstAgentDesc'),
          icon: <Sparkles className="w-5 h-5" />,
          priority: 'high',
          dismissible: true,
          action: {
            label: t('suggestions.browseAgents'),
            onClick: () => {
              window.location.href = '/marketplace';
            }
          }
        });
      }

      // Usage-based insights
      const agentCount = parseInt(localStorage.getItem('agent_count') || '0');
      if (agentCount > 0 && agentCount < 3) {
        newSuggestions.push({
          id: 'expand-agents',
          type: 'insight',
          title: t('suggestions.expandAgents'),
          message: t('suggestions.expandAgentsDesc'),
          icon: <TrendingUp className="w-5 h-5" />,
          priority: 'low',
          dismissible: true,
          action: {
            label: t('suggestions.explore'),
            onClick: () => {
              window.location.href = '/marketplace';
            }
          }
        });
      }

      return newSuggestions.filter(s => !dismissed.has(s.id));
    };

    const newSuggestions = generateSuggestions();
    setSuggestions(newSuggestions);
  }, [context, dismissed, t]);

  const handleDismiss = (id: string) => {
    setDismissed(prev => new Set([...prev, id]));
    setSuggestions(prev => prev.filter(s => s.id !== id));
  };

  if (suggestions.length === 0) return null;

  // Show only highest priority suggestion
  const topSuggestion = suggestions.sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    return priorityOrder[b.priority] - priorityOrder[a.priority];
  })[0];

  if (!topSuggestion) return null;

  return (
    <div className="mb-4 p-4 bg-[var(--color-primary-light)] border border-[var(--color-primary)] rounded-lg">
      <div className="flex items-start gap-3">
        <div className="text-[var(--color-primary)] mt-0.5">
          {topSuggestion.icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-[var(--color-text-primary)] mb-1">
            {topSuggestion.title}
          </div>
          <div className="text-sm text-[var(--color-text-secondary)] mb-3">
            {topSuggestion.message}
          </div>
          {topSuggestion.action && (
            <button
              onClick={topSuggestion.action.onClick}
              className="inline-flex items-center gap-2 px-3 py-1.5 bg-[var(--color-primary)] text-white rounded-md hover:bg-[var(--color-primary-hover)] transition-colors text-sm font-medium"
            >
              {topSuggestion.action.label}
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
        {topSuggestion.dismissible && (
          <button
            onClick={() => handleDismiss(topSuggestion.id)}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
