'use client';

/**
 * Admin Wine Edit - Multi-Source Data Management
 * 
 * This page displays wine data from multiple sources:
 * - LWIN (base catalog data)
 * - Vivino (images, ratings, prices)
 * - Wine-Searcher (market prices)
 * - Manual overrides
 * 
 * Admin can see which field came from which source and override any value.
 */

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../../../../contexts/AuthContext';
import Link from 'next/link';
import styles from './wine-edit.module.css';
import WineImageUpload from '../wine-image-upload';

interface GrapeVariety {
  name: string;
  percentage?: number;
}

interface ImageSource {
  url: string;
  quality?: string;
  source: string;
  updated?: string;
  note?: string;
}

interface PriceInfo {
  value?: number;
  min_price?: number;
  max_price?: number;
  currency: string;
  source: string;
  in_stock?: boolean;
  url?: string;
  updated?: string;
}

interface RatingInfo {
  score: number;
  count?: number;
  source: string;
  updated?: string;
}

interface Wine {
  id: string;
  name: string;
  producer?: string;
  vintage?: number;
  wine_type: string;
  country: string;
  region: string;
  appellation?: string;
  classification?: string;
  
  // LWIN Codes
  lwin7?: string;
  lwin11?: string;
  lwin18?: string;
  
  // Extended LWIN Data
  lwin_status?: string;
  lwin_display_name?: string;
  producer_title?: string;
  sub_region?: string;
  site?: string;
  parcel?: string;
  sub_type?: string;
  designation?: string;
  vintage_config?: string;
  lwin_first_vintage?: string;
  lwin_final_vintage?: string;
  lwin_date_added?: string;
  lwin_date_updated?: string;
  lwin_reference?: string;
  
  // Composition
  grape_varieties: GrapeVariety[];
  alcohol_content?: number;
  
  // Characteristics
  body?: string;
  sweetness?: string;
  acidity?: string;
  tannins?: string;
  
  // Tasting
  color: string;
  nose: string[];
  palate: string[];
  tasting_notes: string;
  
  // Food Pairing
  food_pairings: string[];
  
  // Multi-Source Data
  image_url?: string;
  front_label_image?: string;
  back_label_image?: string;
  bottle_image?: string;
  image_sources: Record<string, ImageSource>;
  price_data: Record<string, PriceInfo>;
  ratings: Record<string, RatingInfo>;
  tasting_notes_sources: Record<string, string>;
  
  // External IDs
  vivino_id?: string;
  wine_searcher_id?: string;
  
  // Provenance
  data_source: string;
  enriched_by: string[];
  external_ids: Record<string, string>;
  last_synced: Record<string, string>;
  sync_enabled: Record<string, boolean>;
  manual_overrides: Record<string, any>;
  
  // Management
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export default function AdminWineEditPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [wine, setWine] = useState<Wine | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'lwin' | 'edit' | 'enrichment' | 'provenance'>('lwin');

  const isAdmin = user && user.role === 'admin';

