/**
 * Onboarding Hook - Verwaltet Onboarding State
 */

import { useState, useEffect } from 'react';

export function useOnboarding() {
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(() => {
    return localStorage.getItem('onboarding_completed') === 'true';
  });

  const [shouldShowOnboarding, setShouldShowOnboarding] = useState(() => {
    if (hasCompletedOnboarding) return false;
    return localStorage.getItem('onboarding_dismissed') !== 'true';
  });

  const completeOnboarding = () => {
    setHasCompletedOnboarding(true);
    setShouldShowOnboarding(false);
    localStorage.setItem('onboarding_completed', 'true');
  };

  const dismissOnboarding = () => {
    setShouldShowOnboarding(false);
    localStorage.setItem('onboarding_dismissed', 'true');
  };

  const resetOnboarding = () => {
    localStorage.removeItem('onboarding_completed');
    localStorage.removeItem('onboarding_dismissed');
    setHasCompletedOnboarding(false);
    setShouldShowOnboarding(true);
  };

  return {
    hasCompletedOnboarding,
    shouldShowOnboarding,
    completeOnboarding,
    dismissOnboarding,
    resetOnboarding
  };
}
