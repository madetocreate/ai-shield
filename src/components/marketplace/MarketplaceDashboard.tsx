/**
 * Marketplace Dashboard - Frontend für App Marketplace
 * 
 * Features:
 * - Agent Discovery
 * - Agent Details
 * - Installation/Uninstallation
 * - Rating
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Star, Search, Download, Trash2, Filter, Package } from 'lucide-react';
import { EmptyState } from '@/components/empty-states/EmptyState';
import { SmartSuggestions } from '@/components/smart-suggestions/SmartSuggestions';
import { Tooltip } from '@/components/tooltip/Tooltip';

interface MarketplaceAgent {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  category: string;
  tags: string[];
  installation_count: number;
  average_rating: number;
  rating_count: number;
  code_url?: string;
  documentation_url?: string;
}

export const MarketplaceDashboard: React.FC = () => {
  const [agents, setAgents] = useState<MarketplaceAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [installedAgents, setInstalledAgents] = useState<Set<string>>(new Set());

  const accountId = 'current_account'; // TODO: Aus Context holen

  useEffect(() => {
    loadAgents();
    loadInstalledAgents();
  }, [searchQuery, categoryFilter]);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      if (categoryFilter !== 'all') params.append('category', categoryFilter);
      
      const response = await fetch(`/api/v1/marketplace/agents?${params}`);
      const data = await response.json();
      setAgents(data);
    } catch (error) {
      console.error('Fehler beim Laden der Agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadInstalledAgents = async () => {
    try {
      const response = await fetch(`/api/v1/marketplace/installed/${accountId}`);
      const data = await response.json();
      setInstalledAgents(new Set(data.map((a: MarketplaceAgent) => a.id)));
    } catch (error) {
      console.error('Fehler beim Laden installierter Agents:', error);
    }
  };

  const handleInstall = async (agentId: string) => {
    try {
      const response = await fetch(`/api/v1/marketplace/agents/${agentId}/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_id: accountId })
      });
      
      if (response.ok) {
        setInstalledAgents(new Set([...installedAgents, agentId]));
        loadAgents(); // Refresh für updated installation_count
      }
    } catch (error) {
      console.error('Fehler beim Installieren:', error);
    }
  };

  const handleUninstall = async (agentId: string) => {
    try {
      const response = await fetch(`/api/v1/marketplace/agents/${agentId}/install`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_id: accountId })
      });
      
      if (response.ok) {
        const newInstalled = new Set(installedAgents);
        newInstalled.delete(agentId);
        setInstalledAgents(newInstalled);
        loadAgents();
      }
    } catch (error) {
      console.error('Fehler beim Deinstallieren:', error);
    }
  };

  return (
    <div className="container mx-auto p-6" data-tour="marketplace">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">{t('marketplace.title')}</h1>
        <Tooltip content={t('marketplace.tooltip')}>
          <button className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)]">
            <Filter className="w-5 h-5" />
          </button>
        </Tooltip>
      </div>
      
      {/* Smart Suggestions */}
      <SmartSuggestions context={{ currentPage: 'marketplace', accountId }} />

      {/* Search & Filter */}
      <div className="mb-6 flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-tertiary)]" />
          <Input
            placeholder={t('marketplace.searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-[var(--color-surface)] border-[var(--color-border)] text-[var(--color-text-primary)]"
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-4 py-2 border border-[var(--color-border)] rounded bg-[var(--color-surface)] text-[var(--color-text-primary)]"
        >
          <option value="all">{t('marketplace.allCategories')}</option>
          <option value="gastronomy">{t('marketplace.categoryGastronomy')}</option>
          <option value="practice">{t('marketplace.categoryPractice')}</option>
          <option value="general">{t('marketplace.categoryGeneral')}</option>
        </select>
      </div>

      {/* Agents Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="p-6 bg-[var(--color-surface-elevated)] rounded-lg border border-[var(--color-border)]">
              <div className="h-6 bg-[var(--color-surface)] rounded w-3/4 mb-4 animate-pulse" />
              <div className="h-4 bg-[var(--color-surface)] rounded w-1/2 mb-4 animate-pulse" />
              <div className="h-20 bg-[var(--color-surface)] rounded mb-4 animate-pulse" />
              <div className="flex gap-2">
                <div className="h-8 bg-[var(--color-surface)] rounded flex-1 animate-pulse" />
                <div className="h-8 bg-[var(--color-surface)] rounded w-20 animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <Card key={agent.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{agent.name}</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">von {agent.author}</p>
                  </div>
                  <Badge variant="outline">{agent.category}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">{agent.description}</p>
                
                {/* Rating */}
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.round(agent.average_rating)
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-[var(--color-text-secondary)]">
                    {agent.average_rating.toFixed(1)} ({agent.rating_count} {t('marketplace.reviews')})
                  </span>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {agent.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs border-[var(--color-border)]">
                      {tag}
                    </Badge>
                  ))}
                </div>

                {/* Stats */}
                <div className="text-sm text-[var(--color-text-tertiary)] mb-4">
                  {agent.installation_count} {t('marketplace.downloads')}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {installedAgents.has(agent.id) ? (
                    <Tooltip content={t('marketplace.uninstallTooltip')}>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleUninstall(agent.id)}
                        className="flex-1"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        {t('marketplace.uninstall')}
                      </Button>
                    </Tooltip>
                  ) : (
                    <Tooltip content={t('marketplace.installTooltip')}>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => handleInstall(agent.id)}
                        className="flex-1"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        {t('marketplace.install')}
                      </Button>
                    </Tooltip>
                  )}
                  {agent.documentation_url && (
                    <Button variant="outline" size="sm" asChild>
                      <a href={agent.documentation_url} target="_blank" rel="noopener noreferrer">
                        {t('marketplace.docs')}
                      </a>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && agents.length === 0 && (
        <EmptyState
          icon={Package}
          title={t('marketplace.noAgentsFound')}
          description={t('marketplace.noAgentsFoundDesc')}
          action={{
            label: t('marketplace.browseTemplates'),
            onClick: () => {
              // Navigate to templates or refresh
              loadAgents();
            }
          }}
        />
      )}
    </div>
  );
};
