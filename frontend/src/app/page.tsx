import Link from 'next/link'
import Image from 'next/image'
import styles from './page.module.css'

export default function Home() {
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
          
          <nav className={styles.nav}>
            <Link href="/recipes" className={styles.navLink}>
              📚 Recettes
            </Link>
            <Link href="/ingredients" className={styles.navLink}>
              🥕 Ingrédients
            </Link>
            <Link href="/shopping-list" className={styles.navLink}>
              � Liste d'Épicerie
            </Link>
            <Link href="/admin" className={styles.navLink}>
              ⚙️ Admin
            </Link>
          </nav>
        </header>
        
        <div className={styles.hero}>
          <h1 className={styles.title}>
            Votre Bibliothèque de<br />Recettes Personnelle
          </h1>
          <p className={styles.subtitle}>
            Organisez, partagez et découvrez vos recettes préférées en toute simplicité
          </p>
          
          <div className={styles.actions}>
            <Link href="/recipes" className={styles.button}>
              🍽️ Explorer les Recettes
            </Link>
            <Link href="/upload" className={styles.buttonSecondary}>
              ➕ Ajouter une Recette
            </Link>
          </div>
        </div>
        
      </div>
    </main>
  )
}
