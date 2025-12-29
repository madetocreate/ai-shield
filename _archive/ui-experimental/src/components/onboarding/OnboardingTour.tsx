/**
 * Onboarding Tour - Interaktive Tour durch das System
 * 
 * Features:
 * - Schritt-für-Schritt Anleitung
 * - Highlight von Elementen
 * - Progress Tracking
 * - Skip Option
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { X, ArrowRight, ArrowLeft, Check } from 'lucide-react';

interface TourStep {
  id: string;
  target: string; // CSS Selector
  title: string;
  description: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface OnboardingTourProps {
  steps: TourStep[];
  onComplete?: () => void;
  onSkip?: () => void;
}

export const OnboardingTour: React.FC<OnboardingTourProps> = ({ steps, onComplete, onSkip }) => {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const overlayRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (currentStep >= steps.length) {
      setIsVisible(false);
      onComplete?.();
      return;
    }

    const step = steps[currentStep];
    const element = document.querySelector(step.target);
    
    if (element) {
      // Scroll element into view
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Position tooltip
      setTimeout(() => {
        if (tooltipRef.current && overlayRef.current) {
          const rect = element.getBoundingClientRect();
          const tooltip = tooltipRef.current;
          
          const position = step.position || 'bottom';
          let top = 0;
          let left = 0;
          
          switch (position) {
            case 'top':
              top = rect.top - tooltip.offsetHeight - 20;
              left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;
              break;
            case 'bottom':
              top = rect.bottom + 20;
              left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;
              break;
            case 'left':
              top = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
              left = rect.left - tooltip.offsetWidth - 20;
              break;
            case 'right':
              top = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
              left = rect.right + 20;
              break;
          }
          
          tooltip.style.top = `${top}px`;
          tooltip.style.left = `${left}px`;
        }
      }, 300);
    }
  }, [currentStep, steps, onComplete]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setIsVisible(false);
      onComplete?.();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSkip = () => {
    setIsVisible(false);
    onSkip?.();
  };

  if (!isVisible || currentStep >= steps.length) return null;

  const step = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <>
      {/* Overlay */}
      <div
        ref={overlayRef}
        className="fixed inset-0 z-[9998] bg-black/50 backdrop-blur-sm"
        onClick={handleNext}
      />
      
      {/* Highlight */}
      <div
        className="fixed z-[9999] border-4 border-[var(--color-primary)] rounded-lg pointer-events-none"
        style={{
          top: 0,
          left: 0,
          width: 0,
          height: 0
        }}
      />

      {/* Tooltip */}
      <div
        ref={tooltipRef}
        className="fixed z-[10000] bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg shadow-xl p-6 max-w-sm pointer-events-auto"
        style={{
          transform: 'translate(-50%, 0)'
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="text-sm font-medium text-[var(--color-text-secondary)] mb-1">
              {t('onboarding.step')} {currentStep + 1} {t('onboarding.of')} {steps.length}
            </div>
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
              {step.title}
            </h3>
          </div>
          <button
            onClick={handleSkip}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Description */}
        <p className="text-sm text-[var(--color-text-secondary)] mb-4">
          {step.description}
        </p>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="h-1 bg-[var(--color-surface)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--color-primary)] transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="px-4 py-2 text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('common.previous')}
          </button>
          
          <div className="flex items-center gap-2">
            {step.action && (
              <button
                onClick={step.action.onClick}
                className="px-4 py-2 text-sm font-medium bg-[var(--color-surface)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-md hover:bg-[var(--color-surface-elevated)] transition-colors"
              >
                {step.action.label}
              </button>
            )}
            <button
              onClick={handleNext}
              className="px-4 py-2 text-sm font-medium bg-[var(--color-primary)] text-white rounded-md hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-2"
            >
              {currentStep === steps.length - 1 ? (
                <>
                  <Check className="w-4 h-4" />
                  {t('onboarding.complete')}
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
    </>
  );
};
