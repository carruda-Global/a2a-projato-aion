import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import ptBR from './pt-BR.json';
import enUS from './en-US.json';
import esES from './es-ES.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      'pt': { translation: ptBR },
      'pt-BR': { translation: ptBR },
      'en': { translation: enUS },
      'en-US': { translation: enUS },
      'es': { translation: esES },
      'es-ES': { translation: esES },
    },
    fallbackLng: 'pt-BR',
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
