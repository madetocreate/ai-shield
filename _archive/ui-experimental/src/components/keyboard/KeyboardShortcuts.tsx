/**
 * Keyboard Shortcuts - Erweiterte Keyboard Navigation
 */

import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface Shortcut {
  key: string;
  description: string;
  action: () => void;
  global?: boolean;
}

export function useKeyboardShortcuts(shortcuts: Shortcut[]) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const shortcut = shortcuts.find(s => {
        const keys = s.key.split('+').map(k => k.trim().toLowerCase());
        const hasCtrl = keys.includes('ctrl') && (e.ctrlKey || e.metaKey);
        const hasShift = keys.includes('shift') && e.shiftKey;
        const hasAlt = keys.includes('alt') && e.altKey;
        const key = keys.find(k => !['ctrl', 'shift', 'alt', 'cmd'].includes(k));
        
        return (
          key === e.key.toLowerCase() &&
          hasCtrl === keys.includes('ctrl') &&
          hasShift === keys.includes('shift') &&
          hasAlt === keys.includes('alt')
        );
      });

      if (shortcut && (shortcut.global || document.activeElement?.tagName !== 'INPUT')) {
        e.preventDefault();
        shortcut.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
}

// Pre-defined shortcuts
export const defaultShortcuts = (t: any, actions: {
  search?: () => void;
  new?: () => void;
  save?: () => void;
  settings?: () => void;
  help?: () => void;
}) => [
  {
    key: 'Ctrl+K',
    description: t('shortcuts.search'),
    action: actions.search || (() => {}),
    global: true
  },
  {
    key: 'Ctrl+N',
    description: t('shortcuts.new'),
    action: actions.new || (() => {}),
    global: true
  },
  {
    key: 'Ctrl+S',
    description: t('shortcuts.save'),
    action: actions.save || (() => {}),
    global: false
  },
  {
    key: 'Ctrl+,',
    description: t('shortcuts.settings'),
    action: actions.settings || (() => {}),
    global: true
  },
  {
    key: 'Ctrl+?',
    description: t('shortcuts.help'),
    action: actions.help || (() => {}),
    global: true
  }
];
