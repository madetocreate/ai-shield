/**
 * Toast Notifications - Toast System
 */

import React, { useEffect, useState } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastProps {
  toast: Toast;
  onClose: (id: string) => void;
}

const ToastComponent: React.FC<ToastProps> = ({ toast, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const duration = toast.duration || 5000;
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose(toast.id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [toast, onClose]);

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info
  };

  const colors = {
    success: {
      bg: 'bg-[var(--color-success-light)]',
      border: 'border-[var(--color-success)]',
      icon: 'text-[var(--color-success)]',
      text: 'text-[var(--color-success-dark)]'
    },
    error: {
      bg: 'bg-[var(--color-error-light)]',
      border: 'border-[var(--color-error)]',
      icon: 'text-[var(--color-error)]',
      text: 'text-[var(--color-error-dark)]'
    },
    warning: {
      bg: 'bg-[var(--color-warning-light)]',
      border: 'border-[var(--color-warning)]',
      icon: 'text-[var(--color-warning)]',
      text: 'text-[var(--color-warning-dark)]'
    },
    info: {
      bg: 'bg-[var(--color-info-light)]',
      border: 'border-[var(--color-info)]',
      icon: 'text-[var(--color-info)]',
      text: 'text-[var(--color-info-dark)]'
    }
  };

  const Icon = icons[toast.type];
  const color = colors[toast.type];

  if (!isVisible) return null;

  return (
    <div
      className={`${color.bg} ${color.border} border rounded-lg shadow-lg p-4 min-w-[300px] max-w-[500px] transition-all duration-300 ${
        isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'
      }`}
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 ${color.icon} mt-0.5 flex-shrink-0`} />
        <div className="flex-1 min-w-0">
          <div className={`font-medium ${color.text} mb-1`}>
            {toast.title}
          </div>
          {toast.message && (
            <div className="text-sm text-[var(--color-text-secondary)]">
              {toast.message}
            </div>
          )}
          {toast.action && (
            <button
              onClick={toast.action.onClick}
              className="mt-2 text-sm font-medium underline"
            >
              {toast.action.label}
            </button>
          )}
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(() => onClose(toast.id), 300);
          }}
          className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors flex-shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

interface ToastContainerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onClose }) => {
  return (
    <div className="fixed top-4 right-4 z-[10000] flex flex-col gap-2">
      {toasts.map(toast => (
        <ToastComponent key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  );
};
