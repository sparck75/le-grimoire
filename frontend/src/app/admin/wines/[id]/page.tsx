'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../../../../contexts/AuthContext';

interface Wine {
  id: string;
  name: string;
  producer?: string;
  vintage?: number;
  wine_type: string;
  country: string;
  region: string;
  appellation?: string;
  alcohol_content?: number;
  body?: string;
  sweetness?: string;
  tasting_notes: string;
  food_pairings: string[];
  barcode?: string;
  image_url?: string;
}

export default function AdminEditWinePage() {
  const router = useRouter();
  const params = useParams();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [wine, setWine] = useState<Wine | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    producer: '',
    vintage: '',
    wine_type: 'red',
    country: '',
    region: '',
    appellation: '',
    alcohol_content: '',
    body: '',
    sweetness: '',
    tasting_notes: '',
    food_pairings: '',
    barcode: '',
  });

  const isAdmin = user && user.role === 'admin';

  useEffect(() => {
    if (isAdmin) {
      fetchWine();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin, params.id]);

  const getApiUrl = () => {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!envUrl || envUrl.includes('localhost')) {
      if (typeof window !== 'undefined') {
        return window.location.origin;
      }
      return 'https://legrimoireonline.ca';
    }
    return envUrl;
  };

  async function fetchWine() {
    try {
      const apiUrl = getApiUrl();
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${apiUrl}/api/admin/wines/${params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Wine not found');
      }

      const wineData = await response.json();
      setWine(wineData);
      
      // Populate form
      setFormData({
        name: wineData.name || '',
        producer: wineData.producer || '',
        vintage: wineData.vintage ? String(wineData.vintage) : '',
        wine_type: wineData.wine_type || 'red',
        country: wineData.country || '',
        region: wineData.region || '',
        appellation: wineData.appellation || '',
        alcohol_content: wineData.alcohol_content ? String(wineData.alcohol_content) : '',
        body: wineData.body || '',
        sweetness: wineData.sweetness || '',
        tasting_notes: wineData.tasting_notes || '',
        food_pairings: wineData.food_pairings ? wineData.food_pairings.join(', ') : '',
        barcode: wineData.barcode || '',
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading wine');
    } finally {
      setLoading(false);
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  async function uploadImage(file: File) {
    try {
      const apiUrl = getApiUrl();
      const token = localStorage.getItem('access_token');

      const formDataUpload = new FormData();
      formDataUpload.append('file', file);

      setUploadingImage(true);

      const response = await fetch(`${apiUrl}/api/admin/wines/${params.id}/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataUpload
      });

      if (response.ok) {
        const data = await response.json();
        setWine(prev => prev ? { ...prev, image_url: data.url } : null);
        alert('Image téléchargée avec succès!');
      } else {
        alert('Erreur lors du téléchargement de l\'image');
      }
    } catch (err) {
      alert('Erreur lors du téléchargement de l\'image');
    } finally {
      setUploadingImage(false);
    }
  }

  function handleImageUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      uploadImage(file);
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const apiUrl = getApiUrl();
      const token = localStorage.getItem('access_token');
      
      // Prepare data
      const data: any = {
        name: formData.name,
        wine_type: formData.wine_type,
      };

      if (formData.producer) data.producer = formData.producer;
      if (formData.vintage) data.vintage = parseInt(formData.vintage);
      if (formData.country) data.country = formData.country;
      if (formData.region) data.region = formData.region;
      if (formData.appellation) data.appellation = formData.appellation;
      if (formData.alcohol_content) data.alcohol_content = parseFloat(formData.alcohol_content);
      if (formData.body) data.body = formData.body;
      if (formData.sweetness) data.sweetness = formData.sweetness;
      if (formData.tasting_notes) data.tasting_notes = formData.tasting_notes;
      if (formData.barcode) data.barcode = formData.barcode;
      
      // Convert comma-separated food pairings to array
      if (formData.food_pairings) {
        data.food_pairings = formData.food_pairings.split(',').map(s => s.trim()).filter(s => s);
      }

      const response = await fetch(`${apiUrl}/api/admin/wines/${params.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update wine');
      }

      router.push('/admin/wines');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div>
        <div className="admin-header">
          <h1>Modifier un Vin</h1>
        </div>
        <div className="loading">Chargement...</div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div>
        <div className="admin-header">
          <h1>Accès refusé</h1>
        </div>
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Vous devez être administrateur pour accéder à cette page.</p>
          <Link href="/admin" className="btn btn-primary">Retour</Link>
        </div>
      </div>
    );
  }

  if (!wine) {
    return (
      <div>
        <div className="admin-header">
          <h1>Vin non trouvé</h1>
        </div>
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Le vin demandé n&apos;existe pas.</p>
          <Link href="/admin/wines" className="btn btn-primary">← Retour à la liste</Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="admin-header">
        <h1>✏️ Modifier le Vin</h1>
        <Link href="/admin/wines" className="btn btn-secondary">
          ← Retour
        </Link>
      </div>

      {error && (
        <div style={{
          background: '#fee',
          color: '#c33',
          padding: '1rem',
          borderRadius: '8px',
          margin: '1rem 0',
          border: '1px solid #fcc'
        }}>
          {error}
        </div>
      )}

      <div className="admin-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <h2>Photo de la Bouteille</h2>
        </div>
        <div className="card-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
            <div style={{ 
              width: '150px', 
              height: '200px', 
              background: '#f5f5f5', 
              borderRadius: '8px', 
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid #e0e0e0'
            }}>
              {wine.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={getApiUrl() + wine.image_url}
                  alt={wine.name}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <span style={{ fontSize: '4rem' }}>🍷</span>
              )}
            </div>
            <div>
              <label 
                htmlFor="wine-image-upload"
                className="btn btn-primary"
                style={{ cursor: uploadingImage ? 'wait' : 'pointer' }}
              >
                {uploadingImage ? 'Téléchargement...' : '📷 Télécharger une photo'}
              </label>
              <input
                id="wine-image-upload"
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                disabled={uploadingImage}
                style={{ display: 'none' }}
              />
              <p style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
                Formats acceptés: JPG, PNG, GIF (max 5MB)
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="admin-card">
        <div className="card-header">
          <h2>Informations du Vin</h2>
        </div>
        <div className="card-content">
          <form onSubmit={handleSubmit}>
            {/* Same form fields as create page */}
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Informations de Base</h3>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                  Nom du vin *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="Ex: Château Margaux"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Producteur
                  </label>
                  <input
                    type="text"
                    name="producer"
                    value={formData.producer}
                    onChange={handleChange}
                    placeholder="Ex: Château Margaux"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Millésime
                  </label>
                  <input
                    type="number"
                    name="vintage"
                    value={formData.vintage}
                    onChange={handleChange}
                    placeholder="Ex: 2015"
                    min="1800"
                    max={new Date().getFullYear() + 1}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Type de vin *
                  </label>
                  <select
                    name="wine_type"
                    value={formData.wine_type}
                    onChange={handleChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  >
                    <option value="red">Rouge</option>
                    <option value="white">Blanc</option>
                    <option value="rosé">Rosé</option>
                    <option value="sparkling">Mousseux</option>
                    <option value="dessert">Dessert</option>
                    <option value="fortified">Fortifié</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Alcool (%)
                  </label>
                  <input
                    type="number"
                    name="alcohol_content"
                    value={formData.alcohol_content}
                    onChange={handleChange}
                    placeholder="Ex: 13.5"
                    step="0.1"
                    min="0"
                    max="100"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                  Code-Barres
                </label>
                <input
                  type="text"
                  name="barcode"
                  value={formData.barcode}
                  onChange={handleChange}
                  placeholder="Ex: 3760059560123"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px',
                    fontFamily: 'monospace'
                  }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Provenance</h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Pays
                  </label>
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    placeholder="Ex: France"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Région
                  </label>
                  <input
                    type="text"
                    name="region"
                    value={formData.region}
                    onChange={handleChange}
                    placeholder="Ex: Bordeaux"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                  Appellation
                </label>
                <input
                  type="text"
                  name="appellation"
                  value={formData.appellation}
                  onChange={handleChange}
                  placeholder="Ex: Margaux"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px'
                  }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Caractéristiques</h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Corps
                  </label>
                  <select
                    name="body"
                    value={formData.body}
                    onChange={handleChange}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  >
                    <option value="">-</option>
                    <option value="light">Léger</option>
                    <option value="medium">Moyen</option>
                    <option value="full">Corsé</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                    Douceur
                  </label>
                  <select
                    name="sweetness"
                    value={formData.sweetness}
                    onChange={handleChange}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  >
                    <option value="">-</option>
                    <option value="dry">Sec</option>
                    <option value="off-dry">Demi-sec</option>
                    <option value="sweet">Doux</option>
                    <option value="very-sweet">Très doux</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                  Notes de dégustation
                </label>
                <textarea
                  name="tasting_notes"
                  value={formData.tasting_notes}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Décrivez les arômes, la structure..."
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Accords</h3>
              
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                  Accords mets-vins
                  <span style={{ fontWeight: 'normal', color: '#666', marginLeft: '0.5rem' }}>
                    (séparés par des virgules)
                  </span>
                </label>
                <input
                  type="text"
                  name="food_pairings"
                  value={formData.food_pairings}
                  onChange={handleChange}
                  placeholder="Ex: Viandes rouges, Fromages affinés, Gibier"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px'
                  }}
                />
              </div>
            </div>

            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '1rem',
              padding: '1.5rem',
              background: '#f8f9fa',
              borderRadius: '8px'
            }}>
              <Link href="/admin/wines" className="btn btn-secondary">
                Annuler
              </Link>
              <button type="submit" className="btn btn-success" disabled={saving}>
                {saving ? 'Enregistrement...' : 'Enregistrer les modifications'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
