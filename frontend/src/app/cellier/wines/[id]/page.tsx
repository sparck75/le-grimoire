'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import styles from './wine-detail.module.css'

interface GrapeVariety {
  name: string
  percentage?: number
}

interface Wine {
  id: string
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  country: string
  region: string
  appellation?: string
  classification?: string
  grape_varieties: GrapeVariety[]
  alcohol_content?: number
  body?: string
  sweetness?: string
  acidity?: string
  tannins?: string
  color: string
  nose: string[]
  palate: string[]
  tasting_notes: string
  food_pairings: string[]
  purchase_date?: string
  purchase_price?: number
  purchase_location?: string
  current_quantity: number
  cellar_location?: string
  drink_from?: number
  drink_until?: number
  peak_drinking?: string
  rating?: number
  image_url?: string
  barcode?: string
}

export default function WineDetailPage() {
  const router = useRouter()
  const params = useParams()
  const wineId = params.id as string

  const [wine, setWine] = useState<Wine | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchWine()
  }, [wineId])

  async function fetchWine() {
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')

      const headers: Record<string, string> = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${apiUrl}/api/v2/wines/${wineId}`, { headers })
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Vin non trouvé')
        }
        throw new Error('Erreur lors du chargement du vin')
      }

      const data = await response.json()
      setWine(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce vin?')) {
      return
    }

    setDeleting(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')

      if (!token) {
        throw new Error('Vous devez être connecté')
      }

      const response = await fetch(`${apiUrl}/api/v2/wines/${wineId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression')
      }

      // Redirect to cellier
      router.push('/cellier')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de suppression')
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Chargement...</div>
      </div>
    )
  }

  if (error || !wine) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <p>❌ {error || 'Vin non trouvé'}</p>
          <Link href="/cellier">
            <button className={styles.backButton}>← Retour au cellier</button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link href="/cellier">
          <button className={styles.backButton}>← Retour</button>
        </Link>
        <div className={styles.actions}>
          <Link href={`/cellier/wines/${wineId}/edit`}>
            <button className={styles.editButton}>✏️ Modifier</button>
          </Link>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className={styles.deleteButton}
          >
            {deleting ? '⏳ Suppression...' : '🗑️ Supprimer'}
          </button>
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.imageSection}>
          {wine.image_url ? (
            <img src={wine.image_url} alt={wine.name} className={styles.wineImage} />
          ) : (
            <div className={styles.placeholderImage}>🍷</div>
          )}
        </div>

        <div className={styles.details}>
          <h1 className={styles.title}>{wine.name}</h1>
          
          {wine.producer && (
            <p className={styles.producer}>{wine.producer}</p>
          )}

          <div className={styles.badges}>
            <span className={styles.badge}>{wine.wine_type}</span>
            {wine.vintage && <span className={styles.badge}>{wine.vintage}</span>}
            {wine.classification && <span className={styles.badge}>{wine.classification}</span>}
          </div>

          {wine.rating && (
            <div className={styles.rating}>
              {'⭐'.repeat(Math.round(wine.rating))} ({wine.rating.toFixed(1)}/5)
            </div>
          )}

          <div className={styles.section}>
            <h2>📍 Origine</h2>
            <p>{wine.region}, {wine.country}</p>
            {wine.appellation && <p className={styles.label}>Appellation: {wine.appellation}</p>}
          </div>

          {wine.grape_varieties && wine.grape_varieties.length > 0 && (
            <div className={styles.section}>
              <h2>🍇 Cépages</h2>
              <ul className={styles.list}>
                {wine.grape_varieties.map((grape, idx) => (
                  <li key={idx}>
                    {grape.name} {grape.percentage && `(${grape.percentage}%)`}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {wine.alcohol_content && (
            <div className={styles.section}>
              <h2>🍷 Alcool</h2>
              <p>{wine.alcohol_content}%</p>
            </div>
          )}

          {(wine.body || wine.sweetness || wine.acidity || wine.tannins) && (
            <div className={styles.section}>
              <h2>📊 Caractéristiques</h2>
              <div className={styles.characteristics}>
                {wine.body && <span className={styles.char}>Corps: {wine.body}</span>}
                {wine.sweetness && <span className={styles.char}>Sucrosité: {wine.sweetness}</span>}
                {wine.acidity && <span className={styles.char}>Acidité: {wine.acidity}</span>}
                {wine.tannins && <span className={styles.char}>Tanins: {wine.tannins}</span>}
              </div>
            </div>
          )}

          {wine.nose && wine.nose.length > 0 && (
            <div className={styles.section}>
              <h2>👃 Nez</h2>
              <div className={styles.tags}>
                {wine.nose.map((note, idx) => (
                  <span key={idx} className={styles.tag}>{note}</span>
                ))}
              </div>
            </div>
          )}

          {wine.palate && wine.palate.length > 0 && (
            <div className={styles.section}>
              <h2>👅 Palais</h2>
              <div className={styles.tags}>
                {wine.palate.map((note, idx) => (
                  <span key={idx} className={styles.tag}>{note}</span>
                ))}
              </div>
            </div>
          )}

          {wine.tasting_notes && (
            <div className={styles.section}>
              <h2>📝 Notes de dégustation</h2>
              <p className={styles.notes}>{wine.tasting_notes}</p>
            </div>
          )}

          {wine.food_pairings && wine.food_pairings.length > 0 && (
            <div className={styles.section}>
              <h2>🍽️ Accords mets-vins</h2>
              <div className={styles.tags}>
                {wine.food_pairings.map((pairing, idx) => (
                  <span key={idx} className={styles.tag}>{pairing}</span>
                ))}
              </div>
            </div>
          )}

          <div className={styles.section}>
            <h2>📦 Cellier</h2>
            <p className={styles.quantity}>
              Quantité: <strong>{wine.current_quantity}</strong> bouteille{wine.current_quantity > 1 ? 's' : ''}
            </p>
            {wine.cellar_location && (
              <p className={styles.label}>Emplacement: {wine.cellar_location}</p>
            )}
            {wine.purchase_location && (
              <p className={styles.label}>Lieu d'achat: {wine.purchase_location}</p>
            )}
            {wine.purchase_price && (
              <p className={styles.label}>Prix d'achat: {wine.purchase_price} $</p>
            )}
            {wine.purchase_date && (
              <p className={styles.label}>
                Date d'achat: {new Date(wine.purchase_date).toLocaleDateString('fr-FR')}
              </p>
            )}
          </div>

          {(wine.drink_from || wine.drink_until || wine.peak_drinking) && (
            <div className={styles.section}>
              <h2>⏰ Fenêtre de consommation</h2>
              {wine.drink_from && <p>À boire à partir de: {wine.drink_from}</p>}
              {wine.drink_until && <p>À boire avant: {wine.drink_until}</p>}
              {wine.peak_drinking && <p>Apogée: {wine.peak_drinking}</p>}
            </div>
          )}

          {wine.barcode && (
            <div className={styles.section}>
              <h2>🔖 Code-barres</h2>
              <p className={styles.barcode}>{wine.barcode}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
