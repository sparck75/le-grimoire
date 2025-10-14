'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import styles from './ingredient-detail.module.css';

interface Ingredient {
  id: string;
  off_id: string;
  name: string;
  names: Record<string, string>;
  parents: string[];
  children: string[];
  properties: Record<string, string>;
  vegan: boolean | null;
  vegetarian: boolean | null;
  wikidata_id?: string;
  ciqual_food_code?: string;
  e_number?: string;
  custom: boolean;
  created_at?: string;
  updated_at?: string;
}

interface IngredientDetailProps {
  params: {
    off_id: string;
  };
}

export default function IngredientDetailPage({ params }: IngredientDetailProps) {
  const { language, getDisplayName } = useLanguage();
  const [ingredient, setIngredient] = useState<Ingredient | null>(null);
  const [parents, setParents] = useState<Ingredient[]>([]);
  const [children, setChildren] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadIngredient() {
      try {
        setLoading(true);
        const decodedOffId = decodeURIComponent(params.off_id);
        
        // Fetch main ingredient
        const response = await fetch(
          `/api/v2/ingredients/${encodeURIComponent(decodedOffId)}`
        );
        
        if (!response.ok) {
          throw new Error('Ingredient not found');
        }
        
        const data = await response.json();
        setIngredient(data);
        
        // Fetch parents
        if (data.parents && data.parents.length > 0) {
          const parentPromises = data.parents.slice(0, 5).map(async (parentId: string) => {
            try {
              const res = await fetch(
                `/api/v2/ingredients/${encodeURIComponent(parentId)}`
              );
              if (res.ok) return await res.json();
            } catch (err) {
              console.error(`Failed to fetch parent: ${parentId}`);
            }
            return null;
          });
          const loadedParents = await Promise.all(parentPromises);
          setParents(loadedParents.filter((p): p is Ingredient => p !== null));
        }
        
        // Fetch children (first 10)
        if (data.children && data.children.length > 0) {
          const childPromises = data.children.slice(0, 10).map(async (childId: string) => {
            try {
              const res = await fetch(
                `/api/v2/ingredients/${encodeURIComponent(childId)}`
              );
              if (res.ok) return await res.json();
            } catch (err) {
              console.error(`Failed to fetch child: ${childId}`);
            }
            return null;
          });
          const loadedChildren = await Promise.all(childPromises);
          setChildren(loadedChildren.filter((c): c is Ingredient => c !== null));
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Une erreur est survenue');
      } finally {
        setLoading(false);
      }
    }

    loadIngredient();
  }, [params.off_id]);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  if (error || !ingredient) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h1>❌ Erreur</h1>
          <p>{error || 'Ingrédient introuvable'}</p>
          <Link href="/ingredients" className={styles.button}>
            ← Retour aux ingrédients
          </Link>
        </div>
      </div>
    );
  }

  const displayName = getDisplayName(ingredient.names);
  const altName = language === 'fr' ? ingredient.names['en'] : ingredient.names['fr'];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <Link href="/ingredients" className={styles.backButton}>
            ← Retour aux ingrédients
          </Link>
          
          <div className={styles.titleSection}>
            <h1>{displayName}</h1>
            {altName && altName !== displayName && (
              <p className={styles.altName}>{altName}</p>
            )}
          </div>
        </div>
      </header>

      <div className={styles.content}>
        {/* Basic Info Card */}
        <div className={styles.card}>
          <h2>📋 Informations</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.label}>ID:</span>
              <code className={styles.code}>{ingredient.off_id}</code>
            </div>
            
            {ingredient.vegan !== null && (
              <div className={styles.infoItem}>
                <span className={styles.label}>Vegan:</span>
                <span className={ingredient.vegan ? styles.yes : styles.no}>
                  {ingredient.vegan ? '✓ Oui' : '✗ Non'}
                </span>
              </div>
            )}
            
            {ingredient.vegetarian !== null && (
              <div className={styles.infoItem}>
                <span className={styles.label}>Végétarien:</span>
                <span className={ingredient.vegetarian ? styles.yes : styles.no}>
                  {ingredient.vegetarian ? '✓ Oui' : '✗ Non'}
                </span>
              </div>
            )}
            
            {ingredient.e_number && (
              <div className={styles.infoItem}>
                <span className={styles.label}>Numéro E:</span>
                <span>{ingredient.e_number}</span>
              </div>
            )}
            
            <div className={styles.infoItem}>
              <span className={styles.label}>Source:</span>
              <span className={ingredient.custom ? styles.badgeCustom : styles.badgeOFF}>
                {ingredient.custom ? '⭐ Personnalisé' : '🌐 OpenFoodFacts'}
              </span>
            </div>
          </div>
        </div>

        {/* Hierarchy - Parents */}
        {parents.length > 0 && (
          <div className={styles.card}>
            <h2>⬆️ Catégories Parentes</h2>
            <p className={styles.description}>
              Ingrédients plus généraux dont {displayName} fait partie
            </p>
            <div className={styles.ingredientList}>
              {parents.map((parent) => (
                <Link
                  key={parent.id}
                  href={`/ingredients/${encodeURIComponent(parent.off_id)}`}
                  className={styles.ingredientChip}
                >
                  {parent.names[language] || parent.name}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Hierarchy - Children */}
        {children.length > 0 && (
          <div className={styles.card}>
            <h2>⬇️ Variantes Plus Spécifiques</h2>
            <p className={styles.description}>
              Types plus spécifiques de {displayName}
            </p>
            <div className={styles.ingredientList}>
              {children.map((child) => (
                <Link
                  key={child.id}
                  href={`/ingredients/${encodeURIComponent(child.off_id)}`}
                  className={styles.ingredientChip}
                >
                  {child.names[language] || child.name}
                </Link>
              ))}
              {ingredient.children.length > 10 && (
                <span className={styles.moreItems}>
                  +{ingredient.children.length - 10} de plus
                </span>
              )}
            </div>
          </div>
        )}

        {/* Available Names */}
        <div className={styles.card}>
          <h2>🌍 Noms Disponibles</h2>
          <div className={styles.namesList}>
            {Object.entries(ingredient.names)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([lang, name]) => (
                <div key={lang} className={styles.nameItem}>
                  <span className={styles.langCode}>{lang.toUpperCase()}</span>
                  <span className={styles.langName}>{name}</span>
                </div>
              ))}
          </div>
        </div>

        {/* External Links */}
        {(ingredient.wikidata_id || ingredient.ciqual_food_code) && (
          <div className={styles.card}>
            <h2>🔗 Liens Externes</h2>
            <div className={styles.linksList}>
              {ingredient.wikidata_id && (
                <a
                  href={`https://www.wikidata.org/wiki/${ingredient.wikidata_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.externalLink}
                >
                  <span>📚 Wikidata</span>
                  <span className={styles.arrow}>→</span>
                </a>
              )}
              {ingredient.ciqual_food_code && (
                <a
                  href={`https://ciqual.anses.fr/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.externalLink}
                >
                  <span>🧪 CIQUAL</span>
                  <span className={styles.arrow}>→</span>
                </a>
              )}
              {!ingredient.custom && (
                <a
                  href={`https://world.openfoodfacts.org/ingredient/${ingredient.off_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.externalLink}
                >
                  <span>🌐 OpenFoodFacts</span>
                  <span className={styles.arrow}>→</span>
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
