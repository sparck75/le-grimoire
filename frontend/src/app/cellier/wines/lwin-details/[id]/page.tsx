'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from './page.module.css'

interface WineDetails {
  id: string
  lwin7?: string
  lwin11?: string
  lwin18?: string
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  country: string
  region: string
  appellation?: string
  classification?: string
  grape_varieties?: Array<{
    name: string
    percentage?: number
  }>
  alcohol_content?: number
  tasting_notes?: string
  // Extended LWIN fields
  lwin_status?: string
  lwin_display_name?: string
  producer_title?: string
  sub_region?: string
  site?: string
  parcel?: string
  sub_type?: string
  designation?: string
  vintage_config?: string
  lwin_first_vintage?: string
  lwin_final_vintage?: string
  lwin_date_added?: string
  lwin_date_updated?: string
  lwin_reference?: string
}

// Translation map for wine types
const wineTypeTranslations: { [key: string]: string } = {
  'red': 'Rouge',
  'white': 'Blanc',
  'rosé': 'Rosé',
  'rose': 'Rosé',
  'sparkling': 'Effervescent',
  'dessert': 'Dessert',
  'fortified': 'Fortifié'
}

const translateWineType = (type: string): string => {
  return wineTypeTranslations[type.toLowerCase()] || type
}

export default function LWINDetailsPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [wine, setWine] = useState<WineDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    fetchWineDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  const fetchWineDetails = async () => {
    try {
      // Use Next.js API proxy (configured in next.config.js)
      const response = await fetch(`/api/v2/lwin/${params.id}`)
      
      if (!response.ok) {
        throw new Error('Vin non trouvé')
      }

      const data = await response.json()
      setWine(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }

  const handleAddToCellar = async () => {
    setAdding(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')

      if (!token) {
        setError('Vous devez être connecté pour ajouter un vin')
        return
      }

      // Use Next.js API proxy
      const response = await fetch(
        `/api/v2/wines/add-from-master/${params.id}?quantity=1`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Échec de l\'ajout')
      }

      alert('Vin ajouté à votre cellier avec succès!')
      router.push('/cellier')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setAdding(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Chargement des détails...</p>
        </div>
      </div>
    )
  }

  if (error || !wine) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || 'Vin non trouvé'}</div>
        <Link href="/cellier/wines/browse">
          <button className={styles.backButton}>← Retour à la recherche</button>
        </Link>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link href="/cellier/wines/browse">
          <button className={styles.backButton}>← Retour à la recherche</button>
        </Link>
      </div>

      <div className={styles.detailsCard}>
        {/* Header */}
        <div className={styles.detailsHeader}>
          <div>
            <h1 className={styles.wineName}>{wine.name}</h1>
            {wine.producer && (
              <p className={styles.producer}>{wine.producer}</p>
            )}
          </div>
          {wine.lwin11 && (
            <div className={styles.lwinBadge} title="Code LWIN">
              LWIN: {wine.lwin11}
            </div>
          )}
        </div>

        {/* Main Info Grid */}
        <div className={styles.infoGrid}>
          {wine.lwin_status && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Statut LWIN</span>
              <span className={styles.infoValue}>{wine.lwin_status}</span>
            </div>
          )}

          {wine.vintage && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Millésime</span>
              <span className={styles.infoValue}>{wine.vintage}</span>
            </div>
          )}
          
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Type</span>
            <span className={styles.wineType}>{translateWineType(wine.wine_type)}</span>
          </div>

          {wine.sub_type && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Sous-type</span>
              <span className={styles.infoValue}>{wine.sub_type}</span>
            </div>
          )}

          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Pays</span>
            <span className={styles.infoValue}>{wine.country}</span>
          </div>

          {wine.region && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Région</span>
              <span className={styles.infoValue}>{wine.region}</span>
            </div>
          )}

          {wine.sub_region && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Sous-région</span>
              <span className={styles.infoValue}>{wine.sub_region}</span>
            </div>
          )}

          {wine.site && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Site/Vignoble</span>
              <span className={styles.infoValue}>{wine.site}</span>
            </div>
          )}

          {wine.parcel && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Parcelle</span>
              <span className={styles.infoValue}>{wine.parcel}</span>
            </div>
          )}

          {wine.designation && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Désignation</span>
              <span className={styles.infoValue}>{wine.designation}</span>
            </div>
          )}

          {wine.appellation && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Appellation</span>
              <span className={styles.infoValue}>{wine.appellation}</span>
            </div>
          )}

          {wine.classification && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Classification</span>
              <span className={styles.infoValue}>{wine.classification}</span>
            </div>
          )}

          {wine.vintage_config && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Config. millésime</span>
              <span className={styles.infoValue}>{wine.vintage_config}</span>
            </div>
          )}

          {wine.alcohol_content && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Alcool</span>
              <span className={styles.infoValue}>{wine.alcohol_content}%</span>
            </div>
          )}
        </div>

        {/* Grape Varieties */}
        {wine.grape_varieties && wine.grape_varieties.length > 0 && (
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>Cépages</h2>
            <div className={styles.grapeList}>
              {wine.grape_varieties.map((grape, idx) => (
                <div key={idx} className={styles.grapeItem}>
                  <span className={styles.grapeName}>{grape.name}</span>
                  {grape.percentage && (
                    <span className={styles.grapePercentage}>{grape.percentage}%</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tasting Notes */}
        {wine.tasting_notes && (
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>Notes de dégustation</h2>
            <p className={styles.tastingNotes}>{wine.tasting_notes}</p>
          </div>
        )}

        {/* LWIN Codes */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Codes LWIN</h2>
          <div className={styles.lwinCodes}>
            {wine.lwin7 && (
              <div className={styles.lwinCode}>
                <span className={styles.lwinCodeLabel}>LWIN7:</span>
                <span className={styles.lwinCodeValue}>{wine.lwin7}</span>
              </div>
            )}
            {wine.lwin11 && (
              <div className={styles.lwinCode}>
                <span className={styles.lwinCodeLabel}>LWIN11:</span>
                <span className={styles.lwinCodeValue}>{wine.lwin11}</span>
              </div>
            )}
            {wine.lwin18 && (
              <div className={styles.lwinCode}>
                <span className={styles.lwinCodeLabel}>LWIN18:</span>
                <span className={styles.lwinCodeValue}>{wine.lwin18}</span>
              </div>
            )}
          </div>
        </div>

        {/* Add to Cellar Button */}
        <div className={styles.actions}>
          <button
            onClick={handleAddToCellar}
            disabled={adding}
            className={styles.addButton}
          >
            {adding ? '⏳ Ajout en cours...' : '➕ Ajouter à mon cellier'}
          </button>
        </div>

        {error && <div className={styles.error}>{error}</div>}
      </div>
    </div>
  )
}
