'use client';

/**
 * Admin Wine Edit - LWIN Style with Multi-Source Fields
 * Similar to LWIN details page but with editable fields
 */

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import styles from './wine-edit.module.css';

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
  country: string;
  region: string;
  appellation?: string;
  classification?: string;
  
  lwin7?: string;
  lwin11?: string;
  lwin18?: string;
  
  grape_varieties: GrapeVariety[];
  alcohol_content?: number;
  
  body?: string;
  sweetness?: string;
  acidity?: string;
  tannins?: string;
  
  color: string;
  nose: string[];
  palate: string[];
  tasting_notes: string;
  food_pairings: string[];
  
  image_url?: string;
  data_source: string;
  enriched_by: string[];
  is_public: boolean;
}

export default function AdminWineEditPage() {
  const { id } = useParams();
  const router = useRouter();
  const [wine, setWine] = useState<Wine | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchWine();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function fetchWine() {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/admin/wines/${id}`, {
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
  }

  async function handleSave() {
    if (!wine) return;

    try {
      setSaving(true);
      const response = await fetch(`/api/admin/wines/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(wine)
      });

      if (!response.ok) {
        throw new Error('Failed to save wine');
      }

      alert('✅ Vin enregistré avec succès');
      router.push('/admin/wines');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error saving wine');
    } finally {
      setSaving(false);
    }
  }

  const updateWine = (field: keyof Wine, value: any) => {
    if (wine) {
      setWine({ ...wine, [field]: value });
    }
  };

  const translateWineType = (type: string): string => {
    const translations: Record<string, string> = {
      'red': 'Rouge',
      'white': 'Blanc',
      'rosé': 'Rosé',
      'sparkling': 'Effervescent',
      'dessert': 'Dessert',
      'fortified': 'Fortifié'
    };
    return translations[type.toLowerCase()] || type;
  };

  if (loading && !wine) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  if (!wine) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>Vin non trouvé</div>
        <Link href="/admin/wines">
          <button className={styles.backButton}>← Retour</button>
        </Link>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link href="/admin/wines">
          <button className={styles.backButton}>← Retour au catalogue</button>
        </Link>
        <button 
          onClick={handleSave} 
          disabled={saving}
          className={styles.saveButton}
        >
          {saving ? '💾 Enregistrement...' : '💾 Enregistrer'}
        </button>
      </div>

      <div className={styles.detailsCard}>
        {/* Header */}
        <div className={styles.detailsHeader}>
          <div className={styles.headerContent}>
            <input
              type="text"
              value={wine.name}
              onChange={(e) => updateWine('name', e.target.value)}
              className={styles.nameInput}
              placeholder="Nom du vin"
            />
            <input
              type="text"
              value={wine.producer || ''}
              onChange={(e) => updateWine('producer', e.target.value)}
              className={styles.producerInput}
              placeholder="Producteur"
            />
          </div>
          {wine.lwin11 && (
            <div className={styles.lwinBadge} title="Code LWIN">
              LWIN: {wine.lwin11}
            </div>
          )}
        </div>

        {error && <div className={styles.error}>⚠️ {error}</div>}

        {/* Source Badge */}
        <div className={styles.sourceIndicator}>
          <span className={styles.sourceLabel}>Source:</span>
          <span className={`${styles.sourceBadge} ${styles[wine.data_source]}`}>
            {wine.data_source.toUpperCase()}
          </span>
          {wine.enriched_by.length > 0 && (
            <>
              <span className={styles.enrichedLabel}>+ {wine.enriched_by.join(', ')}</span>
            </>
          )}
        </div>

        {/* Main Info Grid - Editable */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Informations principales</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Millésime</label>
              <input
                type="number"
                value={wine.vintage || ''}
                onChange={(e) => updateWine('vintage', parseInt(e.target.value) || null)}
                className={styles.input}
                placeholder="2020"
              />
            </div>
            
            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Type</label>
              <select
                value={wine.wine_type}
                onChange={(e) => updateWine('wine_type', e.target.value)}
                className={styles.select}
              >
                <option value="red">Rouge</option>
                <option value="white">Blanc</option>
                <option value="rosé">Rosé</option>
                <option value="sparkling">Effervescent</option>
                <option value="dessert">Dessert</option>
                <option value="fortified">Fortifié</option>
              </select>
            </div>

            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Pays</label>
              <input
                type="text"
                value={wine.country}
                onChange={(e) => updateWine('country', e.target.value)}
                className={styles.input}
                placeholder="France"
              />
            </div>

            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Région</label>
              <input
                type="text"
                value={wine.region}
                onChange={(e) => updateWine('region', e.target.value)}
                className={styles.input}
                placeholder="Bordeaux"
              />
            </div>

            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Appellation</label>
              <input
                type="text"
                value={wine.appellation || ''}
                onChange={(e) => updateWine('appellation', e.target.value)}
                className={styles.input}
                placeholder="Margaux"
              />
            </div>

            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Classification</label>
              <input
                type="text"
                value={wine.classification || ''}
                onChange={(e) => updateWine('classification', e.target.value)}
                className={styles.input}
                placeholder="First Growth"
              />
            </div>

            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Alcool (%)</label>
              <input
                type="number"
                step="0.1"
                value={wine.alcohol_content || ''}
                onChange={(e) => updateWine('alcohol_content', parseFloat(e.target.value) || null)}
                className={styles.input}
                placeholder="13.5"
              />
            </div>
          </div>
        </div>

        {/* Grape Varieties - Editable */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Cépages</h2>
          <div className={styles.grapeList}>
            {wine.grape_varieties && wine.grape_varieties.map((grape, idx) => (
              <div key={idx} className={styles.grapeItem}>
                <input
                  type="text"
                  value={grape.name}
                  onChange={(e) => {
                    const newGrapes = [...wine.grape_varieties];
                    newGrapes[idx].name = e.target.value;
                    updateWine('grape_varieties', newGrapes);
                  }}
                  className={styles.grapeInput}
                  placeholder="Cépage"
                />
                <input
                  type="number"
                  value={grape.percentage || ''}
                  onChange={(e) => {
                    const newGrapes = [...wine.grape_varieties];
                    newGrapes[idx].percentage = parseFloat(e.target.value) || undefined;
                    updateWine('grape_varieties', newGrapes);
                  }}
                  className={styles.percentInput}
                  placeholder="%"
                />
                <button
                  onClick={() => {
                    const newGrapes = wine.grape_varieties.filter((_, i) => i !== idx);
                    updateWine('grape_varieties', newGrapes);
                  }}
                  className={styles.removeButton}
                >
                  ✕
                </button>
              </div>
            ))}
            <button
              onClick={() => {
                const newGrapes = [...(wine.grape_varieties || []), { name: '', percentage: undefined }];
                updateWine('grape_varieties', newGrapes);
              }}
              className={styles.addButton}
            >
              ➕ Ajouter un cépage
            </button>
          </div>
        </div>

        {/* Tasting Notes */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Notes de dégustation</h2>
          <textarea
            value={wine.tasting_notes}
            onChange={(e) => updateWine('tasting_notes', e.target.value)}
            className={styles.textarea}
            placeholder="Description des arômes, du palais, de la finale..."
            rows={6}
          />
        </div>

        {/* LWIN Codes - Read-only */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Codes LWIN</h2>
          <div className={styles.lwinCodes}>
            {wine.lwin7 && (
              <div className={styles.lwinCode}>
                <span className={styles.lwinCodeLabel}>LWIN7:</span>
                <code className={styles.lwinCodeValue}>{wine.lwin7}</code>
              </div>
            )}
            {wine.lwin11 && (
              <div className={styles.lwinCode}>
                <span className={styles.lwinCodeLabel}>LWIN11:</span>
                <code className={styles.lwinCodeValue}>{wine.lwin11}</code>
              </div>
            )}
            {wine.lwin18 && (
              <div className={styles.lwinCode}>
                <span className={styles.lwinCodeLabel}>LWIN18:</span>
                <code className={styles.lwinCodeValue}>{wine.lwin18}</code>
              </div>
            )}
          </div>
        </div>

        {/* Additional Fields */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Champs additionnels</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Image URL</label>
              <input
                type="text"
                value={wine.image_url || ''}
                onChange={(e) => updateWine('image_url', e.target.value)}
                className={styles.input}
                placeholder="https://example.com/wine.jpg"
              />
            </div>
            
            <div className={styles.infoItem}>
              <label className={styles.infoLabel}>Public</label>
              <label className={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={wine.is_public}
                  onChange={(e) => updateWine('is_public', e.target.checked)}
                />
                <span>Visible dans le catalogue</span>
              </label>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className={styles.actions}>
          <button
            onClick={handleSave}
            disabled={saving}
            className={styles.saveButtonLarge}
          >
            {saving ? '⏳ Enregistrement...' : '💾 Enregistrer les modifications'}
          </button>
        </div>
      </div>
    </div>
  );
}
