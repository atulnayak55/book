import { useMemo, useState, type ReactNode } from "react";

import { getLocale, translations, type Language, type TranslationParams } from "./translations";
import { I18nContext, type I18nContextValue } from "./useI18n";

const LANGUAGE_STORAGE_KEY = "lebooks_language";

function readInitialLanguage(): Language {
  if (typeof window === "undefined") {
    return "en";
  }

  const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
  return stored === "it" ? "it" : "en";
}

function interpolate(template: string, params?: TranslationParams): string {
  if (!params) {
    return template;
  }

  return template.replace(/\{(\w+)\}/g, (_, key: string) => String(params[key] ?? `{${key}}`));
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => readInitialLanguage());

  function setLanguage(nextLanguage: Language) {
    setLanguageState(nextLanguage);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(LANGUAGE_STORAGE_KEY, nextLanguage);
    }
  }

  const value = useMemo<I18nContextValue>(() => {
    return {
      language,
      locale: getLocale(language),
      setLanguage,
      t(key, params) {
        const template = translations[language][key] ?? translations.en[key] ?? key;
        return interpolate(template, params);
      },
    };
  }, [language]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
