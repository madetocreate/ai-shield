/**
 * Command Palette - Cmd+K / Ctrl+K
 * 
 * Features:
 * - Global Search
 * - Quick Actions
 * - Keyboard Navigation
 * - Fuzzy Search
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Command, ArrowRight, FileText, Settings, Zap, Users, BarChart3, Bell, Globe } from 'lucide-react';

interface CommandItem {
  id: string;
  title: string;
  description?: string;
  icon: React.ReactNode;
  action: () => void;
  keywords: string[];
  category: string;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const commands: CommandItem[] = [
    {
      id: 'marketplace',
      title: t('commandPalette.marketplace'),
      description: t('commandPalette.marketplaceDesc'),
      icon: <Zap className="w-4 h-4" />,
      action: () => {
        window.location.href = '/marketplace';
        onClose();
      },
      keywords: ['marketplace', 'agents', 'install', 'agent'],
      category: 'navigation'
    },
    {
      id: 'analytics',
      title: t('commandPalette.analytics'),
      description: t('commandPalette.analyticsDesc'),
      icon: <BarChart3 className="w-4 h-4" />,
      action: () => {
        window.location.href = '/analytics';
        onClose();
      },
      keywords: ['analytics', 'metrics', 'reports', 'dashboard'],
      category: 'navigation'
    },
    {
      id: 'integrations',
      title: t('commandPalette.integrations'),
      description: t('commandPalette.integrationsDesc'),
      icon: <Users className="w-4 h-4" />,
      action: () => {
        window.location.href = '/integrations';
        onClose();
      },
      keywords: ['integrations', 'connect', 'providers', 'nango'],
      category: 'navigation'
    },
    {
      id: 'realtime',
      title: t('commandPalette.realtime'),
      description: t('commandPalette.realtimeDesc'),
      icon: <Bell className="w-4 h-4" />,
      action: () => {
        window.location.href = '/realtime';
        onClose();
      },
      keywords: ['realtime', 'monitoring', 'alerts', 'live'],
      category: 'navigation'
    },
    {
      id: 'settings',
      title: t('commandPalette.settings'),
      description: t('commandPalette.settingsDesc'),
      icon: <Settings className="w-4 h-4" />,
      action: () => {
        window.location.href = '/settings';
        onClose();
      },
      keywords: ['settings', 'preferences', 'config', 'options'],
      category: 'navigation'
    },
    {
      id: 'docs',
      title: t('commandPalette.docs'),
      description: t('commandPalette.docsDesc'),
      icon: <FileText className="w-4 h-4" />,
      action: () => {
        window.open('/docs', '_blank');
        onClose();
      },
      keywords: ['docs', 'documentation', 'help', 'guide'],
      category: 'navigation'
    },
    {
      id: 'language',
      title: t('commandPalette.language'),
      description: t('commandPalette.languageDesc'),
      icon: <Globe className="w-4 h-4" />,
      action: () => {
        window.location.href = '/settings#language';
        onClose();
      },
      keywords: ['language', 'locale', 'i18n', 'translate'],
      category: 'settings'
    }
  ];

  const filteredCommands = commands.filter(cmd => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      cmd.title.toLowerCase().includes(query) ||
      cmd.description?.toLowerCase().includes(query) ||
      cmd.keywords.some(kw => kw.toLowerCase().includes(query))
    );
  });

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      setSearchQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action();
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filteredCommands, selectedIndex, onClose]);

  useEffect(() => {
    // Scroll selected item into view
    if (listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement;
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Command Palette */}
      <div className="relative w-full max-w-2xl mx-4">
        <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg shadow-xl overflow-hidden">
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--color-border)]">
            <Search className="w-5 h-5 text-[var(--color-text-tertiary)]" />
            <input
              ref={inputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('commandPalette.placeholder')}
              className="flex-1 bg-transparent text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] outline-none"
            />
            <div className="flex items-center gap-1 text-xs text-[var(--color-text-tertiary)]">
              <kbd className="px-2 py-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded">
                {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}
              </kbd>
              <span>+</span>
              <kbd className="px-2 py-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded">K</kbd>
            </div>
          </div>

          {/* Results */}
          <div ref={listRef} className="max-h-96 overflow-y-auto">
            {filteredCommands.length === 0 ? (
              <div className="px-4 py-8 text-center text-[var(--color-text-tertiary)]">
                {t('commandPalette.noResults')}
              </div>
            ) : (
              filteredCommands.map((cmd, index) => (
                <button
                  key={cmd.id}
                  onClick={cmd.action}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-[var(--color-surface)] transition-colors ${
                    index === selectedIndex ? 'bg-[var(--color-surface)]' : ''
                  }`}
                >
                  <div className="text-[var(--color-text-secondary)]">
                    {cmd.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-[var(--color-text-primary)]">
                      {cmd.title}
                    </div>
                    {cmd.description && (
                      <div className="text-sm text-[var(--color-text-tertiary)] truncate">
                        {cmd.description}
                      </div>
                    )}
                  </div>
                  <ArrowRight className="w-4 h-4 text-[var(--color-text-tertiary)] opacity-0 group-hover:opacity-100" />
                </button>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 border-t border-[var(--color-border)] text-xs text-[var(--color-text-tertiary)] flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded">↑↓</kbd>
                <span>{t('commandPalette.navigate')}</span>
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded">↵</kbd>
                <span>{t('commandPalette.select')}</span>
              </span>
            </div>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded">Esc</kbd>
              <span>{t('commandPalette.close')}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
