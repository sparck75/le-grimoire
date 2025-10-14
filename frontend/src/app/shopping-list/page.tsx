'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import styles from './shopping-list.module.css';

interface ShoppingListItem {
  id: string;
  ingredient_name: string;
  quantity: number | null;
  unit: string | null;
  checked: boolean;
  recipe_title?: string;
}

export default function ShoppingListPage() {
  const [items, setItems] = useState<ShoppingListItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFromLocalStorage();
  }, []);

  function loadFromLocalStorage() {
    const stored = localStorage.getItem('shoppingList');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setItems(parsed);
      } catch (e) {
        console.error('Error loading shopping list:', e);
      }
    }
  }

  function saveToLocalStorage(newItems: ShoppingListItem[]) {
    localStorage.setItem('shoppingList', JSON.stringify(newItems));
    setItems(newItems);
    // Dispatch custom event to update navigation badge
    window.dispatchEvent(new Event('shoppingListUpdated'));
  }

  function toggleItem(id: string) {
    const newItems = items.map(item =>
      item.id === id ? { ...item, checked: !item.checked } : item
    );
    saveToLocalStorage(newItems);
  }

  function removeItem(id: string) {
    const newItems = items.filter(item => item.id !== id);
    saveToLocalStorage(newItems);
  }

  function clearList() {
    if (confirm('Êtes-vous sûr de vouloir vider la liste d\'épicerie ?')) {
      saveToLocalStorage([]);
    }
  }

  function clearChecked() {
    const newItems = items.filter(item => !item.checked);
    saveToLocalStorage(newItems);
  }

  const uncheckedItems = items.filter(item => !item.checked);
  const checkedItems = items.filter(item => item.checked);

  // Group items by recipe
  const groupedItems = uncheckedItems.reduce((acc, item) => {
    const recipe = item.recipe_title || 'Autres';
    if (!acc[recipe]) {
      acc[recipe] = [];
    }
    acc[recipe].push(item);
    return acc;
  }, {} as Record<string, ShoppingListItem[]>);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <Link href="/" className={styles.backButton}>
            ← Accueil
          </Link>
          <h1>🛒 Ma Liste d'Épicerie</h1>
          <p>Gérez vos courses et ajoutez des ingrédients depuis vos recettes</p>
        </div>
      </header>

      <div className={styles.content}>
        {items.length === 0 ? (
          <div className={styles.empty}>
            <div className={styles.emptyIcon}>🛒</div>
            <h2>Votre liste est vide</h2>
            <p>Ajoutez des ingrédients depuis vos recettes préférées</p>
            <Link href="/recipes" className={styles.browseButton}>
              📚 Parcourir les recettes
            </Link>
          </div>
        ) : (
          <>
            <div className={styles.actions}>
              <div className={styles.stats}>
                <span className={styles.statBadge}>
                  {uncheckedItems.length} article{uncheckedItems.length !== 1 ? 's' : ''} à acheter
                </span>
                {checkedItems.length > 0 && (
                  <span className={styles.statBadgeChecked}>
                    {checkedItems.length} article{checkedItems.length !== 1 ? 's' : ''} coché{checkedItems.length !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
              <div className={styles.actionButtons}>
                {checkedItems.length > 0 && (
                  <button onClick={clearChecked} className={styles.clearCheckedButton}>
                    🗑️ Supprimer les articles cochés
                  </button>
                )}
                <button onClick={clearList} className={styles.clearButton}>
                  ❌ Vider la liste
                </button>
              </div>
            </div>

            {/* Unchecked Items */}
            {uncheckedItems.length > 0 && (
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>À acheter</h2>
                {Object.entries(groupedItems).map(([recipe, recipeItems]) => (
                  <div key={recipe} className={styles.recipeGroup}>
                    <h3 className={styles.recipeTitle}>{recipe}</h3>
                    <div className={styles.itemsList}>
                      {recipeItems.map(item => (
                        <div key={item.id} className={styles.item}>
                          <input
                            type="checkbox"
                            checked={item.checked}
                            onChange={() => toggleItem(item.id)}
                            className={styles.checkbox}
                          />
                          <div className={styles.itemContent}>
                            <span className={styles.itemName}>{item.ingredient_name}</span>
                            {(item.quantity || item.unit) && (
                              <span className={styles.itemQuantity}>
                                {item.quantity && `${item.quantity} `}
                                {item.unit}
                              </span>
                            )}
                          </div>
                          <button
                            onClick={() => removeItem(item.id)}
                            className={styles.removeButton}
                            title="Supprimer"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Checked Items */}
            {checkedItems.length > 0 && (
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Dans le panier</h2>
                <div className={styles.checkedList}>
                  {checkedItems.map(item => (
                    <div key={item.id} className={styles.itemChecked}>
                      <input
                        type="checkbox"
                        checked={item.checked}
                        onChange={() => toggleItem(item.id)}
                        className={styles.checkbox}
                      />
                      <div className={styles.itemContent}>
                        <span className={styles.itemNameChecked}>{item.ingredient_name}</span>
                        {(item.quantity || item.unit) && (
                          <span className={styles.itemQuantity}>
                            {item.quantity && `${item.quantity} `}
                            {item.unit}
                          </span>
                        )}
                      </div>
                      <button
                        onClick={() => removeItem(item.id)}
                        className={styles.removeButton}
                        title="Supprimer"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