  const fetchWine = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://192.168.1.100:8000/api/admin/wines/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch wine');
      }

      const data = await response.json();
      setWine(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading wine');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (!isAdmin && !loading) {
      router.push('/admin');
    }
  }, [isAdmin, loading, router]);

  useEffect(() => {
    if (isAdmin && id) {
      fetchWine();
    }
  }, [isAdmin, id, fetchWine]);

  async function handleSave() {
    if (!wine) return;

    try {
      setSaving(true);
      const response = await fetch(`http://192.168.1.100:8000/api/admin/wines/${id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(wine)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to save wine' }));
        throw new Error(errorData.detail || 'Failed to save wine');
      }

      alert('✅ Vin enregistré avec succès');
      router.push('/admin/wines');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error saving wine');
      alert(`❌ Erreur: ${err instanceof Error ? err.message : 'Error saving wine'}`);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!wine) return;

    // Show confirmation dialog
    const confirmed = window.confirm(
      `⚠️ ATTENTION: Voulez-vous vraiment supprimer ce vin?\n\n` +
      `Vin: ${wine.name}\n` +
      `Producteur: ${wine.producer || 'N/A'}\n` +
      `Millésime: ${wine.vintage || 'N/A'}\n\n` +
      `Cette action est IRRÉVERSIBLE!`
    );

    if (!confirmed) return;

    try {
      setSaving(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://192.168.1.100:8000/api/admin/wines/${id}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => 
          ({ detail: 'Failed to delete wine' })
        );
        throw new Error(errorData.detail || 'Failed to delete wine');
      }

      alert('✅ Vin supprimé avec succès');
      router.push('/admin/wines');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error deleting wine');
      alert(
        `❌ Erreur lors de la suppression: ${
          err instanceof Error ? err.message : 'Error deleting wine'
        }`
      );
    } finally {
      setSaving(false);
    }
  }

  async function enrichFromVivino() {
    try {
      setLoading(true);
      const response = await fetch(`http://192.168.1.100:8000/api/admin/wines/${id}/enrich`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ sources: ['vivino'] })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Enrichment failed' }));
        throw new Error(errorData.detail || 'Enrichment failed');
      }
      
      await fetchWine();
      alert('✅ Données Vivino ajoutées');
    } catch (err) {
      alert('⚠️ Erreur: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>⏳ Chargement...</div>
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  if (!wine) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>⚠️ Vin non trouvé</div>
      </div>
    );
  }

  const updateWine = (field: keyof Wine, value: any) => {
    if (wine) {
      setWine({ ...wine, [field]: value });
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link href="/admin/wines">
          <button className={styles.backButton}>← Retour au catalogue admin</button>
        </Link>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={handleDelete}
            disabled={saving}
            style={{
              background: '#dc3545',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: saving ? 'not-allowed' : 'pointer',
              opacity: saving ? 0.6 : 1,
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(220,53,69,0.2)'
            }}
            onMouseOver={(e) => {
              if (!saving) {
                e.currentTarget.style.background = '#c82333';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(220,53,69,0.3)';
              }
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = '#dc3545';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(220,53,69,0.2)';
            }}
          >
            {saving ? '⏳ Traitement...' : '🗑️ Supprimer ce vin'}
          </button>
          <button 
            onClick={handleSave} 
            disabled={saving}
            className={styles.saveButton}
          >
            {saving ? '💾 Enregistrement...' : '💾 Enregistrer les modifications'}
          </button>
        </div>
      </div>

      <div className={styles.detailsCard}>
        {/* Header with Name and LWIN Badge */}
        <div className={styles.detailsHeader}>
          {/* Wine Image */}
          {(wine.bottle_image || wine.front_label_image || wine.image_url) && (
            <div style={{ 
              width: '120px',
              height: '120px',
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: '#f5f5f5',
              borderRadius: '8px',
              overflow: 'hidden',
              marginRight: '20px'
            }}>
              <img 
                src={`http://192.168.1.100:8000${wine.bottle_image || wine.front_label_image || wine.image_url}`}
                alt={wine.name}
                style={{ 
                  maxWidth: '100%', 
                  maxHeight: '100%', 
                  objectFit: 'contain' 
                }}
              />
            </div>
          )}
          
          <div className={styles.headerContent}>
            <h1 className={styles.wineName}>{wine.name}</h1>
            {wine.producer && (
              <h2 className={styles.wineProducer}>{wine.producer}</h2>
            )}
            {/* Data Source Badge */}
            <div style={{ marginTop: '10px', display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span style={{
                background: wine.data_source === 'ai' ? 
                  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 
                  wine.data_source === 'lwin' ? '#28a745' : '#6c757d',
                color: 'white',
                padding: '4px 12px',
                borderRadius: '12px',
                fontSize: '0.85rem',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                {wine.data_source === 'ai' && '🤖 Extrait par IA'}
                {wine.data_source === 'lwin' && '📚 Base LWIN'}
                {wine.data_source === 'manual' && '✏️ Manuel'}
                {!wine.data_source && '❓ Source inconnue'}
              </span>
              {wine.enriched_by && wine.enriched_by.length > 0 && (
                <span style={{
                  background: '#17a2b8',
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontWeight: '600'
                }}>
                  ➕ Enrichi ({wine.enriched_by.length})
                </span>
              )}
            </div>
          </div>
          {wine.lwin11 && (
            <div className={styles.lwinBadge} title="Code LWIN">
              LWIN: {wine.lwin11}
            </div>
          )}
        </div>

        {error && (
          <div className={styles.error}>⚠️ {error}</div>
        )}

        {/* Tabs Navigation */}
        <div className={styles.tabs}>
          <button 
            className={`${styles.tab} ${activeTab === 'lwin' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('lwin')}
          >
            � Sources de données
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'edit' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('edit')}
          >
            ✏️ Édition
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'enrichment' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('enrichment')}
          >
            📸 Enrichissement
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'provenance' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('provenance')}
          >
            🔗 Provenance
          </button>
        </div>

        {/* Data Sources Tab */}
        {activeTab === 'lwin' && (
          <div className={styles.tabContent}>
            
            {/* Data Provenance Header */}
            <div style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              marginBottom: '30px',
              borderRadius: '12px',
              padding: '20px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ margin: 0, marginBottom: '15px', fontSize: '1.5rem' }}>
                📊 Sources de données
              </h2>
              <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', fontSize: '0.95rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 'bold', opacity: 0.9 }}>Source principale:</span>
                  <span style={{ 
                    background: 'rgba(255,255,255,0.25)',
                    padding: '6px 14px',
                    borderRadius: '16px',
                    textTransform: 'uppercase',
                    fontWeight: 'bold',
                    letterSpacing: '0.5px'
                  }}>
                    {wine.data_source || 'manual'}
                  </span>
                </div>
                {wine.enriched_by && wine.enriched_by.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: 'bold', opacity: 0.9 }}>Enrichi par:</span>
                    {wine.enriched_by.map((source: string) => (
                      <span key={source} style={{ 
                        background: 'rgba(255,255,255,0.2)',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '0.85rem'
                      }}>
                        {source}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
            
            {/* General Information */}
            <div className={styles.lwinSection}>
              <div className={styles.lwinSectionHeader}>
                <h3>📋 Métadonnées</h3>
              </div>
              <div className={styles.lwinGrid}>
                <div className={styles.lwinRow}>
                  <span className={styles.lwinRowLabel}>Source principale</span>
                  <span className={styles.lwinRowValue}>
                    <code style={{ 
                      background: '#f0f0f0', 
                      padding: '2px 8px', 
                      borderRadius: '4px',
                      color: '#d63384'
                    }}>
                      {wine.data_source || 'manual'}
                    </code>
                  </span>
                </div>
                {wine.lwin_status && (
                  <div className={styles.lwinRow}>
                    <span className={styles.lwinRowLabel}>Statut LWIN</span>
                    <span className={styles.lwinRowValue}>{wine.lwin_status}</span>
                  </div>
                )}
                {wine.lwin_display_name && (
                  <div className={styles.lwinRow}>
                    <span className={styles.lwinRowLabel}>Nom d&apos;affichage LWIN</span>
                    <span className={styles.lwinRowValue}>{wine.lwin_display_name}</span>
                  </div>
                )}
              </div>
            </div>

            {/* LWIN Codes */}
            {(wine.lwin7 || wine.lwin11 || wine.lwin18) && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>🔢 Codes LWIN</h3>
                </div>
                <div className={styles.lwinGrid}>
                  {wine.lwin7 && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>LWIN7</span>
                      <span className={styles.lwinRowValue}><code>{wine.lwin7}</code></span>
                    </div>
                  )}
                  {wine.lwin11 && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>LWIN11</span>
                      <span className={styles.lwinRowValue}><code>{wine.lwin11}</code></span>
                    </div>
                  )}
                  {wine.lwin18 && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>LWIN18</span>
                      <span className={styles.lwinRowValue}><code>{wine.lwin18}</code></span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Producer Information */}
            <div className={styles.lwinSection}>
              <div className={styles.lwinSectionHeader}>
                <h3>🏛️ Producteur</h3>
              </div>
              <div className={styles.lwinGrid}>
                {wine.producer_title && (
                  <div className={styles.lwinRow}>
                    <span className={styles.lwinRowLabel}>Titre</span>
                    <span className={styles.lwinRowValue}>{wine.producer_title}</span>
                  </div>
                )}
                <div className={styles.lwinRow}>
                  <span className={styles.lwinRowLabel}>Nom</span>
                  <span className={styles.lwinRowValue}>{wine.producer || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Wine Details */}
            <div className={styles.lwinSection}>
              <div className={styles.lwinSectionHeader}>
                <h3>🍷 Détails du vin</h3>
              </div>
              <div className={styles.lwinGrid}>
                <div className={styles.lwinRow}>
                  <span className={styles.lwinRowLabel}>Vin</span>
                  <span className={styles.lwinRowValue}>{wine.name}</span>
                </div>
                <div className={styles.lwinRow}>
                  <span className={styles.lwinRowLabel}>Millésime</span>
                  <span className={styles.lwinRowValue}>{wine.vintage || 'N/A'}</span>
                </div>
                <div className={styles.lwinRow}>
                  <span className={styles.lwinRowLabel}>Couleur</span>
                  <span className={styles.lwinRowValue}>{wine.wine_type}</span>
                </div>
                {wine.sub_type && (
                  <div className={styles.lwinRow}>
                    <span className={styles.lwinRowLabel}>Sous-type</span>
                    <span className={styles.lwinRowValue}>{wine.sub_type}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Location & Description */}
            <div className={styles.lwinSection}>
              <div className={styles.lwinSectionHeader}>
                <h3>🌍 Localisation</h3>
              </div>
              <div className={styles.lwinGrid}>
                <div className={styles.lwinRow}>
                  <span className={styles.lwinRowLabel}>Pays</span>
                  <span className={styles.lwinRowValue}>{wine.country}</span>
                </div>
                <div className={styles.lwinRow}>
                  <span className={styles.lwinRowLabel}>Région</span>
                  <span className={styles.lwinRowValue}>{wine.region}</span>
                </div>
                {wine.sub_region && (
                  <div className={styles.lwinRow}>
                    <span className={styles.lwinRowLabel}>Sous-région</span>
                    <span className={styles.lwinRowValue}>{wine.sub_region}</span>
                  </div>
                )}
                {wine.site && (
                  <div className={styles.lwinRow}>
                    <span className={styles.lwinRowLabel}>Site/Vignoble</span>
                    <span className={styles.lwinRowValue}>{wine.site}</span>
                  </div>
                )}
                {wine.parcel && (
                  <div className={styles.lwinRow}>
                    <span className={styles.lwinRowLabel}>Parcelle</span>
                    <span className={styles.lwinRowValue}>{wine.parcel}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Classification */}
            {(wine.designation || wine.classification) && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>🏆 Classification</h3>
                </div>
                <div className={styles.lwinGrid}>
                  {wine.designation && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Désignation</span>
                      <span className={styles.lwinRowValue}>{wine.designation}</span>
                    </div>
                  )}
                  {wine.classification && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Classification</span>
                      <span className={styles.lwinRowValue}>{wine.classification}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Vintage Configuration */}
            {(wine.vintage_config || wine.lwin_first_vintage || wine.lwin_final_vintage) && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>📅 Configuration millésime</h3>
                </div>
                <div className={styles.lwinGrid}>
                  {wine.vintage_config && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Type</span>
                      <span className={styles.lwinRowValue}>{wine.vintage_config}</span>
                    </div>
                  )}
                  {wine.lwin_first_vintage && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Premier millésime</span>
                      <span className={styles.lwinRowValue}>{wine.lwin_first_vintage}</span>
                    </div>
                  )}
                  {wine.lwin_final_vintage && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Dernier millésime</span>
                      <span className={styles.lwinRowValue}>{wine.lwin_final_vintage}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* External IDs */}
            {(wine.vivino_id || wine.wine_searcher_id || (wine.external_ids && Object.keys(wine.external_ids).length > 0)) && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>🔗 Identifiants externes</h3>
                </div>
                <div className={styles.lwinGrid}>
                  {wine.vivino_id && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Vivino ID</span>
                      <span className={styles.lwinRowValue}>
                        <code style={{ background: '#f0f0f0', padding: '2px 8px', borderRadius: '4px' }}>
                          {wine.vivino_id}
                        </code>
                      </span>
                    </div>
                  )}
                  {wine.wine_searcher_id && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Wine-Searcher ID</span>
                      <span className={styles.lwinRowValue}>
                        <code style={{ background: '#f0f0f0', padding: '2px 8px', borderRadius: '4px' }}>
                          {wine.wine_searcher_id}
                        </code>
                      </span>
                    </div>
                  )}
                  {wine.external_ids && Object.entries(wine.external_ids).map(([source, id]) => (
                    <div key={source} className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>{source}</span>
                      <span className={styles.lwinRowValue}>
                        <code style={{ background: '#f0f0f0', padding: '2px 8px', borderRadius: '4px' }}>
                          {String(id)}
                        </code>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Multi-Source Ratings */}
            {wine.ratings && Object.keys(wine.ratings).length > 0 && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>⭐ Évaluations multi-sources</h3>
                </div>
                <div className={styles.lwinGrid}>
                  {Object.entries(wine.ratings).map(([source, rating]: [string, any]) => (
                    <div key={source} className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>
                        {source}
                        {rating.updated && (
                          <span style={{ fontSize: '0.75rem', opacity: 0.6, marginLeft: '5px' }}>
                            ({new Date(rating.updated).toLocaleDateString('fr-FR')})
                          </span>
                        )}
                      </span>
                      <span className={styles.lwinRowValue}>
                        <strong>{rating.score}</strong>
                        {rating.count && (
                          <span style={{ fontSize: '0.85rem', opacity: 0.7, marginLeft: '5px' }}>
                            ({rating.count} avis)
                          </span>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Multi-Source Prices */}
            {wine.price_data && Object.keys(wine.price_data).length > 0 && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>💰 Prix multi-sources</h3>
                </div>
                <div className={styles.lwinGrid}>
                  {Object.entries(wine.price_data).map(([source, price]: [string, any]) => (
                    <div key={source} className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>
                        {source}
                        {price.updated && (
                          <span style={{ fontSize: '0.75rem', opacity: 0.6, marginLeft: '5px' }}>
                            ({new Date(price.updated).toLocaleDateString('fr-FR')})
                          </span>
                        )}
                      </span>
                      <span className={styles.lwinRowValue}>
                        {price.value ? (
                          <strong>{price.value} {price.currency || 'CAD'}</strong>
                        ) : (
                          price.min_price && price.max_price && (
                            <strong>{price.min_price} - {price.max_price} {price.currency || 'CAD'}</strong>
                          )
                        )}
                        {price.in_stock !== undefined && (
                          <span style={{ 
                            fontSize: '0.75rem',
                            marginLeft: '8px',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            background: price.in_stock ? '#d4edda' : '#f8d7da',
                            color: price.in_stock ? '#155724' : '#721c24'
                          }}>
                            {price.in_stock ? '✓ En stock' : '✗ Rupture'}
                          </span>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Timestamps */}
            {(wine.lwin_date_added || wine.lwin_date_updated) && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>🕐 Horodatage</h3>
                </div>
                <div className={styles.lwinGrid}>
                  {wine.lwin_date_added && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Créé</span>
                      <span className={styles.lwinRowValue}>
                        {new Date(wine.lwin_date_added).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                  )}
                  {wine.lwin_date_updated && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Mis à jour</span>
                      <span className={styles.lwinRowValue}>
                        {new Date(wine.lwin_date_updated).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                  )}
                  {wine.lwin_reference && (
                    <div className={styles.lwinRow}>
                      <span className={styles.lwinRowLabel}>Référence</span>
                      <span className={styles.lwinRowValue}>{wine.lwin_reference}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Grapes */}
            {wine.grape_varieties && wine.grape_varieties.length > 0 && (
              <div className={styles.lwinSection}>
                <div className={styles.lwinSectionHeader}>
                  <h3>🍇 Cépages</h3>
                </div>
                <div className={styles.grapeList}>
                  {wine.grape_varieties.map((grape, index) => (
                    <div key={index} className={styles.grapeBadge}>
                      {grape.name} {grape.percentage && `${grape.percentage}%`}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Edit Tab (Editable Fields) */}
        {activeTab === 'edit' && (
          <div className={styles.tabContent}>
            {/* Main Information */}
            <div className={styles.editSection}>
              <div className={styles.editSectionHeader}>
                <h3>📋 Informations principales</h3>
              </div>
              <div className={styles.editGrid}>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Millésime</label>
                  <input
                    type="number"
                    value={wine.vintage || ''}
                    onChange={(e) => updateWine('vintage', parseInt(e.target.value) || null)}
                    className={styles.editInput}
                    placeholder="Année"
                  />
                </div>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Type</label>
                  <select
                    value={wine.wine_type}
                    onChange={(e) => updateWine('wine_type', e.target.value)}
                    className={styles.editInput}
                  >
                    <option value="red">Rouge</option>
                    <option value="white">Blanc</option>
                    <option value="rosé">Rosé</option>
                    <option value="sparkling">Effervescent</option>
                    <option value="dessert">Dessert</option>
                    <option value="fortified">Fortifié</option>
                  </select>
                </div>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Pays</label>
                  <input
                    type="text"
                    value={wine.country}
                    onChange={(e) => updateWine('country', e.target.value)}
                    className={styles.editInput}
                    placeholder="France"
                  />
                </div>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Région</label>
                  <input
                    type="text"
                    value={wine.region}
                    onChange={(e) => updateWine('region', e.target.value)}
                    className={styles.editInput}
                    placeholder="Alsace"
                  />
                </div>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Appellation</label>
                  <input
                    type="text"
                    value={wine.appellation || ''}
                    onChange={(e) => updateWine('appellation', e.target.value)}
                    className={styles.editInput}
                    placeholder="AOP"
                  />
                </div>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Classification</label>
                  <input
                    type="text"
                    value={wine.classification || ''}
                    onChange={(e) => updateWine('classification', e.target.value)}
                    className={styles.editInput}
                    placeholder="Grand Cru"
                  />
                </div>
              </div>
            </div>

            {/* Grape Varieties */}
            <div className={styles.editSection}>
              <div className={styles.editSectionHeader}>
                <h3>🍇 Cépages</h3>
              </div>
              <div className={styles.editContent}>
                {wine.grape_varieties.map((grape, index) => (
                  <div key={index} className={styles.grapeRow}>
                    <input
                      type="text"
                      value={grape.name}
                      onChange={(e) => {
                        const newGrapes = [...wine.grape_varieties];
                        newGrapes[index] = { ...grape, name: e.target.value };
                        updateWine('grape_varieties', newGrapes);
                      }}
                      className={styles.grapeInput}
                      placeholder="Nom du cépage"
                    />
                    <input
                      type="number"
                      value={grape.percentage || ''}
                      onChange={(e) => {
                        const newGrapes = [...wine.grape_varieties];
                        newGrapes[index] = { ...grape, percentage: parseInt(e.target.value) || undefined };
                        updateWine('grape_varieties', newGrapes);
                      }}
                      className={styles.percentInput}
                      placeholder="%"
                      min="0"
                      max="100"
                    />
                    <button
                      onClick={() => {
                        const newGrapes = wine.grape_varieties.filter((_, i) => i !== index);
                        updateWine('grape_varieties', newGrapes);
                      }}
                      className={styles.removeButton}
                      title="Supprimer"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => {
                    const newGrapes = [...wine.grape_varieties, { name: '', percentage: undefined }];
                    updateWine('grape_varieties', newGrapes);
                  }}
                  className={styles.addGrapeButton}
                >
                  + Ajouter un cépage
                </button>
              </div>
            </div>

            {/* Tasting Notes */}
            <div className={styles.editSection}>
              <div className={styles.editSectionHeader}>
                <h3>🍷 Notes de dégustation</h3>
              </div>
              <div className={styles.editContent}>
                <textarea
                  value={wine.tasting_notes}
                  onChange={(e) => updateWine('tasting_notes', e.target.value)}
                  className={styles.editTextarea}
                  rows={6}
                  placeholder="Description des caractéristiques organoleptiques du vin..."
                />
              </div>
            </div>

            {/* LWIN Codes (Read-Only) - Removed, now shown in LWIN tab */}

            {/* Additional Fields */}
            <div className={styles.editSection}>
              <div className={styles.editSectionHeader}>
                <h3>➕ Champs additionnels</h3>
              </div>
              <div className={styles.editGrid}>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Teneur en alcool</label>
                  <input
                    type="number"
                    step="0.1"
                    value={wine.alcohol_content || ''}
                    onChange={(e) => updateWine('alcohol_content', parseFloat(e.target.value) || undefined)}
                    className={styles.editInput}
                    placeholder="% vol."
                  />
                </div>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Corps</label>
                  <select
                    value={wine.body || ''}
                    onChange={(e) => updateWine('body', e.target.value || undefined)}
                    className={styles.editInput}
                  >
                    <option value="">Non spécifié</option>
                    <option value="léger">Léger</option>
                    <option value="moyen">Moyen</option>
                    <option value="corsé">Corsé</option>
                  </select>
                </div>
                <div className={styles.editField}>
                  <label className={styles.editLabel}>Douceur</label>
                  <select
                    value={wine.sweetness || ''}
                    onChange={(e) => updateWine('sweetness', e.target.value || undefined)}
                    className={styles.editInput}
                  >
                    <option value="">Non spécifié</option>
                    <option value="sec">Sec</option>
                    <option value="demi-sec">Demi-sec</option>
                    <option value="moelleux">Moelleux</option>
                    <option value="doux">Doux</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Image Upload Section */}
            <WineImageUpload
              wineId={wine.id}
              existingImages={{
                front_label_image: wine.front_label_image,
                back_label_image: wine.back_label_image,
                bottle_image: wine.bottle_image
              }}
              onUploadComplete={(images) => {
                // Update wine state with new image URLs
                setWine({
                  ...wine,
                  front_label_image: images.front_label_image || wine.front_label_image,
                  back_label_image: images.back_label_image || wine.back_label_image,
                  bottle_image: images.bottle_image || wine.bottle_image
                });
              }}
            />
          </div>
        )}

        {/* Enrichment Tab */}
        {activeTab === 'enrichment' && (
          <div className={styles.tabContent}>
            <div className={styles.section}>
              <h2 className={styles.sectionTitle}>📸 Images</h2>
              
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                gap: '20px',
                marginBottom: '20px'
              }}>
                {/* Primary Image (uploaded photo) */}
                {wine.image_url && (
                  <div style={{ 
                    border: '2px solid #4CAF50', 
                    borderRadius: '8px', 
                    padding: '15px',
                    textAlign: 'center'
                  }}>
                    <h4 style={{ marginTop: 0, marginBottom: '10px', fontSize: '1rem' }}>
                      📸 Photo téléchargée
                    </h4>
                    <img 
                      src={`http://192.168.1.100:8000${wine.image_url}`}
                      alt="Uploaded photo" 
                      style={{ 
                        maxWidth: '100%', 
                        maxHeight: '200px', 
                        objectFit: 'contain',
                        borderRadius: '4px'
                      }}
                    />
                  </div>
                )}
                
                {/* Front Label */}
                <div style={{ 
                  border: '2px solid #e0e0e0', 
                  borderRadius: '8px', 
                  padding: '15px',
                  textAlign: 'center'
                }}>
                  <h4 style={{ marginTop: 0, marginBottom: '10px', fontSize: '1rem' }}>
                    Étiquette avant
                  </h4>
                  {wine.front_label_image ? (
                    <img 
                      src={`http://192.168.1.100:8000${wine.front_label_image}`}
                      alt="Front label" 
                      style={{ 
                        maxWidth: '100%', 
                        maxHeight: '200px', 
                        objectFit: 'contain',
                        borderRadius: '4px'
                      }}
                    />
                  ) : (
                    <div style={{ 
                      height: '200px', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      background: '#f5f5f5',
                      borderRadius: '4px',
                      color: '#999'
                    }}>
                      📷 Aucune image
                    </div>
                  )}
                </div>

                {/* Back Label */}
                <div style={{ 
                  border: '2px solid #e0e0e0', 
                  borderRadius: '8px', 
                  padding: '15px',
                  textAlign: 'center'
                }}>
                  <h4 style={{ marginTop: 0, marginBottom: '10px', fontSize: '1rem' }}>
                    Étiquette arrière
                  </h4>
                  {wine.back_label_image ? (
                    <img 
                      src={`http://192.168.1.100:8000${wine.back_label_image}`}
                      alt="Back label" 
                      style={{ 
                        maxWidth: '100%', 
                        maxHeight: '200px', 
                        objectFit: 'contain',
                        borderRadius: '4px'
                      }}
                    />
                  ) : (
                    <div style={{ 
                      height: '200px', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      background: '#f5f5f5',
                      borderRadius: '4px',
                      color: '#999'
                    }}>
                      📷 Aucune image
                    </div>
                  )}
                </div>

                {/* Bottle Image */}
                <div style={{ 
                  border: '2px solid #e0e0e0', 
                  borderRadius: '8px', 
                  padding: '15px',
                  textAlign: 'center'
                }}>
                  <h4 style={{ marginTop: 0, marginBottom: '10px', fontSize: '1rem' }}>
                    Bouteille complète
                  </h4>
                  {wine.bottle_image ? (
                    <img 
                      src={`http://192.168.1.100:8000${wine.bottle_image}`}
                      alt="Bottle" 
                      style={{ 
                        maxWidth: '100%', 
                        maxHeight: '200px', 
                        objectFit: 'contain',
                        borderRadius: '4px'
                      }}
                    />
                  ) : (
                    <div style={{ 
                      height: '200px', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      background: '#f5f5f5',
                      borderRadius: '4px',
                      color: '#999'
                    }}>
                      🍷 Aucune image
                    </div>
                  )}
                </div>
              </div>

              {/* External Images from AI/Google Search */}
              {wine.image_sources && Object.keys(wine.image_sources).length > 0 && (
                <div style={{ marginTop: '30px' }}>
                  <h3 style={{ marginBottom: '15px', fontSize: '1.1rem' }}>
                    🌐 Images externes trouvées par l&apos;IA ({Object.keys(wine.image_sources).length})
                  </h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', 
                    gap: '15px'
                  }}>
                    {Object.entries(wine.image_sources).map(([key, imgSource]) => (
                      <div key={key} style={{ 
                        border: '1px solid #ddd', 
                        borderRadius: '8px', 
                        padding: '10px',
                        textAlign: 'center',
                        background: '#fff'
                      }}>
                        <img 
                          src={imgSource.url}
                          alt={`External ${key}`}
                          style={{ 
                            width: '100%', 
                            height: '150px', 
                            objectFit: 'contain',
                            borderRadius: '4px',
                            marginBottom: '8px'
                          }}
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            const parent = e.currentTarget.parentElement;
                            if (parent) {
                              const fallback = document.createElement('div');
                              fallback.style.cssText = 'height: 150px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 32px;';
                              fallback.textContent = '🖼️';
                              parent.insertBefore(fallback, e.currentTarget.nextSibling);
                            }
                          }}
                        />
                        <div style={{ fontSize: '0.8rem', color: '#666' }}>
                          {imgSource.source || 'google'}
                        </div>
                        {imgSource.quality && (
                          <div style={{ fontSize: '0.75rem', color: '#999', marginTop: '4px' }}>
                            Qualité: {imgSource.quality}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className={styles.enrichmentActions}>
                <button disabled className={styles.enrichButton}>
                  🍷 Chercher sur Vivino (À venir)
                </button>
                <button disabled className={styles.enrichButton}>
                  💰 Wine-Searcher (À venir)
                </button>
              </div>
            </div>

            {wine.ratings && Object.keys(wine.ratings).length > 0 && (
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>⭐ Évaluations</h2>
                <div className={styles.ratingsGrid}>
                  {Object.entries(wine.ratings).map(([source, rating]) => (
                    <div key={source} className={styles.ratingCard}>
                      <span className={`${styles.sourceBadge} ${styles[source]}`}>
                        {source}
                      </span>
                      <div className={styles.ratingScore}>{rating.score}</div>
                      {rating.count && (
                        <div className={styles.ratingCount}>
                          {rating.count.toLocaleString()} évaluations
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {wine.price_data && Object.keys(wine.price_data).length > 0 && (
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>💰 Prix</h2>
                <div className={styles.pricesGrid}>
                  {Object.entries(wine.price_data).map(([source, price]) => (
                    <div key={source} className={styles.priceCard}>
                      <span className={`${styles.sourceBadge} ${styles[source]}`}>
                        {source}
                      </span>
                      <div className={styles.priceValue}>
                        {price.min_price && price.max_price ? (
                          `${price.min_price} - ${price.max_price} ${price.currency}`
                        ) : price.value ? (
                          `${price.value} ${price.currency}`
                        ) : 'N/A'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Provenance Tab */}
        {activeTab === 'provenance' && (
          <div className={styles.tabContent}>
            <div className={styles.section}>
              <h2 className={styles.sectionTitle}>🔗 Source de données</h2>
              <p className={styles.readOnlyValue}>
                <strong>Source principale:</strong> {wine.data_source?.toUpperCase() || 'N/A'}
              </p>
              {wine.enriched_by && wine.enriched_by.length > 0 && (
                <p className={styles.readOnlyValue}>
                  <strong>Enrichi par:</strong> {wine.enriched_by.join(', ')}
                </p>
              )}
            </div>

            {wine.external_ids && Object.keys(wine.external_ids).length > 0 && (
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>🔗 IDs Externes</h2>
                <div className={styles.externalIds}>
                  {Object.entries(wine.external_ids).map(([source, id]) => (
                    <div key={source} className={styles.externalId}>
                      <span className={`${styles.sourceBadge} ${styles[source]}`}>
                        {source}
                      </span>
                      <code>{id}</code>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {wine.last_synced && Object.keys(wine.last_synced).length > 0 && (
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>🔄 Synchronisation</h2>
                <div className={styles.syncGrid}>
                  {Object.entries(wine.last_synced).map(([source, date]) => (
                    <div key={source} className={styles.syncItem}>
                      <strong>{source}:</strong> {new Date(date).toLocaleString('fr-FR')}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
