import Link from 'next/link'
import styles from './page.module.css'

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>Le Grimoire</h1>
        <p className={styles.description}>
          Extraire, sauvegarder et partager des recettes de cuisine grâce à l'OCR
        </p>
        
        <div className={styles.features}>
          <div className={styles.feature}>
            <h2>📸 OCR de recettes</h2>
            <p>Téléchargez des images de recettes et extrayez automatiquement le texte</p>
          </div>
          
          <div className={styles.feature}>
            <h2>🛒 Listes d'achats intelligentes</h2>
            <p>Générez des listes d'achats avec les spéciaux d'IGA et Metro</p>
          </div>
          
          <div className={styles.feature}>
            <h2>📚 Bibliothèque de recettes</h2>
            <p>Consultez et sauvegardez vos recettes préférées</p>
          </div>
        </div>
        
        <div className={styles.actions}>
          <Link href="/recipes" className={styles.button}>
            Voir les recettes
          </Link>
          <Link href="/upload" className={styles.buttonSecondary}>
            Télécharger une recette
          </Link>
        </div>
      </div>
    </main>
  )
}
