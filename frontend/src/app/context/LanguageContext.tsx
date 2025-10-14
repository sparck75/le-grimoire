'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Language = 'fr' | 'en';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  getDisplayName: (names: Record<string, string>) => string;
  t: (key: string) => string;
}

// Translation dictionary
const translations: Record<Language, Record<string, string>> = {
  fr: {
    'home': 'Accueil',
    'recipes': 'Recettes',
    'ingredients': 'Ingrédients',
    'shopping_list': "Liste d'Épicerie",
    'admin': 'Admin',
    'search_placeholder': 'Rechercher un ingrédient (ex: tomate, olive, fromage)...',
    'loading': 'Chargement...',
    'error': 'Erreur',
    'no_results': 'Aucun résultat trouvé',
    'load_more': "Charger plus d'ingrédients",
    'back': 'Retour',
  },
  en: {
    'home': 'Home',
    'recipes': 'Recipes',
    'ingredients': 'Ingredients',
    'shopping_list': 'Shopping List',
    'admin': 'Admin',
    'search_placeholder': 'Search for an ingredient (e.g., tomato, olive, cheese)...',
    'loading': 'Loading...',
    'error': 'Error',
    'no_results': 'No results found',
    'load_more': 'Load more ingredients',
    'back': 'Back',
  },
};

const LanguageContext = createContext<LanguageContextType>({
  language: 'fr',
  setLanguage: () => {},
  getDisplayName: () => '',
  t: () => '',
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('fr');
  const [mounted, setMounted] = useState(false);

  // Load language preference from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem('language');
    if (stored === 'en' || stored === 'fr') {
      setLanguage(stored);
    }
  }, []);

  // Save language preference to localStorage
  useEffect(() => {
    if (mounted) {
      localStorage.setItem('language', language);
    }
  }, [language, mounted]);

  // Helper function to get display name with fallback logic
  const getDisplayName = (names: Record<string, string>): string => {
    if (!names) return '';
    
    // Priority: Selected language → Other language → Any available → empty
    if (language === 'fr') {
      return names.fr || names.en || Object.values(names)[0] || '';
    } else {
      return names.en || names.fr || Object.values(names)[0] || '';
    }
  };

  // Translation function
  const t = (key: string): string => {
    const langTranslations = translations[language];
    return langTranslations?.[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, getDisplayName, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export const useLanguage = () => useContext(LanguageContext);
