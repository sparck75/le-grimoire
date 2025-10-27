'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import styles from './recipe-detail.module.css';

interface Recipe {
  id: string;
  title: string;
  description: string | null;
  ingredients: string[];
  equipment: string[];
  instructions: string;
  servings: number | null;
  prep_time: number | null;
  cook_time: number | null;
  total_time: number | null;
  category: string | null;
  cuisine: string | null;
  image_url: string | null;
}

interface ShoppingListItem {
  id: string;
  ingredient_name: string;
  quantity: number | null;
  unit: string | null;
  checked: boolean;
  recipe_title: string;
}

export default function RecipeDetailPage() {
  const params = useParams();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addedToList, setAddedToList] = useState(false);
  const [addedIngredients, setAddedIngredients] = useState<Set<number>>(new Set());
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  function addIngredientToList(ingredient: string, index: number) {
    if (!recipe) return;

    // Get existing shopping list
    const stored = localStorage.getItem('shoppingList');
    let shoppingList: ShoppingListItem[] = [];
    if (stored) {
      try {
        shoppingList = JSON.parse(stored);
      } catch (e) {
        console.error('Error parsing shopping list:', e);
      }
    }

    // Check if ingredient already exists
    const exists = shoppingList.some((item: ShoppingListItem) => 
      item.ingredient_name === ingredient && item.recipe_title === recipe.title
    );

    if (exists) {
      setToastMessage('⚠️ Cet ingrédient est déjà dans votre liste!');
      setTimeout(() => setToastMessage(null), 3000);
      return;
    }

    // Add single ingredient
    const newItem = {
      id: `${recipe.id}-${index}-${Date.now()}`,
      ingredient_name: ingredient,
      quantity: null,
      unit: null,
      checked: false,
      recipe_title: recipe.title
    };

    const updatedList = [...shoppingList, newItem];
    localStorage.setItem('shoppingList', JSON.stringify(updatedList));

    // Dispatch custom event to update navigation badge
    window.dispatchEvent(new Event('shoppingListUpdated'));

    // Show temporary feedback for this specific ingredient
    setAddedIngredients((prev: Set<number>) => new Set(prev).add(index));
    setTimeout(() => {
      setAddedIngredients((prev: Set<number>) => {
        const newSet = new Set(prev);
        newSet.delete(index);
        return newSet;
      });
    }, 2000);

    // Show toast notification
    setToastMessage(`✓ "${ingredient}" ajouté à votre liste!`);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  }

  function addAllToShoppingList() {
    if (!recipe) return;

    // Get existing shopping list
    const stored = localStorage.getItem('shoppingList');
    let shoppingList: ShoppingListItem[] = [];
    if (stored) {
      try {
        shoppingList = JSON.parse(stored);
      } catch (e) {
        console.error('Error parsing shopping list:', e);
      }
    }

    // Filter out ingredients that already exist
    const newItems = recipe.ingredients
      .filter((ingredient: string) => 
        !shoppingList.some((item: ShoppingListItem) => 
          item.ingredient_name === ingredient && item.recipe_title === recipe.title
        )
      )
      .map((ingredient: string, index: number) => ({
        id: `${recipe.id}-${index}-${Date.now()}`,
        ingredient_name: ingredient,
        quantity: null,
        unit: null,
        checked: false,
        recipe_title: recipe.title
      }));

    if (newItems.length === 0) {
      setToastMessage('⚠️ Tous les ingrédients sont déjà dans votre liste!');
      setTimeout(() => setToastMessage(null), 3000);
      return;
    }

    const updatedList = [...shoppingList, ...newItems];
    localStorage.setItem('shoppingList', JSON.stringify(updatedList));

    // Dispatch custom event to update navigation badge
    window.dispatchEvent(new Event('shoppingListUpdated'));

    setAddedToList(true);
    setTimeout(() => setAddedToList(false), 3000);

    // Show toast notification
    setToastMessage(`✓ ${newItems.length} ingrédient${newItems.length > 1 ? 's' : ''} ajouté${newItems.length > 1 ? 's' : ''} à votre liste!`);
    setTimeout(() => setToastMessage(null), 3000);
  }

  useEffect(() => {
    async function fetchRecipe() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v2/recipes/${params.id}`);
        
        if (!response.ok) {
          throw new Error('Recette non trouvée');
        }
        
        const data = await response.json();
        setRecipe(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Une erreur est survenue');
      } finally {
        setLoading(false);
      }
    }

    if (params.id) {
      fetchRecipe();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Chargement de la recette...</p>
        </div>
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h1>❌ {error || 'Recette non trouvée'}</h1>
          <Link href="/recipes" className={styles.backButton}>
            ← Retour aux recettes
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link href="/recipes" className={styles.backButton}>
          ← Retour aux recettes
        </Link>
        <Link href="/" className={styles.homeButton}>
          🏠 Accueil
        </Link>
      </div>

      <div className={styles.recipeCard}>
        {/* Recipe Header */}
        <div className={styles.recipeHeader}>
          <div className={styles.titleSection}>
            <h1 className={styles.title}>{recipe.title}</h1>
            {recipe.description && (
              <p className={styles.description}>{recipe.description}</p>
            )}
          </div>

          {/* Meta Information */}
          <div className={styles.metaBar}>
            {recipe.category && (
              <div className={styles.metaItem}>
                <span className={styles.metaIcon}>📂</span>
                <span className={styles.metaLabel}>Catégorie</span>
                <span className={styles.metaValue}>{recipe.category}</span>
              </div>
            )}
            {recipe.cuisine && (
              <div className={styles.metaItem}>
                <span className={styles.metaIcon}>🌍</span>
                <span className={styles.metaLabel}>Cuisine</span>
                <span className={styles.metaValue}>{recipe.cuisine}</span>
              </div>
            )}
            {recipe.servings && (
              <div className={styles.metaItem}>
                <span className={styles.metaIcon}>👥</span>
                <span className={styles.metaLabel}>Portions</span>
                <span className={styles.metaValue}>{recipe.servings} pers.</span>
              </div>
            )}
          </div>

          {/* Time Information */}
          {(recipe.prep_time || recipe.cook_time || recipe.total_time) && (
            <div className={styles.timeBar}>
              {recipe.prep_time && (
                <div className={styles.timeItem}>
                  <span className={styles.timeIcon}>⏱️</span>
                  <div>
                    <div className={styles.timeLabel}>Préparation</div>
                    <div className={styles.timeValue}>{recipe.prep_time} min</div>
                  </div>
                </div>
              )}
              {recipe.cook_time && (
                <div className={styles.timeItem}>
                  <span className={styles.timeIcon}>🔥</span>
                  <div>
                    <div className={styles.timeLabel}>Cuisson</div>
                    <div className={styles.timeValue}>{recipe.cook_time} min</div>
                  </div>
                </div>
              )}
              {recipe.total_time && (
                <div className={styles.timeItem}>
                  <span className={styles.timeIcon}>⏰</span>
                  <div>
                    <div className={styles.timeLabel}>Total</div>
                    <div className={styles.timeValue}>{recipe.total_time} min</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Recipe Content */}
        <div className={styles.recipeContent}>
          {/* Left Column: Ingredients and Equipment */}
          <div className={styles.leftColumn}>
            {/* Ingredients Section */}
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>
                  <span className={styles.sectionIcon}>🥕</span>
                  Ingrédients
                </h2>
              </div>
              <div className={styles.ingredientsList}>
                {recipe.ingredients && recipe.ingredients.length > 0 ? (
                  recipe.ingredients.map((ingredient, index) => (
                    <div key={index} className={styles.ingredientItem}>
                      <span className={styles.ingredientBullet}>✓</span>
                      <span className={styles.ingredientText}>{ingredient}</span>
                      <button 
                        className={`${styles.addIngredientBtn} ${addedIngredients.has(index) ? styles.addIngredientBtnAdded : ''}`}
                        onClick={() => addIngredientToList(ingredient, index)}
                        title="Ajouter à ma liste"
                        disabled={addedIngredients.has(index)}
                      >
                        <span className={styles.addIcon}>
                          {addedIngredients.has(index) ? '✓' : '+'}
                        </span>
                      </button>
                    </div>
                  ))
                ) : (
                  <p className={styles.emptyMessage}>Aucun ingrédient spécifié</p>
                )}
              </div>
            </div>

            {/* Equipment Section */}
            {recipe.equipment && recipe.equipment.length > 0 && (
              <div className={styles.section}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <span className={styles.sectionIcon}>🔪</span>
                    Équipement
                  </h2>
                </div>
                <div className={styles.equipmentList}>
                  {recipe.equipment.map((item, index) => (
                    <div key={index} className={styles.equipmentItem}>
                      <span className={styles.equipmentBullet}>•</span>
                      <span className={styles.equipmentText}>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Instructions */}
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                <span className={styles.sectionIcon}>📝</span>
                Instructions
              </h2>
            </div>
            <div className={styles.instructions}>
              {recipe.instructions ? (
                recipe.instructions.split('\n').map((step, index) => {
                  const trimmedStep = step.trim();
                  if (!trimmedStep) return null;
                  
                  return (
                    <div key={index} className={styles.instructionStep}>
                      <div className={styles.stepNumber}>{index + 1}</div>
                      <div className={styles.stepText}>{trimmedStep}</div>
                    </div>
                  );
                })
              ) : (
                <p className={styles.emptyMessage}>Aucune instruction disponible</p>
              )}
            </div>
          </div>
        </div>

        {/* Action Footer */}
        <div className={styles.recipeFooter}>
          <button 
            className={styles.addToListButton} 
            onClick={addAllToShoppingList}
            disabled={addedToList}
          >
            {addedToList ? '✓ Ajouté!' : '🛒 Ajouter tous les ingrédients'}
          </button>
          <button className={styles.printButton} onClick={() => window.print()}>
            🖨️ Imprimer la recette
          </button>
          <Link href="/recipes" className={styles.moreButton}>
            📖 Voir plus de recettes
          </Link>
        </div>

        {/* Print Footer (only visible when printing) */}
        <div className={styles.printFooter} style={{ display: 'none' }}></div>
        
        {/* Success Message */}
        {addedToList && (
          <div className={styles.successMessage}>
            ✓ {recipe.ingredients.length} ingrédients ajoutés à votre liste d'épicerie!
          </div>
        )}
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div className={styles.toast}>
          {toastMessage}
        </div>
      )}
    </div>
  );
}
