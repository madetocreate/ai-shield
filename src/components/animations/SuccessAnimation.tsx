/**
 * Success Animations - Confetti, Checkmarks
 */

import React, { useEffect, useState } from 'react';
import { Check, Sparkles } from 'lucide-react';

interface SuccessAnimationProps {
  type?: 'checkmark' | 'confetti';
  message?: string;
  onComplete?: () => void;
  duration?: number;
}

export const SuccessAnimation: React.FC<SuccessAnimationProps> = ({
  type = 'checkmark',
  message,
  onComplete,
  duration = 2000
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onComplete?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onComplete]);

  if (!isVisible) return null;

  if (type === 'checkmark') {
    return (
      <div className="fixed inset-0 z-[10001] flex items-center justify-center pointer-events-none">
        <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg shadow-xl p-8 flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 bg-[var(--color-success)] rounded-full flex items-center justify-center animate-[scaleIn_0.3s_ease-out]">
              <Check className="w-8 h-8 text-white" strokeWidth={3} />
            </div>
            <div className="absolute inset-0 bg-[var(--color-success)] rounded-full animate-[ripple_0.6s_ease-out] opacity-0" />
          </div>
          {message && (
            <p className="text-lg font-medium text-[var(--color-text-primary)]">
              {message}
            </p>
          )}
        </div>
      </div>
    );
  }

  // Confetti
  return (
    <div className="fixed inset-0 z-[10001] pointer-events-none overflow-hidden">
      {Array.from({ length: 50 }).map((_, i) => {
        const delay = Math.random() * 0.5;
        const duration = 2 + Math.random() * 2;
        const left = Math.random() * 100;
        const rotation = Math.random() * 360;
        const colors = [
          'var(--color-primary)',
          'var(--color-success)',
          'var(--color-warning)',
          'var(--color-error)',
          'var(--color-info)'
        ];
        const color = colors[Math.floor(Math.random() * colors.length)];

        return (
          <div
            key={i}
            className="absolute w-2 h-2 rounded-full"
            style={{
              left: `${left}%`,
              top: '-10px',
              backgroundColor: color,
              animation: `confettiFall ${duration}s ease-out ${delay}s forwards`,
              transform: `rotate(${rotation}deg)`
            }}
          />
        );
      })}
      {message && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg shadow-xl p-6">
            <p className="text-lg font-medium text-[var(--color-text-primary)] flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[var(--color-success)]" />
              {message}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
