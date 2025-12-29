/**
 * Dev Tools Buttons - Onboarding & Wizards Icons
 * 
 * Features:
 * - Immer sichtbar (auch in Production)
 * - Floating Buttons
 * - Onboarding & Wizards Zugriff
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { GraduationCap, Sparkles, X } from 'lucide-react';
import { useOnboarding } from '@/components/onboarding/useOnboarding';
import { OnboardingTour } from '@/components/onboarding/OnboardingTour';
import { getDefaultOnboardingSteps } from '@/components/onboarding/OnboardingSteps';
import { WizardManager } from '@/components/wizards/WizardManager';
import { useToast } from '@/hooks/useToast';

export const DevToolsButtons: React.FC = () => {
  const { t } = useTranslation();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showWizards, setShowWizards] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const { resetOnboarding } = useOnboarding();
  const { success } = useToast();

  const onboardingSteps = getDefaultOnboardingSteps(t);

  return (
    <>
      {/* Floating Dev Tools Buttons */}
      <div className="fixed bottom-6 left-6 z-[10000] flex flex-col gap-3">
        {isExpanded && (
          <>
            {/* Onboarding Button */}
            <button
              onClick={() => {
                resetOnboarding();
                setShowOnboarding(true);
                success(t('sidebar.onboardingStarted'));
              }}
              className="w-14 h-14 bg-[var(--color-primary)] text-white rounded-full shadow-lg hover:bg-[var(--color-primary-hover)] transition-all flex items-center justify-center group"
              title={t('sidebar.onboarding')}
            >
              <GraduationCap className="w-6 h-6" />
            </button>

            {/* Wizards Button */}
            <button
              onClick={() => {
                setShowWizards(true);
              }}
              className="w-14 h-14 bg-[var(--color-primary)] text-white rounded-full shadow-lg hover:bg-[var(--color-primary-hover)] transition-all flex items-center justify-center group"
              title={t('sidebar.wizards')}
            >
              <Sparkles className="w-6 h-6" />
            </button>
          </>
        )}

        {/* Toggle Button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`w-14 h-14 bg-[var(--color-surface-elevated)] border-2 border-[var(--color-primary)] text-[var(--color-primary)] rounded-full shadow-lg hover:bg-[var(--color-surface)] transition-all flex items-center justify-center ${
            isExpanded ? 'rotate-45' : ''
          }`}
          title={isExpanded ? t('common.close') : t('sidebar.devTools')}
        >
          {isExpanded ? (
            <X className="w-6 h-6" />
          ) : (
            <GraduationCap className="w-6 h-6" />
          )}
        </button>
      </div>

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
