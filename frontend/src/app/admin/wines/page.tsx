'use client';

/**
 * Admin Wines Page - Browse & Manage LWIN Database
 * Based on the cellier/wines/browse page but with admin controls
 */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import styles from '../../cellier/wines/browse/page.module.css';

interface GrapeVariety {
  name: string;
  percentage?: number;
}

interface Wine {
  id: string;
  name: string;
  producer?: string;
  vintage?: number;
  wine_type: string;
  region: string;
  country: string;
  appellation?: string;
  lwin7?: string;
  lwin11?: string;
  lwin18?: string;
  classification?: string;
  color?: string;
  grape_varieties?: GrapeVariety[];
  sub_region?: string;
  site?: string;
  parcel?: string;
  image_url?: string;
  front_label_image?: string;
  back_label_image?: string;
  bottle_image?: string;
}

export default function AdminLWINBrowsePage() {
  const { user } = useAuth();
  const router = useRouter();
  const [wines, setWines] = useState<Wine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filters, setFilters] = useState({
    country: '',
    region: '',
    wine_type: '',
    vintage: '',
  });

  const isAdmin = user && user.role === 'admin';

  // Format grape varieties for display
  const formatGrapeVarieties = (grapes?: GrapeVariety[]): string => {
    if (!grapes || grapes.length === 0) return '';
    return grapes
      .map(g => g.percentage ? `${g.name} (${g.percentage}%)` : g.name)
      .join(', ');
  };

  useEffect(() => {
    if (!isAdmin && !loading) {
      router.push('/admin');
    }
  }, [isAdmin, loading, router]);

  useEffect(() => {
    if (isAdmin) {
      fetchWines();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin, filters]);

  async function fetchWines() {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        limit: '50',
        ...(searchTerm && { search: searchTerm }),
        ...(filters.country && { country: filters.country }),
        ...(filters.region && { region: filters.region }),
        ...(filters.wine_type && { wine_type: filters.wine_type }),
        ...(filters.vintage && { vintage: filters.vintage }),
      });

      const response = await fetch(
        `http://192.168.1.100:8000/api/admin/wines?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch wines');
      }

      const data = await response.json();
      setWines(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading wines');
    } finally {
      setLoading(false);
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchWines();
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const clearFilters = () => {
    setSearchTerm('');
    setFilters({ country: '', region: '', wine_type: '', vintage: '' });
  };

  const translateWineType = (type: string): string => {
    const translations: Record<string, string> = {
      'red': 'Rouge',
      'white': 'Blanc',
      'rosé': 'Rosé',
      'rose': 'Rosé',
      'sparkling': 'Effervescent',
      'dessert': 'Dessert',
      'fortified': 'Fortifié'
    };
    return translations[type.toLowerCase()] || type;
  };

  if (loading && wines.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>⏳ Chargement de la base LWIN...</div>
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1>🔐 Base de Données LWIN (Admin)</h1>
          <p className={styles.subtitle}>
            Gérez le catalogue master de 200K+ vins
          </p>
        </div>
        <Link href="/admin/wines/new">
          <button className={styles.addButton}>➕ Ajouter un vin</button>
        </Link>
      </div>

      <div className={styles.searchBox}>
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <input
            type="text"
            placeholder="Rechercher par nom, producteur, appellation..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles.searchInput}
          />
          <button type="submit" className={styles.searchButton}>
            🔍 Rechercher
          </button>
        </form>
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
          <option value="USA">États-Unis</option>
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
            ✕ Effacer les filtres
          </button>
        )}
      </div>

      {error && (
        <div className={styles.error}>
          ⚠️ {error}
        </div>
      )}

      <div className={styles.resultsHeader}>
        <h2>{wines.length} vins trouvés</h2>
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
                  <Link href={`/admin/wines/${wine.id}/edit`}>
                    <button className={styles.editButton}>
                      ✏️ Gérer
                    </button>
                  </Link>
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
                  <Link href={`/admin/wines/${wine.id}/edit`}>
                    <button className={styles.listEditButton}>
                      ✏️ Gérer
                    </button>
                  </Link>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      {wines.length === 0 && !loading && (
        <div className={styles.emptyState}>
          <h3>Aucun vin trouvé</h3>
          <p>Essayez de modifier vos critères de recherche ou ajoutez un nouveau vin.</p>
          <Link href="/admin/wines/new">
            <button className={styles.addButton}>➕ Ajouter un vin</button>
          </Link>
        </div>
      )}
    </div>
  );
}
