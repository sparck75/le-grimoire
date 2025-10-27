'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useAuth } from '../contexts/AuthContext'
import styles from './page.module.css'

export default function Home() {
  const { user } = useAuth()
  
  // Check if user is contributor or admin
  const canAddRecipe = user && (user.role === 'collaborator' || user.role === 'admin')
  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <header className={styles.header}>
          <div className={styles.logoContainer}>
            <Image 
              src="/logo.png" 
              alt="Le Grimoire" 
              width={80} 
              height={80}
              className={styles.logo}
              priority
            />
            <span className={styles.logoText}>Le Grimoire</span>
          </div>
        </header>
        
        <div className={styles.hero}>
          <h1 className={styles.title}>
            Votre Bibliothèque de<br />Recettes Personnelles
          </h1>
          <p className={styles.subtitle}>
            Organisez, partagez et découvrez vos recettes préférées en toute simplicité
          </p>
          
          <div className={styles.actions}>
            <Link href="/recipes" className={styles.button}>
              🍽️ Explorer les Recettes
            </Link>
            {canAddRecipe && (
              <Link href="/recipes/new" className={styles.buttonSecondary}>
                ➕ Ajouter une Recette
              </Link>
            )}
          </div>
        </div>
        
      </div>
    </main>
  )
}
