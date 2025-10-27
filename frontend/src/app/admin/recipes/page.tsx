'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../contexts/AuthContext';
import styles from '../admin.module.css';

interface Recipe {
  id: string;
  title: string;
  description: string | null;
  category: string | null;
  cuisine: string | null;
  difficulty_level: string | null;
  servings: number | null;
  prep_time: number | null;
  cook_time: number | null;
  total_time: number | null;
  ingredient_count: number | null;
  has_structured_ingredients: boolean;
  is_public: boolean;
  created_at?: string;
  updated_at?: string;
}

type ViewMode = 'table' | 'cards';
type SortOption = 'title' | 'category' | 'difficulty' | 'time' | 'recent';

export default function RecipesAdmin() {
  const { token, user } = useAuth();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedCuisine, setSelectedCuisine] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortOption>('recent');
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [selectedRecipes, setSelectedRecipes] = useState<Set<string>>(new Set());

  useEffect(() => {
    console.log('Token:', token ? 'present' : 'missing');
    console.log('User:', user);
    
    if (token) {
      console.log('Fetching recipes with token...');
      fetchRecipes();
    } else {
      // If no token after a delay, show error
      const timeout = setTimeout(() => {
        if (!token) {
          setError('Authentification requise. Veuillez vous connecter.');
          setLoading(false);
        }
      }, 2000);
      
      return () => clearTimeout(timeout);
    }
  }, [token]);

  async function fetchRecipes() {
    if (!token) {
      setError('Authentification requise');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };
      
      const response = await fetch('/api/admin/recipes', { headers });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRecipes(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching recipes:', err);
      setError('Erreur lors du chargement des recettes');
    } finally {
      setLoading(false);
    }
  }

  // Filter and sort recipes
  const filteredRecipes = recipes
    .filter(recipe => {
      // Search filter
      const matchesSearch = !searchTerm || 
        recipe.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (recipe.description && recipe.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (recipe.category && recipe.category.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (recipe.cuisine && recipe.cuisine.toLowerCase().includes(searchTerm.toLowerCase()));

      // Category filter
      const matchesCategory = selectedCategory === 'all' || recipe.category === selectedCategory;

      // Cuisine filter
      const matchesCuisine = selectedCuisine === 'all' || recipe.cuisine === selectedCuisine;

      // Difficulty filter
      const matchesDifficulty = selectedDifficulty === 'all' || recipe.difficulty_level === selectedDifficulty;

      // Status filter
      const matchesStatus = selectedStatus === 'all' || 
        (selectedStatus === 'public' && recipe.is_public) ||
        (selectedStatus === 'private' && !recipe.is_public) ||
        (selectedStatus === 'structured' && recipe.has_structured_ingredients);

      return matchesSearch && matchesCategory && matchesCuisine && matchesDifficulty && matchesStatus;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'category':
          return (a.category || '').localeCompare(b.category || '');
        case 'difficulty':
          const diffOrder: { [key: string]: number } = { 'Facile': 1, 'Moyen': 2, 'Difficile': 3 };
          return (diffOrder[a.difficulty_level || ''] || 0) - (diffOrder[b.difficulty_level || ''] || 0);
        case 'time':
          return (a.total_time || 0) - (b.total_time || 0);
        case 'recent':
          return (b.updated_at || b.created_at || '').localeCompare(a.updated_at || a.created_at || '');
        default:
          return 0;
      }
    });

  // Get unique values for filters
  const categories = ['all', ...Array.from(new Set(recipes.map(r => r.category).filter(Boolean)))];
  const cuisines = ['all', ...Array.from(new Set(recipes.map(r => r.cuisine).filter(Boolean)))];
  const difficulties = ['all', 'Facile', 'Moyen', 'Difficile'];

  // Calculate stats
  const stats = {
    total: recipes.length,
    public: recipes.filter(r => r.is_public).length,
    private: recipes.filter(r => !r.is_public).length,
    structured: recipes.filter(r => r.has_structured_ingredients).length,
  };

  // Bulk actions
  const toggleSelectAll = () => {
    if (selectedRecipes.size === filteredRecipes.length) {
      setSelectedRecipes(new Set());
    } else {
      setSelectedRecipes(new Set(filteredRecipes.map(r => r.id)));
    }
  };

  const toggleSelectRecipe = (id: string) => {
    const newSelected = new Set(selectedRecipes);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedRecipes(newSelected);
  };

  const getDifficultyBadge = (level: string | null) => {
    if (!level) return <span style={{ color: '#999' }}>—</span>;
    const colors: { [key: string]: string } = {
      'Facile': '#4caf50',
      'Moyen': '#ff9800',
      'Difficile': '#f44336'
    };
    return (
      <span className={styles.badge} style={{ backgroundColor: colors[level] || '#999' }}>
        {level}
      </span>
    );
  };

  if (loading) {
    return (
      <div>
        <div className={styles['admin-header']}>
          <h1>Gestion des Recettes</h1>
        </div>
        <div className={styles['loading']}>Chargement des recettes...</div>
      </div>
    );
  }

  return (
    <div>
      <div className={styles['admin-header']}>
        <h1>Gestion des Recettes</h1>
        <Link href="/admin/recipes/new" className={`${styles.btn} ${styles['btn-primary']}`}>
          ➕ Nouvelle Recette
        </Link>
      </div>

      {error && (
        <div className={styles['error-message']} style={{ 
          padding: '1rem', 
          marginBottom: '1rem', 
          backgroundColor: '#fee', 
          border: '1px solid #fcc',
          borderRadius: '8px',
          color: '#c00'
        }}>
          {error}
        </div>
      )}

      {/* Stats Dashboard */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className={styles['stat-card']}>
          <div className={styles['stat-value']}>{stats.total}</div>
          <div className={styles['stat-label']}>Total Recettes</div>
        </div>
        <div className={styles['stat-card']}>
          <div className={styles['stat-value']} style={{ color: '#10b981' }}>{stats.public}</div>
          <div className={styles['stat-label']}>Publiques</div>
        </div>
        <div className={styles['stat-card']}>
          <div className={styles['stat-value']} style={{ color: '#6b7280' }}>{stats.private}</div>
          <div className={styles['stat-label']}>Privées</div>
        </div>
        <div className={styles['stat-card']}>
          <div className={styles['stat-value']} style={{ color: '#4caf50' }}>{stats.structured}</div>
          <div className={styles['stat-label']}>Structurées</div>
        </div>
      </div>

      <div className={styles['admin-card']}>
        <div className={styles['card-header']}>
          <h2>Liste des Recettes ({filteredRecipes.length})</h2>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            {/* View Mode Toggle */}
            <div style={{ display: 'flex', background: '#f3f4f6', borderRadius: '8px', padding: '4px' }}>
              <button
                onClick={() => setViewMode('table')}
                className={`${styles.btn} ${styles['btn-sm']}`}
                style={{ 
                  background: viewMode === 'table' ? 'white' : 'transparent',
                  boxShadow: viewMode === 'table' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  padding: '0.5rem 1rem'
                }}
              >
                📋 Table
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={`${styles.btn} ${styles['btn-sm']}`}
                style={{ 
                  background: viewMode === 'cards' ? 'white' : 'transparent',
                  boxShadow: viewMode === 'cards' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  padding: '0.5rem 1rem'
                }}
              >
                🃏 Cartes
              </button>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '8px', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <input
              type="text"
              placeholder="🔍 Rechercher une recette..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={styles['search-input']}
              style={{ flex: '1', minWidth: '250px' }}
            />
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className={styles['select-input']}
            >
              <option value="all">Toutes catégories</option>
              {categories.filter(c => c !== 'all').map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>

            <select
              value={selectedCuisine}
              onChange={(e) => setSelectedCuisine(e.target.value)}
              className={styles['select-input']}
            >
              <option value="all">Toutes cuisines</option>
              {cuisines.filter(c => c !== 'all').map(cuisine => (
                <option key={cuisine} value={cuisine}>{cuisine}</option>
              ))}
            </select>

            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className={styles['select-input']}
            >
              <option value="all">Toutes difficultés</option>
              {difficulties.filter(d => d !== 'all').map(diff => (
                <option key={diff} value={diff}>{diff}</option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className={styles['select-input']}
            >
              <option value="all">Tous statuts</option>
              <option value="public">Publiques</option>
              <option value="private">Privées</option>
              <option value="structured">Structurées</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className={styles['select-input']}
            >
              <option value="recent">Plus récentes</option>
              <option value="title">Par titre</option>
              <option value="category">Par catégorie</option>
              <option value="difficulty">Par difficulté</option>
              <option value="time">Par temps</option>
            </select>
          </div>

          {/* Bulk Actions */}
          {selectedRecipes.size > 0 && (
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.75rem', background: '#e0e7ff', borderRadius: '6px' }}>
              <span style={{ fontWeight: '600' }}>{selectedRecipes.size} sélectionnée(s)</span>
              <button
                onClick={() => handleBulkDelete()}
                className={`${styles.btn} ${styles['btn-danger']} ${styles['btn-sm']}`}
              >
                🗑️ Supprimer la sélection
              </button>
              <button
                onClick={() => setSelectedRecipes(new Set())}
                className={`${styles.btn} ${styles['btn-secondary']} ${styles['btn-sm']}`}
              >
                Annuler
              </button>
            </div>
          )}
        </div>

        {/* Table View */}
        {viewMode === 'table' && (
          <div className={styles['table-container']}>
            <table className={styles['data-table']}>
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input
                      type="checkbox"
                      checked={selectedRecipes.size === filteredRecipes.length && filteredRecipes.length > 0}
                      onChange={toggleSelectAll}
                      style={{ cursor: 'pointer' }}
                    />
                  </th>
                  <th>Titre</th>
                  <th>Catégorie</th>
                  <th>Cuisine</th>
                  <th>Difficulté</th>
                  <th>Temps</th>
                  <th>Ingrédients</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecipes.length === 0 ? (
                  <tr>
                    <td colSpan={9} style={{ textAlign: 'center', padding: '2rem', color: '#999' }}>
                      {searchTerm ? 'Aucune recette trouvée' : 'Aucune recette disponible'}
                    </td>
                  </tr>
                ) : (
                  filteredRecipes.map((recipe) => (
                    <tr key={recipe.id} style={{ background: selectedRecipes.has(recipe.id) ? '#f0f9ff' : 'transparent' }}>
                      <td>
                        <input
                          type="checkbox"
                          checked={selectedRecipes.has(recipe.id)}
                          onChange={() => toggleSelectRecipe(recipe.id)}
                          style={{ cursor: 'pointer' }}
                        />
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <strong>{recipe.title}</strong>
                          {recipe.has_structured_ingredients && (
                            <span title="Ingrédients structurés" style={{ 
                              color: '#4caf50', 
                              fontWeight: 'bold',
                              fontSize: '1.1rem'
                            }}>
                              ✓
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        {recipe.category ? (
                          <span className={styles.badge}>{recipe.category}</span>
                        ) : (
                          <span style={{ color: '#999' }}>—</span>
                        )}
                      </td>
                      <td>
                        {recipe.cuisine ? (
                          <span className={styles.badge} style={{ background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                            {recipe.cuisine}
                          </span>
                        ) : (
                          <span style={{ color: '#999' }}>—</span>
                        )}
                      </td>
                      <td>
                        {getDifficultyBadge(recipe.difficulty_level)}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        {recipe.total_time ? (
                          `${recipe.total_time} min`
                        ) : recipe.prep_time || recipe.cook_time ? (
                          `${(recipe.prep_time || 0) + (recipe.cook_time || 0)} min`
                        ) : (
                          <span style={{ color: '#999' }}>—</span>
                        )}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        {recipe.ingredient_count ? (
                          <span>🥕 {recipe.ingredient_count}</span>
                        ) : (
                          <span style={{ color: '#999' }}>—</span>
                        )}
                      </td>
                      <td>
                        {recipe.is_public ? (
                          <span className={styles.badge} style={{ backgroundColor: '#10b981' }}>
                            ✓ Public
                          </span>
                        ) : (
                          <span className={styles.badge} style={{ backgroundColor: '#6b7280' }}>
                            🔒 Privé
                          </span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                          <Link
                            href={`/admin/recipes/${recipe.id}`}
                            className={`${styles.btn} ${styles['btn-secondary']}`}
                            style={{ fontSize: '0.875rem', padding: '0.25rem 0.75rem' }}
                          >
                            ✏️ Modifier
                          </Link>
                          <button
                            onClick={() => handleDelete(recipe.id, recipe.title)}
                            className={`${styles.btn} ${styles['btn-danger']}`}
                            style={{ fontSize: '0.875rem', padding: '0.25rem 0.75rem' }}
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Card View */}
        {viewMode === 'cards' && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
            gap: '1.5rem',
            padding: '1rem 0'
          }}>
            {filteredRecipes.length === 0 ? (
              <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem', color: '#999' }}>
                {searchTerm ? 'Aucune recette trouvée' : 'Aucune recette disponible'}
              </div>
            ) : (
              filteredRecipes.map((recipe) => (
                <div 
                  key={recipe.id} 
                  style={{ 
                    background: selectedRecipes.has(recipe.id) ? '#f0f9ff' : 'white',
                    border: selectedRecipes.has(recipe.id) ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    transition: 'all 0.2s',
                    cursor: 'pointer'
                  }}
                  onClick={() => toggleSelectRecipe(recipe.id)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.25rem', flex: 1 }}>{recipe.title}</h3>
                    <input
                      type="checkbox"
                      checked={selectedRecipes.has(recipe.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        toggleSelectRecipe(recipe.id);
                      }}
                      style={{ cursor: 'pointer', marginLeft: '0.5rem' }}
                    />
                  </div>

                  {recipe.description && (
                    <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '1rem' }}>
                      {recipe.description.length > 100 
                        ? recipe.description.substring(0, 100) + '...' 
                        : recipe.description
                      }
                    </p>
                  )}

                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                    {recipe.category && (
                      <span className={styles.badge}>{recipe.category}</span>
                    )}
                    {recipe.cuisine && (
                      <span className={styles.badge} style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                        {recipe.cuisine}
                      </span>
                    )}
                    {recipe.difficulty_level && getDifficultyBadge(recipe.difficulty_level)}
                    {recipe.has_structured_ingredients && (
                      <span className={styles.badge} style={{ backgroundColor: '#4caf50' }}>
                        ✓ Structuré
                      </span>
                    )}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                    {(recipe.total_time || recipe.prep_time || recipe.cook_time) && (
                      <div>
                        ⏱️ {recipe.total_time || ((recipe.prep_time || 0) + (recipe.cook_time || 0))} min
                      </div>
                    )}
                    {recipe.servings && (
                      <div>👥 {recipe.servings} pers.</div>
                    )}
                    {recipe.ingredient_count && (
                      <div>🥕 {recipe.ingredient_count} ingr.</div>
                    )}
                    <div>
                      {recipe.is_public ? (
                        <span style={{ color: '#10b981' }}>✓ Public</span>
                      ) : (
                        <span style={{ color: '#6b7280' }}>🔒 Privé</span>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem' }} onClick={(e) => e.stopPropagation()}>
                    <Link
                      href={`/admin/recipes/${recipe.id}`}
                      className={`${styles.btn} ${styles['btn-secondary']}`}
                      style={{ flex: 1, textAlign: 'center', fontSize: '0.875rem' }}
                    >
                      ✏️ Modifier
                    </Link>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(recipe.id, recipe.title);
                      }}
                      className={`${styles.btn} ${styles['btn-danger']}`}
                      style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );

  async function handleDelete(recipeId: string, recipeTitle: string) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer la recette "${recipeTitle}" ?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/recipes/${recipeId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      // Remove from selection if selected
      const newSelected = new Set(selectedRecipes);
      newSelected.delete(recipeId);
      setSelectedRecipes(newSelected);

      // Refresh the list
      fetchRecipes();
    } catch (err) {
      console.error('Error deleting recipe:', err);
      alert('Erreur lors de la suppression de la recette');
    }
  }

  async function handleBulkDelete() {
    const count = selectedRecipes.size;
    if (!confirm(`Êtes-vous sûr de vouloir supprimer ${count} recette(s) sélectionnée(s) ?`)) {
      return;
    }

    try {
      const deletePromises = Array.from(selectedRecipes).map(recipeId =>
        fetch(`/api/admin/recipes/${recipeId}`, { method: 'DELETE' })
      );

      await Promise.all(deletePromises);

      // Clear selection
      setSelectedRecipes(new Set());

      // Refresh the list
      fetchRecipes();
    } catch (err) {
      console.error('Error deleting recipes:', err);
      alert('Erreur lors de la suppression des recettes');
    }
  }
}
