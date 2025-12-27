/**
 * Default Onboarding Steps
 */

import { useTranslation } from 'react-i18next';

export const getDefaultOnboardingSteps = (t: any) => [
  {
    id: 'welcome',
    target: 'body',
    title: t('onboarding.steps.welcome.title'),
    description: t('onboarding.steps.welcome.description'),
    position: 'bottom' as const
  },
  {
    id: 'marketplace',
    target: '[data-tour="marketplace"]',
    title: t('onboarding.steps.marketplace.title'),
    description: t('onboarding.steps.marketplace.description'),
    position: 'bottom' as const,
    action: {
      label: t('onboarding.steps.marketplace.action'),
      onClick: () => {
        window.location.href = '/marketplace';
      }
    }
  },
  {
    id: 'integrations',
    target: '[data-tour="integrations"]',
    title: t('onboarding.steps.integrations.title'),
    description: t('onboarding.steps.integrations.description'),
    position: 'bottom' as const
  },
  {
    id: 'analytics',
    target: '[data-tour="analytics"]',
    title: t('onboarding.steps.analytics.title'),
    description: t('onboarding.steps.analytics.description'),
    position: 'bottom' as const
  },
  {
    id: 'settings',
    target: '[data-tour="settings"]',
    title: t('onboarding.steps.settings.title'),
    description: t('onboarding.steps.settings.description'),
    position: 'bottom' as const
  }
];
