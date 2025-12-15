/**
 * App Wrapper - Integriert alle UX Features
 * 
 * Wrappt die App mit:
 * - Theme Provider
 * - Command Palette Provider
 * - Toast Container
 * - AI Help Chatbot
 */

import React from 'react';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { CommandPaletteProvider } from '@/components/command-palette/CommandPaletteProvider';
import { ToastContainer } from '@/components/toast/Toast';
import { AIHelpChatbot } from '@/components/ai-help/AIHelpChatbot';
import { Sidebar } from '@/components/sidebar/Sidebar';
import { DevToolsButtons } from '@/components/dev-tools/DevToolsButtons';
import { useToast } from '@/hooks/useToast';
import '@/styles/tokens.css';
import '@/styles/animations.css';

interface AppWrapperProps {
  children: React.ReactNode;
  currentPage?: string;
  onNavigate?: (page: string) => void;
}

export const AppWrapper: React.FC<AppWrapperProps> = ({ children, currentPage, onNavigate }) => {
  const { toasts, removeToast } = useToast();

  return (
    <ThemeProvider>
      <CommandPaletteProvider>
        {/* Sidebar - Nur in Development */}
        <Sidebar currentPage={currentPage} onNavigate={onNavigate} />
        
        {/* Dev Tools Buttons - Immer sichtbar (Onboarding & Wizards) */}
        <DevToolsButtons />
        
        {/* Content */}
        <div className="min-h-screen">
          {children}
        </div>
        
        {/* Toast Container */}
        <ToastContainer toasts={toasts} onClose={removeToast} />
        
        {/* AI Help Chatbot */}
        <AIHelpChatbot />
      </CommandPaletteProvider>
    </ThemeProvider>
  );
};
