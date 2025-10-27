'use client'

import Link from 'next/link'
import { useAuth } from '../../../contexts/AuthContext'
import styles from './new-recipe.module.css'

export default function NewRecipePage() {
  const { user } = useAuth()

  // Check if user can add recipes
  const canAddRecipe = user && (user.role === 'collaborator' || user.role === 'admin')

  if (!canAddRecipe) {
    return (
      <div className={styles.container}>
        <div className={styles.card}>
          <h1 className={styles.title}>🔒 Accès Restreint</h1>
          <p className={styles.message}>
            Vous devez être connecté avec un compte collaborateur ou administrateur pour ajouter des recettes.
          </p>
          <div className={styles.actions}>
            <Link href="/login" className={styles.button}>
              Se connecter
            </Link>
            <Link href="/" className={styles.buttonSecondary}>
              Retour à l'accueil
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Ajouter une recette</h1>
        <Link href="/" className={styles.backButton}>← Retour</Link>
      </header>

      <div className={styles.optionsGrid}>
        {/* Option 1: Manual Entry */}
        <Link href="/recipes/new/manual" className={styles.optionCard}>
          <div className={styles.optionIcon}>✍️</div>
          <h2 className={styles.optionTitle}>Saisie manuelle</h2>
          <p className={styles.optionDescription}>
            Créez une recette en remplissant un formulaire détaillé avec tous les champs : 
            ingrédients structurés, instructions, temps de préparation, etc.
          </p>
          <div className={styles.optionFeatures}>
            <span className={styles.feature}>✓ Ingrédients structurés</span>
            <span className={styles.feature}>✓ Instructions détaillées</span>
            <span className={styles.feature}>✓ Équipement requis</span>
            <span className={styles.feature}>✓ Métadonnées complètes</span>
          </div>
          <div className={styles.optionButton}>
            Créer manuellement →
          </div>
        </Link>

        {/* Option 2: OCR Upload */}
        <Link href="/upload" className={styles.optionCard}>
          <div className={styles.optionIcon}>📸</div>
          <h2 className={styles.optionTitle}>Importer une photo</h2>
          <p className={styles.optionDescription}>
            Prenez une photo d'une recette papier et laissez notre système OCR 
            extraire automatiquement le texte pour vous.
          </p>
          <div className={styles.optionFeatures}>
            <span className={styles.feature}>✓ Scan automatique</span>
            <span className={styles.feature}>✓ Extraction de texte</span>
            <span className={styles.feature}>✓ Rapide et facile</span>
            <span className={styles.feature}>✓ Révision après import</span>
          </div>
          <div className={styles.optionButton}>
            Importer une image →
          </div>
        </Link>
      </div>

      {/* Info Section */}
      <div className={styles.infoSection}>
        <h3 className={styles.infoTitle}>Quelle méthode choisir ?</h3>
        <div className={styles.comparisonGrid}>
          <div className={styles.comparisonCard}>
            <h4>✍️ Saisie manuelle</h4>
            <p>
              <strong>Idéal pour :</strong> Les recettes que vous créez vous-même, 
              les recettes trouvées en ligne, ou quand vous voulez un contrôle total 
              sur la structure et le format.
            </p>
          </div>
          <div className={styles.comparisonCard}>
            <h4>📸 Import photo</h4>
            <p>
              <strong>Idéal pour :</strong> Les recettes papier (livres, magazines, 
              fiches manuscrites), pour gagner du temps sur la saisie, ou pour 
              numériser rapidement votre collection.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
