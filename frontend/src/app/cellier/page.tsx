'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import styles from './cellier.module.css'

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
}

interface Liquor {
  id: string
  name: string
  brand?: string
  spirit_type: string
  region: string
  country: string
  current_quantity: number
  image_url?: string
  rating?: number
}

type ViewType = 'wines' | 'liquors'

export default function CellierPage() {
  const [wines, setWines] = useState<Wine[]>([])
  const [liquors, setLiquors] = useState<Liquor[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [viewType, setViewType] = useState<ViewType>('wines')
  const [inStockOnly, setInStockOnly] = useState(false)

  useEffect(() => {
    fetchData()
  }, [viewType, inStockOnly])

  async function fetchData() {
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      if (viewType === 'wines') {
        const params = new URLSearchParams()
        if (inStockOnly) params.append('in_stock', 'true')
        
        const response = await fetch(`${apiUrl}/api/v2/wines/?${params}`)
        if (!response.ok) throw new Error('Failed to fetch wines')
        const data = await response.json()
        setWines(data)
      } else {
        const params = new URLSearchParams()
        if (inStockOnly) params.append('in_stock', 'true')
        
        const response = await fetch(`${apiUrl}/api/v2/liquors/?${params}`)
        if (!response.ok) throw new Error('Failed to fetch liquors')
        const data = await response.json()
        setLiquors(data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const filteredWines = wines.filter(wine => {
    const matchesSearch = wine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         wine.producer?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || wine.wine_type === filterType
    return matchesSearch && matchesType
  })

  const filteredLiquors = liquors.filter(liquor => {
    const matchesSearch = liquor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         liquor.brand?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || liquor.spirit_type === filterType
    return matchesSearch && matchesType
  })

  const items = viewType === 'wines' ? filteredWines : filteredLiquors
  const totalCount = viewType === 'wines' ? wines.length : liquors.length
  const inStockCount = viewType === 'wines' 
    ? wines.filter(w => w.current_quantity > 0).length
    : liquors.filter(l => l.current_quantity > 0).length

  if (loading && items.length === 0) {
    return <div className={styles.container}>Chargement...</div>
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🍷 Mon Cellier</h1>
        <Link href={`/cellier/${viewType}/new`}>
          <button className={styles.addButton}>
            {viewType === 'wines' ? 'Ajouter un vin' : 'Ajouter un spiritueux'}
          </button>
        </Link>
      </div>

      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${viewType === 'wines' ? styles.active : ''}`}
          onClick={() => setViewType('wines')}
        >
          🍷 Vins
        </button>
        <button
          className={`${styles.tab} ${viewType === 'liquors' ? styles.active : ''}`}
          onClick={() => setViewType('liquors')}
        >
          🥃 Spiritueux
        </button>
      </div>

      <div className={styles.filters}>
        <input
          type="text"
          placeholder="Rechercher..."
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
          {viewType === 'wines' ? (
            <>
              <option value="red">Rouge</option>
              <option value="white">Blanc</option>
              <option value="rosé">Rosé</option>
              <option value="sparkling">Mousseux</option>
              <option value="dessert">Dessert</option>
            </>
          ) : (
            <>
              <option value="whiskey">Whisky</option>
              <option value="vodka">Vodka</option>
              <option value="rum">Rhum</option>
              <option value="gin">Gin</option>
              <option value="tequila">Tequila</option>
              <option value="brandy">Brandy</option>
              <option value="liqueur">Liqueur</option>
              <option value="other">Autre</option>
            </>
          )}
        </select>

        <label className={styles.checkbox}>
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={(e) => setInStockOnly(e.target.checked)}
          />
          En stock seulement
        </label>
      </div>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statValue}>{totalCount}</span>
          <span className={styles.statLabel}>Total</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>{inStockCount}</span>
          <span className={styles.statLabel}>En stock</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>{items.length}</span>
          <span className={styles.statLabel}>Affichés</span>
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.grid}>
        {viewType === 'wines' ? (
          filteredWines.map(wine => (
            <Link key={wine.id} href={`/cellier/wines/${wine.id}`}>
              <div className={styles.card}>
                <div className={styles.cardImage}>
                  {wine.image_url ? (
                    <img src={wine.image_url} alt={wine.name} />
                  ) : (
                    <div className={styles.placeholder}>🍷</div>
                  )}
                </div>
                <div className={styles.cardContent}>
                  <h3>{wine.name}</h3>
                  {wine.producer && <p className={styles.producer}>{wine.producer}</p>}
                  <div className={styles.cardMeta}>
                    <span className={styles.badge}>{wine.wine_type}</span>
                    <span>{wine.vintage || 'NV'}</span>
                    <span>{wine.region}</span>
                  </div>
                  <div className={styles.quantity}>
                    {wine.current_quantity > 0 ? (
                      <span className={styles.inStock}>
                        ✓ {wine.current_quantity} bouteille{wine.current_quantity > 1 ? 's' : ''}
                      </span>
                    ) : (
                      <span className={styles.outOfStock}>Aucune en stock</span>
                    )}
                  </div>
                  {wine.rating && (
                    <div className={styles.rating}>
                      {'⭐'.repeat(Math.round(wine.rating))}
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))
        ) : (
          filteredLiquors.map(liquor => (
            <Link key={liquor.id} href={`/cellier/liquors/${liquor.id}`}>
              <div className={styles.card}>
                <div className={styles.cardImage}>
                  {liquor.image_url ? (
                    <img src={liquor.image_url} alt={liquor.name} />
                  ) : (
                    <div className={styles.placeholder}>🥃</div>
                  )}
                </div>
                <div className={styles.cardContent}>
                  <h3>{liquor.name}</h3>
                  {liquor.brand && <p className={styles.producer}>{liquor.brand}</p>}
                  <div className={styles.cardMeta}>
                    <span className={styles.badge}>{liquor.spirit_type}</span>
                    <span>{liquor.region || liquor.country}</span>
                  </div>
                  <div className={styles.quantity}>
                    {liquor.current_quantity > 0 ? (
                      <span className={styles.inStock}>
                        ✓ {liquor.current_quantity}%
                      </span>
                    ) : (
                      <span className={styles.outOfStock}>Vide</span>
                    )}
                  </div>
                  {liquor.rating && (
                    <div className={styles.rating}>
                      {'⭐'.repeat(Math.round(liquor.rating))}
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))
        )}
      </div>

      {items.length === 0 && !loading && (
        <div className={styles.empty}>
          <p>Aucun {viewType === 'wines' ? 'vin' : 'spiritueux'} trouvé</p>
          <Link href={`/cellier/${viewType}/new`}>
            <button className={styles.addButton}>
              Ajouter votre premier {viewType === 'wines' ? 'vin' : 'spiritueux'}
            </button>
          </Link>
        </div>
      )}
    </div>
  )
}
