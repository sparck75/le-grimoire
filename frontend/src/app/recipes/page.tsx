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
  prep_time?: number
  cook_time?: number
  servings?: number
}

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchRecipes()
  }, [])

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

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Bibliothèque de recettes</h1>
        <Link href="/" className={styles.backButton}>← Retour</Link>
      </header>

      {recipes.length === 0 ? (
        <div className={styles.empty}>
          <p>Aucune recette disponible pour le moment.</p>
          <Link href="/upload" className={styles.button}>
            Télécharger votre première recette
          </Link>
        </div>
      ) : (
        <div className={styles.grid}>
          {recipes.map((recipe) => (
            <div key={recipe.id} className={styles.card}>
              <h2>{recipe.title}</h2>
              {recipe.description && <p>{recipe.description}</p>}
              
              <div className={styles.meta}>
                {recipe.category && <span className={styles.tag}>{recipe.category}</span>}
                {recipe.cuisine && <span className={styles.tag}>{recipe.cuisine}</span>}
              </div>
              
              <div className={styles.info}>
                {recipe.prep_time && <span>⏱️ {recipe.prep_time} min</span>}
                {recipe.servings && <span>👥 {recipe.servings} portions</span>}
              </div>
              
              <Link href={`/recipes/${recipe.id}`} className={styles.viewButton}>
                Voir la recette →
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
