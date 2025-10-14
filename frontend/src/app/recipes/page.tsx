'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import styles from './recipes.module.css'

interface Recipe {
  id: string
  title: string
  description?: string
  category?: string
  cuisine?: string
  difficulty_level?: string
  prep_time?: number
  cook_time?: number
  total_time?: number
  servings?: number
  image_url?: string
  ingredient_count?: number
  has_structured_ingredients?: boolean
}

type CardSize = 'small' | 'medium' | 'large'
type SortOption = 'name' | 'time' | 'difficulty' | 'recent'
type ViewMode = 'grid' | 'list'

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // UI state
  const [searchTerm, setSearchTerm] = useState('')
  const [cardSize, setCardSize] = useState<CardSize>('medium')
  const [sortBy, setSortBy] = useState<SortOption>('name')
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedCuisine, setSelectedCuisine] = useState<string>('all')

  useEffect(() => {
    async function fetchRecipes() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/recipes/`)
        
        if (!response.ok) {
          throw new Error('Failed to fetch recipes')
        }
        
        const data = await response.json()
        setRecipes(data)
        setFilteredRecipes(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchRecipes()
  }, [])

  // Filter and sort recipes
  useEffect(() => {
    let filtered = [...recipes]

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(recipe =>
        recipe.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        recipe.description?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(recipe => recipe.category === selectedCategory)
    }

    // Cuisine filter
    if (selectedCuisine !== 'all') {
      filtered = filtered.filter(recipe => recipe.cuisine === selectedCuisine)
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.title.localeCompare(b.title)
        case 'time':
          return (a.total_time || 0) - (b.total_time || 0)
        case 'difficulty':
          const difficultyOrder: { [key: string]: number } = { 'Facile': 1, 'Moyen': 2, 'Difficile': 3 }
          return (difficultyOrder[a.difficulty_level || ''] || 0) - (difficultyOrder[b.difficulty_level || ''] || 0)
        case 'recent':
          return 0 // Would need created_at field
        default:
          return 0
      }
    })

    setFilteredRecipes(filtered)
  }, [recipes, searchTerm, selectedCategory, selectedCuisine, sortBy])

  // Get unique categories and cuisines
  const categories = ['all', ...Array.from(new Set(recipes.map(r => r.category).filter(Boolean)))]
  const cuisines = ['all', ...Array.from(new Set(recipes.map(r => r.cuisine).filter(Boolean)))]

  if (loading) {
    return (
      <div className={styles.container}>
        <h1>Chargement des recettes...</h1>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.container}>
        <h1>Erreur</h1>
        <p>{error}</p>
        <Link href="/" className={styles.button}>Retour à l'accueil</Link>
      </div>
    )
  }

  const getDifficultyLabel = (level?: string) => {
    if (!level) return null
    const colors: { [key: string]: string } = {
      'Facile': '#4caf50',
      'Moyen': '#ff9800',
      'Difficile': '#f44336'
    }
    return (
      <span className={styles.difficultyBadge} style={{ backgroundColor: colors[level] || '#999' }}>
        {level}
      </span>
    )
  }

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <div className={styles.headerTop}>
          <h1>Bibliothèque de recettes</h1>
          <Link href="/" className={styles.backButton}>← Retour</Link>
        </div>
        <div className={styles.recipeCount}>
          {filteredRecipes.length} {filteredRecipes.length === 1 ? 'recette' : 'recettes'}
          {filteredRecipes.length !== recipes.length && ` sur ${recipes.length}`}
        </div>
      </header>

      {/* Toolbar */}
      <div className={styles.toolbar}>
        {/* Search */}
        <div className={styles.searchBox}>
          <input
            type="text"
            placeholder="Rechercher une recette..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles.searchInput}
          />
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')}
              className={styles.clearButton}
              type="button"
            >
              ×
            </button>
          )}
        </div>

        {/* Filters */}
        <div className={styles.filters}>
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            className={styles.select}
          >
            <option value="all">Toutes les catégories</option>
            {categories.filter(c => c !== 'all').map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>

          <select 
            value={selectedCuisine} 
            onChange={(e) => setSelectedCuisine(e.target.value)}
            className={styles.select}
          >
            <option value="all">Toutes les cuisines</option>
            {cuisines.filter(c => c !== 'all').map(cuisine => (
              <option key={cuisine} value={cuisine}>{cuisine}</option>
            ))}
          </select>

          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className={styles.select}
          >
            <option value="name">Trier par nom</option>
            <option value="time">Trier par temps</option>
            <option value="difficulty">Trier par difficulté</option>
          </select>
        </div>

        {/* View Controls */}
        <div className={styles.viewControls}>
          <div className={styles.buttonGroup}>
            <button 
              className={`${styles.sizeButton} ${cardSize === 'small' ? styles.active : ''}`}
              onClick={() => setCardSize('small')}
              title="Petites cartes"
              type="button"
            >
              S
            </button>
            <button 
              className={`${styles.sizeButton} ${cardSize === 'medium' ? styles.active : ''}`}
              onClick={() => setCardSize('medium')}
              title="Cartes moyennes"
              type="button"
            >
              M
            </button>
            <button 
              className={`${styles.sizeButton} ${cardSize === 'large' ? styles.active : ''}`}
              onClick={() => setCardSize('large')}
              title="Grandes cartes"
              type="button"
            >
              L
            </button>
          </div>

          <div className={styles.buttonGroup}>
            <button 
              className={`${styles.viewButton} ${viewMode === 'grid' ? styles.active : ''}`}
              onClick={() => setViewMode('grid')}
              title="Grille"
              type="button"
            >
              ⊞
            </button>
            <button 
              className={`${styles.viewButton} ${viewMode === 'list' ? styles.active : ''}`}
              onClick={() => setViewMode('list')}
              title="Liste"
              type="button"
            >
              ☰
            </button>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {recipes.length === 0 ? (
        <div className={styles.empty}>
          <p>Aucune recette disponible pour le moment.</p>
          <Link href="/upload" className={styles.button}>
            Télécharger votre première recette
          </Link>
        </div>
      ) : filteredRecipes.length === 0 ? (
        <div className={styles.empty}>
          <p>Aucune recette ne correspond à vos critères.</p>
          <button 
            onClick={() => {
              setSearchTerm('')
              setSelectedCategory('all')
              setSelectedCuisine('all')
            }}
            className={styles.button}
            type="button"
          >
            Réinitialiser les filtres
          </button>
        </div>
      ) : (
        <div className={`${styles.recipeGrid} ${styles[`grid-${cardSize}`]} ${styles[`view-${viewMode}`]}`}>
          {filteredRecipes.map((recipe) => (
            <div key={recipe.id} className={styles.recipeCard}>
              {/* Image Placeholder */}
              <div className={styles.cardImage}>
                {recipe.image_url ? (
                  <img src={recipe.image_url} alt={recipe.title} />
                ) : (
                  <div className={styles.imagePlaceholder}>
                    <span>📷</span>
                  </div>
                )}
                {recipe.has_structured_ingredients && (
                  <span className={styles.structuredBadge} title="Ingrédients structurés">
                    ✓
                  </span>
                )}
              </div>

              {/* Card Content */}
              <div className={styles.cardContent}>
                <div className={styles.cardHeader}>
                  <h2 className={styles.cardTitle}>{recipe.title}</h2>
                  {getDifficultyLabel(recipe.difficulty_level)}
                </div>

                {recipe.description && (
                  <p className={styles.cardDescription}>{recipe.description}</p>
                )}
                
                {/* Tags */}
                <div className={styles.cardTags}>
                  {recipe.category && <span className={styles.tag}>{recipe.category}</span>}
                  {recipe.cuisine && <span className={styles.tag}>{recipe.cuisine}</span>}
                </div>
                
                {/* Info */}
                <div className={styles.cardInfo}>
                  {recipe.total_time ? (
                    <span title="Temps total">⏱️ {recipe.total_time} min</span>
                  ) : recipe.prep_time ? (
                    <span title="Temps de préparation">⏱️ {recipe.prep_time} min</span>
                  ) : null}
                  {recipe.servings && <span title="Portions">👥 {recipe.servings}</span>}
                  {recipe.ingredient_count && (
                    <span title="Nombre d'ingrédients">🥕 {recipe.ingredient_count}</span>
                  )}
                </div>

                {/* Actions */}
                <div className={styles.cardActions}>
                  <Link href={`/recipes/${recipe.id}`} className={styles.viewLink}>
                    Voir la recette →
                  </Link>
                  <div className={styles.actionButtons}>
                    <Link 
                      href={`/admin/recipes/${recipe.id}`} 
                      className={styles.editButton}
                      title="Modifier"
                    >
                      ✎
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
