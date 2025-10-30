'use client'

import Link from 'next/link'
import styles from './wine-form.module.css'

export default function NewWineSelectionPage() {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1> Ajouter un vin à votre cellier</h1>
        <Link href="/cellier">
          <button className={styles.backButton}> Retour au cellier</button>
        </Link>
      </div>

      <div className={styles.selectionGrid}>
        <Link href="/cellier/wines/new/ai" className={styles.selectionCard}>
          <div className={styles.selectionIcon}></div>
          <h2 className={styles.selectionTitle}>Extraction AI</h2>
          <p className={styles.selectionDescription}>
            Prenez une photo de l'étiquette du vin et laissez l'IA extraire 
            automatiquement toutes les informations : nom, producteur, millésime, région, etc.
          </p>
          <div className={styles.selectionFeatures}>
            <span className={styles.feature}> Photo de l'étiquette</span>
            <span className={styles.feature}> Extraction automatique</span>
            <span className={styles.feature}> Rapide et précis</span>
            <span className={styles.feature}> Révision possible</span>
          </div>
          <div className={styles.selectionButton}>
            Utiliser l'IA 
          </div>
        </Link>

        <Link href="/cellier/wines/new/manual" className={styles.selectionCard}>
          <div className={styles.selectionIcon}></div>
          <h2 className={styles.selectionTitle}>Saisie manuelle</h2>
          <p className={styles.selectionDescription}>
            Entrez manuellement les informations du vin via un formulaire détaillé.
            Idéal si vous connaissez déjà tous les détails ou pour des vins spéciaux.
          </p>
          <div className={styles.selectionFeatures}>
            <span className={styles.feature}> Formulaire complet</span>
            <span className={styles.feature}> Contrôle total</span>
            <span className={styles.feature}> Photo de bouteille</span>
            <span className={styles.feature}> Notes personnalisées</span>
          </div>
          <div className={styles.selectionButton}>
            Saisir manuellement 
          </div>
        </Link>
      </div>

      <div className={styles.infoSection}>
        <h3 className={styles.infoTitle}>Quelle méthode choisir ?</h3>
        <div className={styles.comparisonGrid}>
          <div className={styles.comparisonCard}>
            <h4> Extraction AI</h4>
            <p>
              <strong>Idéal pour :</strong> Ajouter rapidement de nouveaux vins à votre cellier.
              Prenez simplement une photo de l'étiquette et l'IA s'occupe du reste.
              Particulièrement utile pour les vins avec toutes les informations sur l'étiquette.
            </p>
          </div>
          <div className={styles.comparisonCard}>
            <h4> Saisie manuelle</h4>
            <p>
              <strong>Idéal pour :</strong> Quand vous voulez un contrôle total sur les informations,
              pour les vins anciens ou rares, ou si vous avez déjà toutes les informations
              et préférez les entrer vous-même. Vous pouvez aussi ajouter une photo de la bouteille.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
