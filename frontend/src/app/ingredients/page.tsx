'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useLanguage } from '../context/LanguageContext';
import styles from './ingredients.module.css';

interface Ingredient {
  id: string;
  off_id: string;
  name: string;
  names: Record<string, string>;
  vegan: boolean | null;
  vegetarian: boolean | null;
  custom: boolean;
  wikidata_id?: string;
}

export default function IngredientsPage() {
  const { language, getDisplayName } = useLanguage();
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string>('');
  const [searching, setSearching] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  // Debounce search
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  const fetchIngredients = useCallback(async (query?: string, append: boolean = false) => {
    try {
      if (append) {
        setLoadingMore(true);
      } else {
        setSearching(true);
      }
      setError('');
      
      // Build API URL with search parameter
      const params = new URLSearchParams();
      params.append('language', language);
      params.append('limit', '100');
      
      if (append) {
        // For "Load More", skip already loaded items
        params.append('skip', ingredients.length.toString());
      }
      
      if (query && query.trim()) {
        params.append('search', query.trim());
      }
      
      const response = await fetch(`/api/v2/ingredients/?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des ingrédients');
      }
      
      const data = await response.json();
      console.log('Ingredients loaded:', data.length, append ? '(appended)' : '(new)');
      
      if (append) {
        setIngredients(prev => [...prev, ...data]);
        // If we got fewer results than limit, no more to load
        setHasMore(data.length >= 100);
      } else {
        setIngredients(data || []);
        setHasMore(data.length >= 100);
      }
    } catch (err) {
      console.error('Error fetching ingredients:', err);
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setSearching(false);
      setLoading(false);
      setLoadingMore(false);
    }
  }, [language, ingredients.length]);

  // Fetch total count on mount
  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch('/api/v2/ingredients/stats/summary');
        if (response.ok) {
          const stats = await response.json();
          setTotalCount(stats.total || 0);
        }
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      }
    }
    fetchStats();
  }, []);

  // Handle search and language change with debounce
  useEffect(() => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    const timeout = setTimeout(() => {
      fetchIngredients(searchTerm);
    }, 500); // 500ms debounce

    setSearchTimeout(timeout);

    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [searchTerm, language, fetchIngredients]);

  // Get emoji based on ingredient type
  const getIngredientEmoji = (ingredient: Ingredient): string => {
    if (ingredient.vegan) return '🌱';
    if (ingredient.vegetarian) return '🥬';
    
    // Try to infer from off_id
    const id = ingredient.off_id.toLowerCase();
    if (id.includes('fruit')) return '🍎';
    if (id.includes('vegetable') || id.includes('legume')) return '🥕';
    if (id.includes('meat') || id.includes('beef') || id.includes('pork') || id.includes('chicken')) return '🍖';
    if (id.includes('fish') || id.includes('seafood')) return '🐟';
    if (id.includes('dairy') || id.includes('milk') || id.includes('cheese') || id.includes('yogurt')) return '🥛';
    if (id.includes('grain') || id.includes('cereal') || id.includes('wheat')) return '🌾';
    if (id.includes('nut') || id.includes('almond') || id.includes('walnut')) return '🥜';
    if (id.includes('spice') || id.includes('herb')) return '🌿';
    if (id.includes('oil')) return '🫒';
    if (id.includes('sugar') || id.includes('honey')) return '🍯';
    
    return '🍽️';
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <Link href="/" className={styles.backButton}>
            ← Accueil
          </Link>
          <h1>🥕 Ingrédients Disponibles</h1>
          <p>
            {searchTerm 
              ? `${ingredients.length} résultat${ingredients.length > 1 ? 's' : ''} trouvé${ingredients.length > 1 ? 's' : ''}`
              : `Base de données: ${totalCount.toLocaleString('fr-FR')} ingrédients`
            }
          </p>
        </div>
      </header>

      <div className={styles.content}>
        <div className={styles.filters}>
          <div className={styles.searchBox}>
            <div className={styles.searchInputWrapper}>
              <input
                type="text"
                placeholder="Rechercher un ingrédient (ex: tomate, olive, fromage)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={styles.searchInput}
              />
              {searching && (
                <div className={styles.searchSpinner}></div>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className={styles.error}>
            <p>❌ {error}</p>
          </div>
        )}

        {loading ? (
          <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <p>Chargement des ingrédients...</p>
          </div>
        ) : (
          <div className={styles.ingredientGrid}>
            {ingredients.map(ingredient => {
              const displayName = getDisplayName(ingredient.names);
              const altName = language === 'fr' ? ingredient.names['en'] : ingredient.names['fr'];
              const emoji = getIngredientEmoji(ingredient);
              
              return (
                <Link 
                  key={ingredient.id} 
                  href={`/ingredients/${encodeURIComponent(ingredient.off_id)}`}
                  className={styles.ingredientCard}
                >
                  <div className={styles.ingredientImageWrapper}>
                    <div className={styles.ingredientPlaceholder}>
                      {emoji}
                    </div>
                  </div>
                  
                  <div className={styles.ingredientInfo}>
                    <span className={styles.ingredientName}>{displayName}</span>
                    {altName && altName !== displayName && (
                      <span className={styles.ingredientNameEn}>{altName}</span>
                    )}
                    <div className={styles.ingredientBadges}>
                      {ingredient.vegan && (
                        <span className={styles.badge} title="Vegan">🌱</span>
                      )}
                      {ingredient.vegetarian && !ingredient.vegan && (
                        <span className={styles.badge} title="Végétarien">🥬</span>
                      )}
                      {ingredient.custom && (
                        <span className={styles.badgeCustom} title="Ingrédient personnalisé">⭐</span>
                      )}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        {!loading && !error && ingredients.length === 0 && (
          <div className={styles.empty}>
            <p>Aucun ingrédient trouvé</p>
            {searchTerm && (
              <button 
                onClick={() => setSearchTerm('')}
                className={styles.clearButton}
              >
                Effacer la recherche
              </button>
            )}
          </div>
        )}

        {/* Load More Button */}
        {!loading && !error && ingredients.length > 0 && hasMore && (
          <div className={styles.loadMoreContainer}>
            <button 
              onClick={() => fetchIngredients(searchTerm, true)}
              className={styles.loadMoreButton}
              disabled={loadingMore}
            >
              {loadingMore ? (
                <>
                  <div className={styles.smallSpinner}></div>
                  Chargement...
                </>
              ) : (
                <>
                  Charger plus d'ingrédients
                  <span className={styles.loadMoreHint}>
                    ({ingredients.length} / {searchTerm ? '?' : totalCount.toLocaleString('fr-FR')})
                  </span>
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
