'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import styles from './liquor-detail.module.css'

interface Liquor {
  id: string
  name: string
  brand?: string
  distillery?: string
  spirit_type: string
  subtype?: string
  country: string
  region: string
  alcohol_content?: number
  age_statement?: string
  cask_type?: string
  finish?: string
  color: string
  nose: string[]
  palate: string[]
  finish_notes: string
  tasting_notes: string
  cocktail_uses: string[]
  food_pairings: string[]
  serving_suggestion: string
  purchase_date?: string
  purchase_price?: number
  purchase_location?: string
  current_quantity: number
  cellar_location?: string
  rating?: number
  image_url?: string
  barcode?: string
}

export default function LiquorDetailPage() {
  const router = useRouter()
  const params = useParams()
  const liquorId = params.id as string

  const [liquor, setLiquor] = useState<Liquor | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchLiquor()
  }, [liquorId])

  async function fetchLiquor() {
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')

      const headers: Record<string, string> = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${apiUrl}/api/v2/liquors/${liquorId}`, { headers })
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Spiritueux non trouvé')
        }
        throw new Error('Erreur lors du chargement')
      }

      const data = await response.json()
      setLiquor(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce spiritueux?')) {
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

      const response = await fetch(`${apiUrl}/api/v2/liquors/${liquorId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression')
      }

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

  if (error || !liquor) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <p>❌ {error || 'Spiritueux non trouvé'}</p>
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
          <Link href={`/cellier/liquors/${liquorId}/edit`}>
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
          {liquor.image_url ? (
            <img src={liquor.image_url} alt={liquor.name} className={styles.liquorImage} />
          ) : (
            <div className={styles.placeholderImage}>🥃</div>
          )}
        </div>

        <div className={styles.details}>
          <h1 className={styles.title}>{liquor.name}</h1>
          
          {liquor.brand && (
            <p className={styles.brand}>{liquor.brand}</p>
          )}

          {liquor.distillery && (
            <p className={styles.distillery}>Distillerie: {liquor.distillery}</p>
          )}

          <div className={styles.badges}>
            <span className={styles.badge}>{liquor.spirit_type}</span>
            {liquor.subtype && <span className={styles.badge}>{liquor.subtype}</span>}
            {liquor.age_statement && <span className={styles.badge}>{liquor.age_statement}</span>}
          </div>

          {liquor.rating && (
            <div className={styles.rating}>
              {'⭐'.repeat(Math.round(liquor.rating))} ({liquor.rating.toFixed(1)}/5)
            </div>
          )}

          <div className={styles.section}>
            <h2>📍 Origine</h2>
            <p>{liquor.region ? `${liquor.region}, ${liquor.country}` : liquor.country}</p>
          </div>

          {liquor.alcohol_content && (
            <div className={styles.section}>
              <h2>🥃 Alcool</h2>
              <p>{liquor.alcohol_content}%</p>
            </div>
          )}

          {(liquor.cask_type || liquor.finish) && (
            <div className={styles.section}>
              <h2>🛢️ Vieillissement</h2>
              {liquor.cask_type && <p>Type de fût: {liquor.cask_type}</p>}
              {liquor.finish && <p>Finition: {liquor.finish}</p>}
            </div>
          )}

          {liquor.nose && liquor.nose.length > 0 && (
            <div className={styles.section}>
              <h2>👃 Nez</h2>
              <div className={styles.tags}>
                {liquor.nose.map((note, idx) => (
                  <span key={idx} className={styles.tag}>{note}</span>
                ))}
              </div>
            </div>
          )}

          {liquor.palate && liquor.palate.length > 0 && (
            <div className={styles.section}>
              <h2>👅 Palais</h2>
              <div className={styles.tags}>
                {liquor.palate.map((note, idx) => (
                  <span key={idx} className={styles.tag}>{note}</span>
                ))}
              </div>
            </div>
          )}

          {liquor.finish_notes && (
            <div className={styles.section}>
              <h2>🎯 Finale</h2>
              <p className={styles.notes}>{liquor.finish_notes}</p>
            </div>
          )}

          {liquor.tasting_notes && (
            <div className={styles.section}>
              <h2>📝 Notes de dégustation</h2>
              <p className={styles.notes}>{liquor.tasting_notes}</p>
            </div>
          )}

          {liquor.cocktail_uses && liquor.cocktail_uses.length > 0 && (
            <div className={styles.section}>
              <h2>🍸 Utilisations en cocktail</h2>
              <div className={styles.tags}>
                {liquor.cocktail_uses.map((cocktail, idx) => (
                  <span key={idx} className={styles.tag}>{cocktail}</span>
                ))}
              </div>
            </div>
          )}

          {liquor.food_pairings && liquor.food_pairings.length > 0 && (
            <div className={styles.section}>
              <h2>🍽️ Accords mets</h2>
              <div className={styles.tags}>
                {liquor.food_pairings.map((pairing, idx) => (
                  <span key={idx} className={styles.tag}>{pairing}</span>
                ))}
              </div>
            </div>
          )}

          {liquor.serving_suggestion && (
            <div className={styles.section}>
              <h2>🥄 Suggestion de service</h2>
              <p>{liquor.serving_suggestion}</p>
            </div>
          )}

          <div className={styles.section}>
            <h2>📦 Cellier</h2>
            <div className={styles.quantityBar}>
              <div className={styles.quantityFill} style={{ width: `${liquor.current_quantity}%` }}>
                {liquor.current_quantity}%
              </div>
            </div>
            <p className={styles.quantity}>
              Niveau: <strong>{liquor.current_quantity}%</strong>
            </p>
            {liquor.cellar_location && (
              <p className={styles.label}>Emplacement: {liquor.cellar_location}</p>
            )}
            {liquor.purchase_location && (
              <p className={styles.label}>Lieu d'achat: {liquor.purchase_location}</p>
            )}
            {liquor.purchase_price && (
              <p className={styles.label}>Prix d'achat: {liquor.purchase_price} $</p>
            )}
            {liquor.purchase_date && (
              <p className={styles.label}>
                Date d'achat: {new Date(liquor.purchase_date).toLocaleDateString('fr-FR')}
              </p>
            )}
          </div>

          {liquor.barcode && (
            <div className={styles.section}>
              <h2>🔖 Code-barres</h2>
              <p className={styles.barcode}>{liquor.barcode}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
