/**
 * i18n Configuration - Frontend Internationalization
 * 
 * Supports: German (DE), English (EN), Spanish (ES), French (FR), Italian (IT)
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import de from './locales/de.json';
import en from './locales/en.json';
import es from './locales/es.json';
import fr from './locales/fr.json';
import it from './locales/it.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      de: { translation: de },
      en: { translation: en },
      es: { translation: es },
      fr: { translation: fr },
      it: { translation: it }
    },
    lng: localStorage.getItem('language') || 'de', // Default: Deutsch
    fallbackLng: 'de',
    interpolation: {
      escapeValue: false
    },
    react: {
      useSuspense: false
    }
  });

export default i18n;
