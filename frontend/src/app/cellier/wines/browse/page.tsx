'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import styles from '../../cellier.module.css'

interface Wine {
  id: string
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  region: string
  country: string
  current_quantity: number
  image_url?: string
  rating?: number
  appellation?: string
  alcohol_content?: number
  tasting_notes: string
}

export default function BrowseMasterWinesPage() {
  const router = useRouter()
  const [wines, setWines] = useState<Wine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [addingWineId, setAddingWineId] = useState<string | null>(null)

  useEffect(() => {
    fetchMasterWines()
  }, [])

  async function fetchMasterWines() {
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      const headers: Record<string, string> = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await fetch(`${apiUrl}/api/v2/wines/master`, { headers })
      if (!response.ok) throw new Error('Failed to fetch master wines')
      const data = await response.json()
      setWines(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  async function addToCellier(wineId: string) {
    setAddingWineId(wineId)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        throw new Error('You must be logged in to add wines')
      }

      const response = await fetch(
        `${apiUrl}/api/v2/wines/add-from-master/${wineId}?quantity=1`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to add wine')
      }

      // Success! Show feedback and optionally navigate
      alert('✅ Vin ajouté à votre cellier!')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setAddingWineId(null)
    }
  }

  const filteredWines = wines.filter(wine => {
    const matchesSearch = wine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         wine.producer?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || wine.wine_type === filterType
    return matchesSearch && matchesType
  })

  const wineTypes = Array.from(new Set(wines.map(w => w.wine_type)))

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button onClick={() => router.back()} className={styles.backButton}>
          ← Retour
        </button>
        <h1>🍷 Catalogue de Vins</h1>
        <p className={styles.subtitle}>
          Parcourez notre catalogue et ajoutez des vins à votre cellier
        </p>
      </div>

      <div className={styles.controls}>
        <input
          type="text"
          placeholder="🔍 Rechercher un vin..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className={styles.filterSelect}
        >
          <option value="all">Tous les types</option>
          {wineTypes.map(type => (
            <option key={type} value={type}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className={styles.error}>
          <p>❌ {error}</p>
        </div>
      )}

      {loading ? (
        <div className={styles.loading}>
          <p>Chargement des vins...</p>
        </div>
      ) : filteredWines.length === 0 ? (
        <div className={styles.empty}>
          <p>Aucun vin trouvé</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {filteredWines.map((wine) => (
            <div key={wine.id} className={styles.card}>
              <div className={styles.cardImage}>
                {wine.image_url ? (
                  <img src={wine.image_url} alt={wine.name} />
                ) : (
                  <div className={styles.placeholderImage}>🍷</div>
                )}
              </div>
              
              <div className={styles.cardContent}>
                <h3>{wine.name}</h3>
                
                {wine.producer && (
                  <p className={styles.producer}>{wine.producer}</p>
                )}
                
                <div className={styles.details}>
                  {wine.vintage && (
                    <span className={styles.vintage}>{wine.vintage}</span>
                  )}
                  <span className={styles.type}>{wine.wine_type}</span>
                </div>
                
                {wine.region && (
                  <p className={styles.region}>
                    📍 {wine.region}{wine.country ? `, ${wine.country}` : ''}
                  </p>
                )}
                
                {wine.appellation && (
                  <p className={styles.appellation}>{wine.appellation}</p>
                )}
                
                {wine.alcohol_content && (
                  <p className={styles.alcohol}>🍷 {wine.alcohol_content}%</p>
                )}
                
                {wine.rating && (
                  <div className={styles.rating}>
                    ⭐ {wine.rating.toFixed(1)}/5
                  </div>
                )}
                
                {wine.tasting_notes && (
                  <p className={styles.tastingNotes}>{wine.tasting_notes}</p>
                )}
              </div>
              
              <div className={styles.cardActions}>
                <button
                  onClick={() => addToCellier(wine.id)}
                  disabled={addingWineId === wine.id}
                  className={styles.addButton}
                >
                  {addingWineId === wine.id ? '⏳ Ajout...' : '➕ Ajouter à mon cellier'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
