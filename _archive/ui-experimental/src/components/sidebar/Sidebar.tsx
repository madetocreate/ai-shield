/**
 * Sidebar - Navigation
 * 
 * Features:
 * - Navigation Menu
 * - Nur in Development sichtbar
 * - Onboarding & Wizards sind in DevToolsButtons (immer sichtbar)
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  LayoutDashboard, 
  Package, 
  BarChart3, 
  Plug, 
  Activity, 
  Settings,
  GraduationCap,
  Sparkles,
  Menu,
  X,
  ChevronRight
} from 'lucide-react';
import { useOnboarding } from '@/components/onboarding/useOnboarding';
import { OnboardingTour } from '@/components/onboarding/OnboardingTour';
import { getDefaultOnboardingSteps } from '@/components/onboarding/OnboardingSteps';
import { WizardManager } from '@/components/wizards/WizardManager';
import { useToast } from '@/hooks/useToast';

interface SidebarProps {
  currentPage?: string;
  onNavigate?: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showWizards, setShowWizards] = useState(false);
  const { resetOnboarding } = useOnboarding();
  const { success } = useToast();

  // Immer anzeigen - kann später wieder entfernt werden

  const menuItems = [
    { id: 'dashboard', label: t('sidebar.dashboard'), icon: LayoutDashboard, path: '/' },
    { id: 'marketplace', label: t('sidebar.marketplace'), icon: Package, path: '/marketplace' },
    { id: 'analytics', label: t('sidebar.analytics'), icon: BarChart3, path: '/analytics' },
    { id: 'integrations', label: t('sidebar.integrations'), icon: Plug, path: '/integrations' },
    { id: 'realtime', label: t('sidebar.realtime'), icon: Activity, path: '/realtime' },
    { id: 'settings', label: t('sidebar.settings'), icon: Settings, path: '/settings' },
  ];

  const devItems = [
    { 
      id: 'onboarding', 
      label: t('sidebar.onboarding'), 
      icon: GraduationCap, 
      onClick: () => {
        resetOnboarding();
        setShowOnboarding(true);
        success(t('sidebar.onboardingStarted'));
      }
    },
    { 
      id: 'wizards', 
      label: t('sidebar.wizards'), 
      icon: Sparkles, 
      onClick: () => {
        setShowWizards(true);
      }
    },
  ];

  const handleNavigate = (path: string) => {
    if (onNavigate) {
      onNavigate(path);
    } else {
      window.location.href = path;
    }
  };

  const onboardingSteps = getDefaultOnboardingSteps(t);

  return (
    <>
      {/* Sidebar - Immer sichtbar */}
      <div
        className={`fixed left-0 top-0 h-screen bg-[var(--color-surface-elevated)] border-r border-[var(--color-border)] z-50 transition-all duration-300 ${
          isOpen ? 'w-64' : 'w-16'
        }`}
      >
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[var(--color-border)]">
          {isOpen && (
            <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
              {t('sidebar.title')}
            </h2>
          )}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {/* Main Menu */}
          <div className="px-2 space-y-1">
            {menuItems.map(item => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.path)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-[var(--color-primary)] text-white'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)] hover:text-[var(--color-text-primary)]'
                  }`}
                  title={!isOpen ? item.label : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {isOpen && (
                    <span className="flex-1 text-left">{item.label}</span>
                  )}
                  {isOpen && isActive && (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>
              );
            })}
          </div>

          {/* Dev Tools Section Divider */}
          {isOpen && (
            <div className="px-4 py-2 mt-4">
              <div className="h-px bg-[var(--color-border)] mb-2" />
              <div className="text-xs font-medium text-[var(--color-text-tertiary)] uppercase tracking-wider px-2">
                {t('sidebar.devTools')}
              </div>
            </div>
          )}

          {/* Dev Tools */}
          <div className="px-2 space-y-1 mt-2">
            {devItems.map(item => {
              const Icon = item.icon;
              
              return (
                <button
                  key={item.id}
                  onClick={item.onClick}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)] hover:text-[var(--color-text-primary)] transition-colors"
                  title={!isOpen ? item.label : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {isOpen && (
                    <span className="flex-1 text-left">{item.label}</span>
                  )}
                </button>
              );
            })}
          </div>
        </nav>

        {/* Footer - Optional, kann entfernt werden */}
        {isOpen && (
          <div className="px-4 py-3 border-t border-[var(--color-border)]">
            <div className="text-xs text-[var(--color-text-tertiary)]">
              {t('sidebar.devMode')}
            </div>
          </div>
        )}
      </div>

      {/* Content Offset */}
      <div className={isOpen ? 'ml-64' : 'ml-16'} />

      {/* Onboarding Tour */}
      {showOnboarding && (
        <OnboardingTour
          steps={onboardingSteps}
          onComplete={() => {
            setShowOnboarding(false);
            success(t('sidebar.onboardingComplete'));
          }}
          onSkip={() => {
            setShowOnboarding(false);
          }}
        />
      )}

      {/* Wizard Manager */}
      <WizardManager
        isOpen={showWizards}
        onClose={() => setShowWizards(false)}
      />
    </>
  );
};
