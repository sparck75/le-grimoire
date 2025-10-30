'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../../../../contexts/AuthContext';

export default function AdminNewWinePage() {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const uploadImageToWine = async (wineId: string) => {
    if (!selectedImage) return;

    try {
      const apiUrl = getApiUrl();
      const token = localStorage.getItem('access_token');

      const formDataUpload = new FormData();
      formDataUpload.append('file', selectedImage);

      setUploadingImage(true);

      const response = await fetch(`${apiUrl}/api/admin/wines/${wineId}/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataUpload
      });

      if (!response.ok) {
        console.error('Failed to upload image');
      }
    } catch (err) {
      console.error('Error uploading image:', err);
    } finally {
      setUploadingImage(false);
    }
  };

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const apiUrl = getApiUrl();
      const token = localStorage.getItem('access_token');
      
      // Prepare data
      const data: any = {
        name: formData.name,
        wine_type: formData.wine_type,
        is_public: true,  // Master wines are public
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

      const response = await fetch(`${apiUrl}/api/admin/wines`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create wine');
      }

      const createdWine = await response.json();

      // Upload image if selected
      if (selectedImage && createdWine.id) {
        await uploadImageToWine(createdWine.id);
      }

      router.push('/admin/wines');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(false);
    }
  };

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

  return (
    <div>
      <div className="admin-header">
        <h1>➕ Ajouter un Vin (Base de Données)</h1>
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

      <div className="admin-card">
        <div className="card-header">
          <h2>Informations du Vin</h2>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
            Ce vin sera ajouté à la base de données maître. Les utilisateurs pourront le scanner ou l&apos;ajouter à leur cellier.
          </p>
        </div>
        <div className="card-content">
          <form onSubmit={handleSubmit}>
            {/* Image Upload Section */}
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Photo de la Bouteille</h3>
              
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '2rem' }}>
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
                  {imagePreview ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={imagePreview}
                      alt="Aperçu"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <span style={{ fontSize: '4rem' }}>🍷</span>
                  )}
                </div>
                
                <div style={{ flex: 1 }}>
                  <label 
                    htmlFor="wine-image"
                    className="btn btn-primary"
                    style={{ cursor: 'pointer', display: 'inline-block' }}
                  >
                    📷 Choisir une photo
                  </label>
                  <input
                    id="wine-image"
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    style={{ display: 'none' }}
                  />
                  <p style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
                    Formats acceptés: JPG, PNG, GIF (max 5MB)
                  </p>
                  {selectedImage && (
                    <p style={{ marginTop: '0.5rem', color: '#28a745', fontSize: '0.9rem' }}>
                      ✓ {selectedImage.name}
                    </p>
                  )}
                </div>
              </div>
            </div>

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
                  Code-Barres (pour scanner)
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
              <button type="submit" className="btn btn-success" disabled={loading || uploadingImage}>
                {uploadingImage ? 'Téléchargement de l\'image...' : loading ? 'Ajout en cours...' : 'Ajouter le Vin'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
