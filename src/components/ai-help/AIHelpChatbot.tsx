/**
 * AI Help Chatbot - AI Chatbot für Fragen
 * 
 * Features:
 * - Kontextbewusste Antworten
 * - "Did you mean...?" bei Fehlern
 * - Help Center Integration
 */

import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { MessageCircle, Send, X, Minimize2, Bot, User } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  suggestions?: string[];
}

interface AIHelpChatbotProps {
  context?: {
    currentPage?: string;
    userAction?: string;
    error?: string;
  };
}

export const AIHelpChatbot: React.FC<AIHelpChatbotProps> = ({ context }) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (context?.error) {
      // Auto-suggest bei Fehlern
      setMessages([{
        id: 'error-suggestion',
        role: 'assistant',
        content: t('aiHelp.didYouMean', { error: context.error }),
        suggestions: [
          t('aiHelp.checkConnection'),
          t('aiHelp.verifyCredentials'),
          t('aiHelp.contactSupport')
        ]
      }]);
      setIsOpen(true);
    }
  }, [context, t]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simuliere AI Response (in Production: API Call)
    setTimeout(() => {
      const response: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: generateResponse(input, context),
        suggestions: generateSuggestions(input, context)
      };
      setMessages(prev => [...prev, response]);
      setIsLoading(false);
    }, 1000);
  };

  const generateResponse = (query: string, ctx?: any): string => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('install') || lowerQuery.includes('agent')) {
      return t('aiHelp.installAgentHelp');
    }
    if (lowerQuery.includes('error') || lowerQuery.includes('problem')) {
      return t('aiHelp.errorHelp');
    }
    if (lowerQuery.includes('integration') || lowerQuery.includes('connect')) {
      return t('aiHelp.integrationHelp');
    }
    
    return t('aiHelp.defaultHelp');
  };

  const generateSuggestions = (query: string, ctx?: any): string[] => {
    const suggestions: string[] = [];
    
    if (query.includes('error')) {
      suggestions.push(t('aiHelp.suggestionCheckLogs'));
      suggestions.push(t('aiHelp.suggestionRestart'));
    }
    
    return suggestions;
  };

  if (!isOpen && !isMinimized) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-[var(--color-primary)] text-white rounded-full shadow-lg hover:bg-[var(--color-primary-hover)] transition-all flex items-center justify-center z-[9999]"
        title={t('aiHelp.openChat')}
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  if (isMinimized) {
    return (
      <button
        onClick={() => {
          setIsMinimized(false);
          setIsOpen(true);
        }}
        className="fixed bottom-6 right-6 w-14 h-14 bg-[var(--color-primary)] text-white rounded-full shadow-lg hover:bg-[var(--color-primary-hover)] transition-all flex items-center justify-center z-[9999]"
        title={t('aiHelp.openChat')}
      >
        <MessageCircle className="w-6 h-6" />
        {messages.length > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-[var(--color-error)] rounded-full text-xs flex items-center justify-center">
            {messages.length}
          </span>
        )}
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg shadow-xl flex flex-col z-[9999]">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-[var(--color-primary)]" />
          <h3 className="font-semibold text-[var(--color-text-primary)]">
            {t('aiHelp.title')}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMinimized(true)}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="w-12 h-12 text-[var(--color-text-tertiary)] mx-auto mb-4" />
            <p className="text-sm text-[var(--color-text-secondary)]">
              {t('aiHelp.welcome')}
            </p>
          </div>
        )}
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 bg-[var(--color-primary)] rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-[var(--color-primary)] text-white'
                  : 'bg-[var(--color-surface)] text-[var(--color-text-primary)]'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.suggestions && msg.suggestions.length > 0 && (
                <div className="mt-2 space-y-1">
                  {msg.suggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInput(suggestion)}
                      className="block w-full text-left text-xs text-[var(--color-primary)] hover:underline"
                    >
                      • {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 bg-[var(--color-text-tertiary)] rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-[var(--color-primary)] rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-[var(--color-surface)] rounded-lg p-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-[var(--color-text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[var(--color-border)]">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={t('aiHelp.placeholder')}
            className="flex-1 px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] outline-none focus:border-[var(--color-primary)]"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-md hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
