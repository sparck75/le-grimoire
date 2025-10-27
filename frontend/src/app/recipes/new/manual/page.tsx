'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../../../contexts/AuthContext';
import Link from 'next/link';
import ImageUpload from '../../../components/ImageUpload';

interface Recipe {
  title: string;
  description: string;
  ingredients: string[];
  equipment: string[];
  instructions: string;
  servings: number | null;
  prep_time: number | null;
  cook_time: number | null;
  total_time: number | null;
  category: string;
  cuisine: string;
  image_url: string | null;
  is_public: boolean;
}

export default function ManualRecipeNewPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [ingredients, setIngredients] = useState<string[]>(['']);
  const [equipment, setEquipment] = useState<string[]>(['']);
  const [instructions, setInstructions] = useState('');
  const [servings, setServings] = useState<number | null>(null);
  const [prepTime, setPrepTime] = useState<number | null>(null);
  const [cookTime, setCookTime] = useState<number | null>(null);
  const [category, setCategory] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isPublic, setIsPublic] = useState(true);
  const [ocrImageUrl, setOcrImageUrl] = useState<string | null>(null);

  // Load OCR data if present
  useEffect(() => {
    const ocrJobId = searchParams.get('ocr');
    if (ocrJobId) {
      loadOCRData(ocrJobId);
    }
  }, [searchParams]);

  const loadOCRData = async (jobId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/ocr/jobs/${jobId}`);
      if (!response.ok) {
        throw new Error('Impossible de charger les données OCR');
      }
      
      const data = await response.json();
      
      // Store the OCR image URL for display
      if (data.image_url) {
        setOcrImageUrl(data.image_url);
        // Optionally set as recipe image if none is uploaded
        if (!imageUrl) {
          setImageUrl(data.image_url);
        }
      }
      
      if (data.extracted_text) {
        // Parse the extracted text and populate fields
        // This is a simple implementation - you may want to improve the parsing
        const text = data.extracted_text;
        
        // Try to extract title (first line)
        const lines = text.split('\n').filter((line: string) => line.trim());
        if (lines.length > 0) {
          setTitle(lines[0].trim());
        }
        
        // Put remaining text in instructions
        if (lines.length > 1) {
          setInstructions(lines.slice(1).join('\n'));
        }
      }
    } catch (err) {
      console.error('Error loading OCR data:', err);
      setError('Erreur lors du chargement des données OCR');
    } finally {
      setLoading(false);
    }
  };

  // Check authentication
  const canAddRecipe = user && (user.role === 'collaborator' || user.role === 'admin');

  if (!canAddRecipe) {
    return (
      <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '2rem', textAlign: 'center' }}>
        <h1 style={{ marginBottom: '1rem' }}>Accès restreint</h1>
        <p style={{ marginBottom: '2rem', color: '#666' }}>
          Vous devez être connecté en tant que collaborateur ou administrateur pour créer des recettes.
        </p>
        <Link href="/login" style={{ 
          display: 'inline-block', padding: '0.75rem 2rem', backgroundColor: '#8B5A3C', 
          color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: 'bold' 
        }}>
          Se connecter
        </Link>
      </div>
    );
  }

  const handleAddIngredient = () => {
    setIngredients([...ingredients, '']);
  };

  const handleRemoveIngredient = (index: number) => {
    const newIngredients = ingredients.filter((_, i) => i !== index);
    setIngredients(newIngredients.length > 0 ? newIngredients : ['']);
  };

  const handleIngredientChange = (index: number, value: string) => {
    const newIngredients = [...ingredients];
    newIngredients[index] = value;
    setIngredients(newIngredients);
  };

  const handleAddEquipment = () => {
    setEquipment([...equipment, '']);
  };

  const handleRemoveEquipment = (index: number) => {
    const newEquipment = equipment.filter((_, i) => i !== index);
    setEquipment(newEquipment.length > 0 ? newEquipment : ['']);
  };

  const handleEquipmentChange = (index: number, value: string) => {
    const newEquipment = [...equipment];
    newEquipment[index] = value;
    setEquipment(newEquipment);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const recipeData: Recipe = {
        title,
        description,
        ingredients: ingredients.filter(ing => ing.trim() !== ''),
        equipment: equipment.filter(eq => eq.trim() !== ''),
        instructions,
        servings,
        prep_time: prepTime,
        cook_time: cookTime,
        total_time: (prepTime || 0) + (cookTime || 0) || null,
        category,
        cuisine,
        image_url: imageUrl || null,
        is_public: isPublic,
      };

      console.log('Creating recipe:', recipeData);

      const response = await fetch('/api/v2/recipes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recipeData),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error creating recipe:', errorData);
        throw new Error(errorData.detail || 'Échec de la création de la recette');
      }

      const newRecipe = await response.json();
      console.log('Recipe created:', newRecipe);
      // Redirect to recipes list after creation
      router.push('/recipes');
    } catch (err) {
      console.error('Exception:', err);
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)', padding: '2rem' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ 
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
          marginBottom: '2rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.95)', 
          borderRadius: '12px', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)' 
        }}>
          <h1 style={{ margin: 0, color: '#5c3317', fontSize: '1.75rem' }}>Créer une Nouvelle Recette</h1>
          <button 
            onClick={() => router.back()} 
            style={{ 
              padding: '0.5rem 1.5rem', backgroundColor: '#6c757d', color: 'white', 
              border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold',
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#5a6268'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#6c757d'}
          >
            ← Retour
          </button>
        </div>

        {loading && (
          <div style={{ 
            padding: '1rem', marginBottom: '1.5rem', backgroundColor: '#d1ecf1', 
            color: '#0c5460', borderRadius: '8px', border: '1px solid #bee5eb',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' 
          }}>
            ⏳ Chargement des données OCR...
          </div>
        )}

        {error && (
          <div style={{ 
            padding: '1rem', marginBottom: '1.5rem', backgroundColor: '#f8d7da', 
            color: '#721c24', borderRadius: '8px', border: '1px solid #f5c6cb',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' 
          }}>
            ⚠️ {error}
          </div>
        )}

        {ocrImageUrl && (
          <div style={{ 
            marginBottom: '1.5rem', background: 'rgba(255, 255, 255, 0.95)', 
            padding: '1.5rem', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)' 
          }}>
            <h3 style={{ marginTop: 0, marginBottom: '1rem', color: '#5c3317', fontSize: '1.25rem' }}>
              📸 Image source de la recette
            </h3>
            <div style={{ 
              border: '2px solid #8B5A3C', borderRadius: '8px', overflow: 'hidden',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
            }}>
              <img 
                src={ocrImageUrl} 
                alt="Image OCR de la recette" 
                style={{ 
                  width: '100%', 
                  height: 'auto', 
                  display: 'block',
                  maxHeight: '500px',
                  objectFit: 'contain',
                  backgroundColor: '#f8f9fa'
                }}
              />
            </div>
            <p style={{ 
              marginTop: '0.75rem', marginBottom: 0, color: '#6c757d', 
              fontSize: '0.875rem', textAlign: 'center' 
            }}>
              Référez-vous à cette image pendant que vous complétez la recette
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ 
          background: 'rgba(255, 255, 255, 0.95)', padding: '2.5rem', 
          borderRadius: '12px', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)' 
        }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
              Titre *
            </label>
            <input 
              type="text" 
              value={title} 
              onChange={(e) => setTitle(e.target.value)} 
              required
              placeholder="Ex: Tarte aux pommes"
              style={{ 
                width: '100%', padding: '0.75rem', fontSize: '1rem', 
                border: '2px solid #ddd', borderRadius: '8px',
                transition: 'border-color 0.3s ease'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
              onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
              Description
            </label>
            <textarea 
              value={description} 
              onChange={(e) => setDescription(e.target.value)} 
              rows={3}
              placeholder="Décrivez votre recette..."
              style={{ 
                width: '100%', padding: '0.75rem', fontSize: '1rem', 
                border: '2px solid #ddd', borderRadius: '8px',
                transition: 'border-color 0.3s ease', resize: 'vertical'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
              onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 'bold', color: '#5c3317' }}>
              Ingrédients *
            </label>
            {ingredients.map((ingredient, index) => (
              <div key={index} style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <input 
                  type="text" 
                  value={ingredient} 
                  onChange={(e) => handleIngredientChange(index, e.target.value)}
                  placeholder="Ex: 2 tasses de farine"
                  style={{ 
                    flex: 1, padding: '0.75rem', fontSize: '1rem', 
                    border: '2px solid #ddd', borderRadius: '8px',
                    transition: 'border-color 0.3s ease'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
                  onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
                />
                {ingredients.length > 1 && (
                  <button 
                    type="button" 
                    onClick={() => handleRemoveIngredient(index)}
                    style={{ 
                      padding: '0.5rem 1rem', backgroundColor: '#dc3545', color: 'white', 
                      border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#c82333'}
                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#dc3545'}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button 
              type="button" 
              onClick={handleAddIngredient}
              style={{ 
                marginTop: '0.5rem', padding: '0.5rem 1.5rem', backgroundColor: '#28a745', 
                color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', 
                fontWeight: 'bold', transition: 'all 0.3s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#218838'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#28a745'}
            >
              + Ajouter un ingrédient
            </button>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 'bold', color: '#5c3317' }}>
              Équipement
            </label>
            {equipment.map((item, index) => (
              <div key={index} style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <input 
                  type="text" 
                  value={item} 
                  onChange={(e) => handleEquipmentChange(index, e.target.value)}
                  placeholder="Ex: Fouet, Casserole, Four"
                  style={{ 
                    flex: 1, padding: '0.75rem', fontSize: '1rem', 
                    border: '2px solid #ddd', borderRadius: '8px',
                    transition: 'border-color 0.3s ease'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
                  onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
                />
                {equipment.length > 1 && (
                  <button 
                    type="button" 
                    onClick={() => handleRemoveEquipment(index)}
                    style={{ 
                      padding: '0.5rem 1rem', backgroundColor: '#dc3545', color: 'white', 
                      border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#c82333'}
                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#dc3545'}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button 
              type="button" 
              onClick={handleAddEquipment}
              style={{ 
                marginTop: '0.5rem', padding: '0.5rem 1.5rem', backgroundColor: '#28a745', 
                color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', 
                fontWeight: 'bold', transition: 'all 0.3s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#218838'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#28a745'}
            >
              + Ajouter un équipement
            </button>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
              Instructions *
            </label>
            <textarea 
              value={instructions} 
              onChange={(e) => setInstructions(e.target.value)} 
              required 
              rows={8}
              placeholder="Étape 1: ...&#10;Étape 2: ..."
              style={{ 
                width: '100%', padding: '0.75rem', fontSize: '1rem', 
                border: '2px solid #ddd', borderRadius: '8px',
                transition: 'border-color 0.3s ease', resize: 'vertical'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
              onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
                Portions
              </label>
              <input 
                type="number" 
                value={servings || ''} 
                onChange={(e) => setServings(e.target.value ? parseInt(e.target.value) : null)} 
                min="1"
                placeholder="4"
                style={{ 
                  width: '100%', padding: '0.75rem', fontSize: '1rem', 
                  border: '2px solid #ddd', borderRadius: '8px',
                  transition: 'border-color 0.3s ease'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
                Préparation (min)
              </label>
              <input 
                type="number" 
                value={prepTime || ''} 
                onChange={(e) => setPrepTime(e.target.value ? parseInt(e.target.value) : null)} 
                min="0"
                placeholder="15"
                style={{ 
                  width: '100%', padding: '0.75rem', fontSize: '1rem', 
                  border: '2px solid #ddd', borderRadius: '8px',
                  transition: 'border-color 0.3s ease'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
                Cuisson (min)
              </label>
              <input 
                type="number" 
                value={cookTime || ''} 
                onChange={(e) => setCookTime(e.target.value ? parseInt(e.target.value) : null)} 
                min="0"
                placeholder="30"
                style={{ 
                  width: '100%', padding: '0.75rem', fontSize: '1rem', 
                  border: '2px solid #ddd', borderRadius: '8px',
                  transition: 'border-color 0.3s ease'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
                Catégorie
              </label>
              <input 
                type="text" 
                value={category} 
                onChange={(e) => setCategory(e.target.value)}
                placeholder="Ex: Dessert, Entrée, Plat principal"
                style={{ 
                  width: '100%', padding: '0.75rem', fontSize: '1rem', 
                  border: '2px solid #ddd', borderRadius: '8px',
                  transition: 'border-color 0.3s ease'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#5c3317' }}>
                Cuisine
              </label>
              <input 
                type="text" 
                value={cuisine} 
                onChange={(e) => setCuisine(e.target.value)}
                placeholder="Ex: Française, Italienne, Mexicaine"
                style={{ 
                  width: '100%', padding: '0.75rem', fontSize: '1rem', 
                  border: '2px solid #ddd', borderRadius: '8px',
                  transition: 'border-color 0.3s ease'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#8B5A3C'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
              />
            </div>
          </div>

          <ImageUpload
            currentImageUrl={imageUrl}
            onImageChange={(url, file) => {
              setImageUrl(url);
              setImageFile(file);
            }}
            label="Image de la recette"
          />

          <div style={{ marginBottom: '2rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={isPublic} 
                onChange={(e) => setIsPublic(e.target.checked)}
                style={{ width: '20px', height: '20px', cursor: 'pointer', accentColor: '#8B5A3C' }}
              />
              <span style={{ fontWeight: 'bold', color: '#5c3317' }}>Recette publique</span>
            </label>
            <p style={{ marginTop: '0.5rem', marginLeft: '1.75rem', fontSize: '0.875rem', color: '#666' }}>
              Les recettes publiques sont visibles par tous les utilisateurs
            </p>
          </div>

          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button 
              type="submit" 
              disabled={saving}
              style={{ 
                flex: 1, minWidth: '200px', padding: '1rem 2rem', fontSize: '1.125rem', 
                backgroundColor: saving ? '#6c757d' : '#28a745',
                color: 'white', border: 'none', borderRadius: '8px', 
                cursor: saving ? 'not-allowed' : 'pointer', fontWeight: 'bold',
                transition: 'all 0.3s ease', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
              }}
              onMouseOver={(e) => !saving && (e.currentTarget.style.backgroundColor = '#218838')}
              onMouseOut={(e) => !saving && (e.currentTarget.style.backgroundColor = '#28a745')}
            >
              {saving ? '⏳ Création...' : '✨ Créer la recette'}
            </button>
            <button 
              type="button"
              onClick={() => router.back()} 
              style={{ 
                flex: 1, minWidth: '200px', padding: '1rem 2rem', fontSize: '1.125rem', 
                backgroundColor: '#6c757d', color: 'white', 
                border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold',
                transition: 'all 0.3s ease', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#5a6268'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#6c757d'}
            >
              Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
