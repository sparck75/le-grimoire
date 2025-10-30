'use client'

import Link from 'next/link'
import styles from './wine-admin.module.css'

export default function AdminNewWineSelectionPage() {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1> Ajouter un vin (Admin)</h1>
        <Link href="/admin/wines">
          <button className={styles.backButton}> Retour</button>
        </Link>
      </div>

      <div className={styles.selectionGrid}>
        <Link href="/admin/wines/new/ai" className={styles.selectionCard}>
          <div className={styles.selectionIcon}></div>
          <h2 className={styles.selectionTitle}>Extraction AI</h2>
          <p className={styles.selectionDescription}>
            Prenez une photo de l'�tiquette du vin et laissez l'IA extraire 
            automatiquement toutes les informations : nom, producteur, mill�sime, r�gion, etc.
          </p>
          <div className={styles.selectionFeatures}>
            <span className={styles.feature}> Photo de l'�tiquette</span>
            <span className={styles.feature}> Extraction automatique</span>
            <span className={styles.feature}> Rapide et pr�cis</span>
            <span className={styles.feature}> R�vision possible</span>
          </div>
          <div className={styles.selectionButton}>
            Utiliser l'IA 
          </div>
        </Link>

        <Link href="/admin/wines/new/manual" className={styles.selectionCard}>
          <div className={styles.selectionIcon}></div>
          <h2 className={styles.selectionTitle}>Saisie manuelle</h2>
          <p className={styles.selectionDescription}>
            Entrez manuellement les informations du vin via un formulaire d�taill�.
            Id�al si vous connaissez d�j� tous les d�tails ou pour des vins sp�ciaux.
          </p>
          <div className={styles.selectionFeatures}>
            <span className={styles.feature}> Formulaire complet</span>
            <span className={styles.feature}> Contr�le total</span>
            <span className={styles.feature}> Photo de bouteille</span>
            <span className={styles.feature}> Notes personnalis�es</span>
          </div>
          <div className={styles.selectionButton}>
            Saisir manuellement 
          </div>
        </Link>
      </div>

      <div className={styles.infoSection}>
        <h3 className={styles.infoTitle}> Quelle m�thode choisir ?</h3>
        <div className={styles.comparisonGrid}>
          <div className={styles.comparisonCard}>
            <h4> Extraction AI</h4>
            <p>
              <strong>Id�al pour :</strong> Ajouter rapidement de nouveaux vins au catalogue master.
              Prenez simplement une photo de l'�tiquette et l'IA s'occupe du reste.
              Particuli�rement utile pour les vins avec toutes les informations sur l'�tiquette.
            </p>
          </div>
          <div className={styles.comparisonCard}>
            <h4> Saisie manuelle</h4>
            <p>
              <strong>Id�al pour :</strong> Quand vous voulez un contr�le total sur les informations,
              pour les vins anciens ou rares, ou si vous avez d�j� toutes les informations
              et pr�f�rez les entrer vous-m�me. Vous pouvez aussi ajouter une photo de la bouteille.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
