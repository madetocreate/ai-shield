'use client';

import React from 'react';
import { SparklesIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { AkButton } from '@/components/ui/AkButton';
import { motion } from 'framer-motion';
import type { JobStatus } from '@/lib/actions/types';

interface ActionCardProps {
  label: string;
  output: string;
  isGenerating: boolean;
  jobStatus?: JobStatus;
  error?: string;
  onAccept: () => void;
  onDiscard: () => void;
}

export const ActionCard: React.FC<ActionCardProps> = ({ 
  label, 
  output, 
  isGenerating, 
  jobStatus,
  error,
  onAccept, 
  onDiscard 
}) => {
  const isPending = isGenerating || jobStatus === 'queued' || jobStatus === 'running';
  const isFailed = jobStatus === 'failed';
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className="apple-card-strong overflow-hidden bg-white/80 border border-[var(--ak-color-accent)]/20 shadow-xl"
    >
      <div className="px-3 py-2 bg-[var(--ak-color-accent)]/5 border-b border-[var(--ak-color-accent)]/10 flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-[var(--ak-color-accent)] uppercase tracking-wider">
          <SparklesIcon className="w-3.5 h-3.5" />
          {isFailed ? 'Fehlgeschlagen' : isPending ? 'Wird vorbereitet…' : 'Vorschau'}
        </div>
        <button onClick={onDiscard} className="text-gray-400 hover:text-gray-600 transition-colors">
          <XMarkIcon className="w-4 h-4" />
        </button>
      </div>
      
      <div className="p-3">
        <p className="text-[10px] text-[var(--ak-color-text-muted)] mb-2 font-medium">Aktion: {label}</p>
        
        {isPending ? (
          <div className="space-y-2 py-4">
            <div className="h-3 bg-gray-100 rounded-full w-full animate-pulse" />
            <div className="h-3 bg-gray-100 rounded-full w-5/6 animate-pulse" />
            <div className="h-3 bg-gray-100 rounded-full w-4/6 animate-pulse" />
          </div>
        ) : isFailed ? (
          <div className="text-xs text-red-600 leading-relaxed whitespace-pre-wrap max-h-[200px] overflow-y-auto ak-scrollbar p-2 bg-red-50 rounded-lg">
            {error || 'Fehler beim Ausführen der Aktion.'}
          </div>
        ) : (
          <div className="text-xs text-[var(--ak-color-text-secondary)] leading-relaxed whitespace-pre-wrap max-h-[200px] overflow-y-auto ak-scrollbar p-2 bg-white/50 rounded-lg">
            {output}
          </div>
        )}
      </div>

      <div className="px-3 py-2 border-t border-gray-100 flex gap-2 justify-end bg-gray-50/50">
        <AkButton variant="ghost" size="sm" onClick={onDiscard}>Verwerfen</AkButton>
        <AkButton 
          variant="primary" 
          size="sm" 
          onClick={onAccept} 
          disabled={isPending || isFailed}
          leftIcon={<CheckIcon className="w-3.5 h-3.5" />}
        >
          Übernehmen
        </AkButton>
      </div>
    </motion.div>
  );
};

