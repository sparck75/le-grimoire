'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from './page.module.css'

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
  region: string
  country: string
  appellation?: string
  classification?: string
  color?: string
  sub_region?: string
  site?: string
  grape_varieties?: GrapeVariety[]
  lwin7?: string
  lwin11?: string
  lwin18?: string
  image_url?: string
  front_label_image?: string
  back_label_image?: string
  bottle_image?: string
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

export default function BrowseLWINWinesPage() {
  const router = useRouter()
  const [wines, setWines] = useState<Wine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState({
    country: '',
    region: '',
    wine_type: '',
  })
  const [addingWineId, setAddingWineId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  // Format grape varieties for display
  const formatGrapeVarieties = (grapes?: GrapeVariety[]): string => {
    if (!grapes || grapes.length === 0) return '';
    return grapes
      .map(g => g.percentage ? `${g.name} (${g.percentage}%)` : g.name)
      .join(', ');
  };

  useEffect(() => {
    fetchLWINWines()
  }, [searchTerm, filters])

  async function fetchLWINWines() {
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Build query params for LWIN search
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)
      if (filters.country) params.append('country', filters.country)
      if (filters.region) params.append('region', filters.region)
      if (filters.wine_type) params.append('wine_type', filters.wine_type)
      params.append('limit', '50')
      
      const response = await fetch(`${apiUrl}/api/v2/lwin/search?${params}`)
      if (!response.ok) throw new Error('Failed to fetch LWIN wines')
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
        setError('Vous devez être connecté pour ajouter un vin')
        return
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

      alert('✅ Vin ajouté à votre cellier!')
      router.push('/cellier')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setAddingWineId(null)
    }
  }

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  const clearFilters = () => {
    setSearchTerm('')
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
          Parcourez plus de 200,000 vins de la base de données LWIN et ajoutez-les à votre cellier
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
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
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

          {(searchTerm || filters.country || filters.region || filters.wine_type) && (
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
            <div className={styles.viewToggle}>
              <button
                className={`${styles.viewButton} ${viewMode === 'grid' ? styles.active : ''}`}
                onClick={() => setViewMode('grid')}
                title="Vue en grille"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <rect x="2" y="2" width="7" height="7" rx="1"/>
                  <rect x="11" y="2" width="7" height="7" rx="1"/>
                  <rect x="2" y="11" width="7" height="7" rx="1"/>
                  <rect x="11" y="11" width="7" height="7" rx="1"/>
                </svg>
              </button>
              <button
                className={`${styles.viewButton} ${viewMode === 'list' ? styles.active : ''}`}
                onClick={() => setViewMode('list')}
                title="Vue en liste"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <rect x="2" y="3" width="16" height="2" rx="1"/>
                  <rect x="2" y="9" width="16" height="2" rx="1"/>
                  <rect x="2" y="15" width="16" height="2" rx="1"/>
                </svg>
              </button>
            </div>
          </div>
          <div className={viewMode === 'grid' ? styles.wineGrid : styles.wineList}>
            {wines.map((wine) => (
              <div key={wine.id} className={viewMode === 'grid' ? styles.wineCard : styles.wineListItem}>
                {viewMode === 'grid' ? (
                  // Grid View
                  <>
                    {/* Wine Image with Fallback */}
                    <div style={{ 
                      width: '100%', 
                      height: '180px', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      background: '#f5f5f5',
                      borderRadius: '8px 8px 0 0',
                      overflow: 'hidden',
                      marginBottom: '12px',
                      position: 'relative'
                    }}>
                      {(wine.bottle_image || wine.front_label_image || wine.image_url) ? (
                        <img 
                          src={`http://192.168.1.100:8000/${wine.bottle_image || wine.front_label_image || wine.image_url}`}
                          alt={wine.name}
                          style={{ 
                            maxWidth: '100%', 
                            maxHeight: '100%', 
                            objectFit: 'contain' 
                          }}
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            const parent = e.currentTarget.parentElement;
                            if (parent && !parent.querySelector('.fallback-icon')) {
                              const fallback = document.createElement('div');
                              fallback.className = 'fallback-icon';
                              fallback.style.cssText = 'color: #999; font-size: 48px;';
                              fallback.textContent = '🍷';
                              parent.appendChild(fallback);
                            }
                          }}
                        />
                      ) : (
                        <div style={{ color: '#999', fontSize: '48px' }}>🍷</div>
                      )}
                    </div>

                    <div className={styles.wineCardHeader}>
                      <div className={styles.wineTitleSection}>
                        <h3 className={styles.wineName}>{wine.name}</h3>
                        {wine.producer && (
                          <p className={styles.wineProducer}>{wine.producer}</p>
                        )}
                      </div>
                      {wine.lwin11 && (
                        <span className={styles.lwinBadge} title="Code LWIN">
                          {wine.lwin11}
                        </span>
                      )}
                    </div>
                    
                    <div className={styles.wineMetaRow}>
                      {wine.vintage && (
                        <span className={styles.vintageBadge}>{wine.vintage}</span>
                      )}
                      {wine.color && (
                        <span className={styles.colorBadge} data-color={wine.color?.toLowerCase()}>
                          {wine.color}
                        </span>
                      )}
                      <span className={styles.typeBadge} data-type={wine.wine_type?.toLowerCase()}>
                        {translateWineType(wine.wine_type)}
                      </span>
                    </div>

                    <div className={styles.wineLocation}>
                      <span className={styles.locationIcon}>📍</span>
                      <span>
                        {wine.sub_region || wine.region}
                        {wine.site && ` • ${wine.site}`}
                        {wine.country && `, ${wine.country}`}
                      </span>
                    </div>

                    {wine.appellation && (
                      <div className={styles.wineAppellation}>
                        <span className={styles.appellationIcon}>🏆</span>
                        <span>{wine.appellation}</span>
                      </div>
                    )}

                    {wine.classification && (
                      <div className={styles.wineClassification}>
                        <span className={styles.classificationIcon}>⭐</span>
                        <span>{wine.classification}</span>
                      </div>
                    )}

                    {wine.grape_varieties && wine.grape_varieties.length > 0 && (
                      <div className={styles.wineGrapes}>
                        <span className={styles.grapesIcon}>🍇</span>
                        <span>{formatGrapeVarieties(wine.grape_varieties)}</span>
                      </div>
                    )}

                    <div className={styles.wineActions}>
                      <Link href={`/cellier/wines/lwin-details/${wine.id}`}>
                        <button className={styles.detailsButton}>
                          📖 Détails
                        </button>
                      </Link>
                      <button
                        onClick={() => addToCellier(wine.id)}
                        disabled={addingWineId === wine.id}
                        className={styles.addButton}
                      >
                        {addingWineId === wine.id ? '⏳' : '➕'}
                      </button>
                    </div>
                  </>
                ) : (
                  // List View
                  <>
                    {/* Wine Image in List View with Fallback */}
                    <div style={{ 
                      width: '80px',
                      height: '80px',
                      flexShrink: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: '#f5f5f5',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      marginRight: '15px'
                    }}>
                      {(wine.bottle_image || wine.front_label_image || wine.image_url) ? (
                        <img 
                          src={`http://192.168.1.100:8000/${wine.bottle_image || wine.front_label_image || wine.image_url}`}
                          alt={wine.name}
                          style={{ 
                            maxWidth: '100%', 
                            maxHeight: '100%', 
                            objectFit: 'contain' 
                          }}
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            const parent = e.currentTarget.parentElement;
                            if (parent && !parent.querySelector('.fallback-icon')) {
                              const fallback = document.createElement('div');
                              fallback.className = 'fallback-icon';
                              fallback.style.cssText = 'color: #999; font-size: 32px;';
                              fallback.textContent = '🍷';
                              parent.appendChild(fallback);
                            }
                          }}
                        />
                      ) : (
                        <div style={{ color: '#999', fontSize: '32px' }}>🍷</div>
                      )}
                    </div>

                    <div className={styles.listMainInfo}>
                      <div className={styles.listTitle}>
                        <h3 className={styles.listWineName}>{wine.name}</h3>
                        {wine.producer && (
                          <p className={styles.listProducer}>{wine.producer}</p>
                        )}
                      </div>
                      <div className={styles.listMeta}>
                        {wine.vintage && (
                          <span className={`${styles.listBadge} vintage`}>{wine.vintage}</span>
                        )}
                        {wine.color && (
                          <span className={`${styles.listBadge} color`} data-color={wine.color?.toLowerCase()}>
                            {wine.color}
                          </span>
                        )}
                        <span className={`${styles.listBadge} type`} data-type={wine.wine_type?.toLowerCase()}>
                          {translateWineType(wine.wine_type)}
                        </span>
                        {wine.grape_varieties && wine.grape_varieties.length > 0 && (
                          <span className={`${styles.listBadge} grapes`}>
                            🍇 {formatGrapeVarieties(wine.grape_varieties)}
                          </span>
                        )}
                        <div className={styles.listLocation}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                          </svg>
                          <span>
                            {wine.sub_region || wine.region}
                            {wine.site && ` • ${wine.site}`}
                            {wine.country && `, ${wine.country}`}
                          </span>
                        </div>
                        {wine.appellation && (
                          <div className={styles.listAppellation}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                            </svg>
                            <span>{wine.appellation}</span>
                          </div>
                        )}
                        {wine.classification && (
                          <div className={styles.listClassification}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                            </svg>
                            <span>{wine.classification}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    {wine.lwin11 && (
                      <span className={styles.listLwinBadge}>{wine.lwin11}</span>
                    )}
                    <div className={styles.listActions}>
                      <Link href={`/cellier/wines/lwin-details/${wine.id}`}>
                        <button className={styles.listDetailsButton}>
                          📖 Détails
                        </button>
                      </Link>
                      <button
                        onClick={() => addToCellier(wine.id)}
                        disabled={addingWineId === wine.id}
                        className={styles.listAddButton}
                      >
                        {addingWineId === wine.id ? '⏳ Ajout...' : '➕ Ajouter'}
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
