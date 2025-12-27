/**
 * Theme Provider - Initialisiert Theme System
 */

import React, { useEffect } from 'react';
import { useTheme } from '@/hooks/useTheme';
import '@/styles/tokens.css';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    // Ensure theme is applied on mount
    const root = document.documentElement;
    if (resolvedTheme === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.setAttribute('data-theme', 'light');
    }
  }, [resolvedTheme]);

  return <>{children}</>;
};
