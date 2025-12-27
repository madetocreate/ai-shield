/**
 * Wizard Manager - Verwaltet verschiedene Wizards
 * 
 * Features:
 * - Agent Setup Wizard
 * - Integration Setup Wizard
 * - Workflow Wizard
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { X, ArrowRight, ArrowLeft, Check, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/useToast';

interface WizardStep {
  id: string;
  title: string;
  description: string;
  component: React.ReactNode;
}

interface Wizard {
  id: string;
  title: string;
  description: string;
  steps: WizardStep[];
}

interface WizardManagerProps {
  isOpen: boolean;
  onClose: () => void;
  wizardId?: string;
}

export const WizardManager: React.FC<WizardManagerProps> = ({ isOpen, onClose, wizardId }) => {
  const { t } = useTranslation();
  const [currentWizard, setCurrentWizard] = useState<string | null>(wizardId || null);
  const [currentStep, setCurrentStep] = useState(0);
  const { success } = useToast();

  // TODO: Wizards definieren
  const wizards: Wizard[] = [
    {
      id: 'agent-setup',
      title: t('wizards.agentSetup.title'),
      description: t('wizards.agentSetup.description'),
      steps: [
        {
          id: 'select-template',
          title: t('wizards.agentSetup.steps.selectTemplate.title'),
          description: t('wizards.agentSetup.steps.selectTemplate.description'),
          component: <div>{t('wizards.agentSetup.steps.selectTemplate.content')}</div>
        },
        {
          id: 'configure',
          title: t('wizards.agentSetup.steps.configure.title'),
          description: t('wizards.agentSetup.steps.configure.description'),
          component: <div>{t('wizards.agentSetup.steps.configure.content')}</div>
        },
        {
          id: 'review',
          title: t('wizards.agentSetup.steps.review.title'),
          description: t('wizards.agentSetup.steps.review.description'),
          component: <div>{t('wizards.agentSetup.steps.review.content')}</div>
        }
      ]
    },
    {
      id: 'integration-setup',
      title: t('wizards.integrationSetup.title'),
      description: t('wizards.integrationSetup.description'),
      steps: [
        {
          id: 'select-provider',
          title: t('wizards.integrationSetup.steps.selectProvider.title'),
          description: t('wizards.integrationSetup.steps.selectProvider.description'),
          component: <div>{t('wizards.integrationSetup.steps.selectProvider.content')}</div>
        },
        {
          id: 'configure',
          title: t('wizards.integrationSetup.steps.configure.title'),
          description: t('wizards.integrationSetup.steps.configure.description'),
          component: <div>{t('wizards.integrationSetup.steps.configure.content')}</div>
        }
      ]
    }
  ];

  if (!isOpen) return null;

  const wizard = wizards.find(w => w.id === currentWizard);
  const step = wizard?.steps[currentStep];

  const handleNext = () => {
    if (wizard && currentStep < wizard.steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      // Wizard abgeschlossen
      success(t('wizards.complete'));
      handleClose();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleClose = () => {
    setCurrentWizard(null);
    setCurrentStep(0);
    onClose();
  };

  // Wizard Auswahl
  if (!currentWizard) {
    return (
      <div className="fixed inset-0 z-[10001] flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Sparkles className="w-6 h-6 text-[var(--color-primary)]" />
              <h2 className="text-2xl font-bold text-[var(--color-text-primary)]">
                {t('wizards.title')}
              </h2>
            </div>
            <button
              onClick={handleClose}
              className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {wizards.map(w => (
              <button
                key={w.id}
                onClick={() => setCurrentWizard(w.id)}
                className="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-elevated)] hover:border-[var(--color-primary)] transition-all text-left"
              >
                <h3 className="font-semibold text-[var(--color-text-primary)] mb-2">
                  {w.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  {w.description}
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Wizard Steps
  return (
    <div className="fixed inset-0 z-[10001] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg shadow-xl p-6 max-w-3xl w-full mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-1">
              {wizard.title}
            </h2>
            <p className="text-sm text-[var(--color-text-secondary)]">
              {t('wizards.step')} {currentStep + 1} {t('wizards.of')} {wizard.steps.length}
            </p>
          </div>
          <button
            onClick={handleClose}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress */}
        <div className="mb-6">
          <div className="h-2 bg-[var(--color-surface)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--color-primary)] transition-all duration-300"
              style={{ width: `${((currentStep + 1) / wizard.steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="flex-1 overflow-y-auto mb-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
              {step?.title}
            </h3>
            <p className="text-sm text-[var(--color-text-secondary)] mb-4">
              {step?.description}
            </p>
          </div>
          <div className="bg-[var(--color-surface)] rounded-lg p-4">
            {step?.component}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-[var(--color-border)]">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="px-4 py-2 text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('common.previous')}
          </button>
          
          <button
            onClick={handleNext}
            className="px-4 py-2 text-sm font-medium bg-[var(--color-primary)] text-white rounded-md hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-2"
          >
            {currentStep === wizard.steps.length - 1 ? (
              <>
                <Check className="w-4 h-4" />
                {t('wizards.finish')}
              </>
            ) : (
              <>
                {t('common.next')}
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
