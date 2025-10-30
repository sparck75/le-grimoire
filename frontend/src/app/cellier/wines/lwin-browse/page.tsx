'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from '../browse/page.module.css'

interface LWINWine {
  id: string
  lwin7?: string
  lwin11?: string
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  country: string
  region: string
  appellation?: string
}

export default function LWINBrowsePage() {
  const router = useRouter()
  const [wines, setWines] = useState<LWINWine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({
    country: '',
    region: '',
    wine_type: '',
  })
  const [addingWine, setAddingWine] = useState<string | null>(null)

  useEffect(() => {
    fetchLWINWines()
  }, [search, filters])

  const fetchLWINWines = async () => {
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Build query params
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (filters.country) params.append('country', filters.country)
      if (filters.region) params.append('region', filters.region)
      if (filters.wine_type) params.append('wine_type', filters.wine_type)
      params.append('limit', '50')

      const response = await fetch(`${apiUrl}/api/v2/lwin/search?${params}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch LWIN wines')
      }

      const data = await response.json()
      setWines(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleAddToCellar = async (wineId: string) => {
    setAddingWine(wineId)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')

      if (!token) {
        setError('Vous devez être connecté pour ajouter un vin')
        return
      }

      const response = await fetch(`${apiUrl}/api/v2/wines/add-from-master/${wineId}?quantity=1`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to add wine')
      }

      // Show success message and redirect
      alert('Vin ajouté à votre cellier avec succès!')
      router.push('/cellier')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setAddingWine(null)
    }
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
  }

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  const clearFilters = () => {
    setSearch('')
    setFilters({
      country: '',
      region: '',
      wine_type: '',
    })
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🍷 Base de données LWIN</h1>
        <p style={{ color: '#666', marginBottom: '1.5rem' }}>
          Parcourez plus de 200,000 vins de la base de données LWIN (Liv-ex Wine Identification Number)
          et ajoutez-les directement à votre cellier.
        </p>
        <Link href="/cellier">
          <button className={styles.backButton}>← Retour au cellier</button>
        </Link>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {/* Search and filters */}
      <div className={styles.filterSection}>
        <div className={styles.searchBox}>
          <input
            type="text"
            placeholder="Rechercher par nom ou producteur..."
            value={search}
            onChange={handleSearchChange}
            className={styles.searchInput}
          />
          <button onClick={fetchLWINWines} className={styles.searchButton}>
            🔍 Rechercher
          </button>
        </div>

        <div className={styles.filters}>
          <select
            name="country"
            value={filters.country}
            onChange={handleFilterChange}
            className={styles.filterSelect}
          >
            <option value="">Tous les pays</option>
            <option value="France">France</option>
            <option value="Italy">Italie</option>
            <option value="Spain">Espagne</option>
            <option value="United States">États-Unis</option>
            <option value="Australia">Australie</option>
            <option value="Chile">Chili</option>
            <option value="Argentina">Argentine</option>
          </select>

          <select
            name="region"
            value={filters.region}
            onChange={handleFilterChange}
            className={styles.filterSelect}
          >
            <option value="">Toutes les régions</option>
            <option value="Bordeaux">Bordeaux</option>
            <option value="Burgundy">Bourgogne</option>
            <option value="Champagne">Champagne</option>
            <option value="Rhône">Rhône</option>
            <option value="Tuscany">Toscane</option>
            <option value="Piedmont">Piémont</option>
            <option value="Rioja">Rioja</option>
            <option value="Napa Valley">Napa Valley</option>
          </select>

          <select
            name="wine_type"
            value={filters.wine_type}
            onChange={handleFilterChange}
            className={styles.filterSelect}
          >
            <option value="">Tous les types</option>
            <option value="red">Rouge</option>
            <option value="white">Blanc</option>
            <option value="rosé">Rosé</option>
            <option value="sparkling">Effervescent</option>
            <option value="dessert">Dessert</option>
            <option value="fortified">Fortifié</option>
          </select>

          {(search || filters.country || filters.region || filters.wine_type) && (
            <button onClick={clearFilters} className={styles.clearButton}>
              ✖ Effacer
            </button>
          )}
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Chargement des vins LWIN...</p>
        </div>
      ) : wines.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>🍷</div>
          <h3>Aucun vin trouvé</h3>
          <p>Essayez de modifier vos critères de recherche</p>
        </div>
      ) : (
        <>
          <div className={styles.resultsHeader}>
            <p>{wines.length} vins trouvés</p>
          </div>
          <div className={styles.wineGrid}>
            {wines.map((wine) => (
              <div key={wine.id} className={styles.wineCard}>
                <div className={styles.wineCardHeader}>
                  <h3 className={styles.wineName}>{wine.name}</h3>
                  {wine.lwin11 && (
                    <span className={styles.lwinBadge} title="Code LWIN">
                      LWIN: {wine.lwin11}
                    </span>
                  )}
                </div>
                
                <div className={styles.wineDetails}>
                  {wine.producer && (
                    <div className={styles.wineDetail}>
                      <span className={styles.wineDetailLabel}>Producteur:</span>
                      <span>{wine.producer}</span>
                    </div>
                  )}
                  {wine.vintage && (
                    <div className={styles.wineDetail}>
                      <span className={styles.wineDetailLabel}>Millésime:</span>
                      <span>{wine.vintage}</span>
                    </div>
                  )}
                  <div className={styles.wineDetail}>
                    <span className={styles.wineDetailLabel}>Type:</span>
                    <span className={styles.wineType}>{wine.wine_type}</span>
                  </div>
                  <div className={styles.wineDetail}>
                    <span className={styles.wineDetailLabel}>Pays:</span>
                    <span>{wine.country}</span>
                  </div>
                  {wine.region && (
                    <div className={styles.wineDetail}>
                      <span className={styles.wineDetailLabel}>Région:</span>
                      <span>{wine.region}</span>
                    </div>
                  )}
                  {wine.appellation && (
                    <div className={styles.wineDetail}>
                      <span className={styles.wineDetailLabel}>Appellation:</span>
                      <span>{wine.appellation}</span>
                    </div>
                  )}
                </div>

                <div className={styles.wineActions}>
                  <button
                    onClick={() => handleAddToCellar(wine.id)}
                    disabled={addingWine === wine.id}
                    className={styles.addButton}
                  >
                    {addingWine === wine.id ? '⏳ Ajout...' : '➕ Ajouter à mon cellier'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
