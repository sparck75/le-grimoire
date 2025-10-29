'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
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

export default function AdminRecipeNewPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v2/recipes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recipeData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create recipe');
      }

      const newRecipe = await response.json();
      router.push(`/admin/recipes/${newRecipe.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="admin-header">
        <h1>Créer une Nouvelle Recette</h1>
        <button 
          onClick={() => router.back()} 
          className="btn btn-secondary"
          style={{ padding: '0.5rem 1rem', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          ← Retour
        </button>
      </div>

      {error && (
        <div style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', border: '1px solid #f5c6cb' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Titre *</label>
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required
            style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Description</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3}
            style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Ingrédients *</label>
          {ingredients.map((ingredient, index) => (
            <div key={index} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <input type="text" value={ingredient} onChange={(e) => handleIngredientChange(index, e.target.value)}
                placeholder="Ex: 2 tasses de farine"
                style={{ flex: 1, padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
              {ingredients.length > 1 && (
                <button type="button" onClick={() => handleRemoveIngredient(index)}
                  style={{ padding: '0.5rem 1rem', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  ✕
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={handleAddIngredient}
            style={{ marginTop: '0.5rem', padding: '0.5rem 1rem', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            + Ajouter un ingrédient
          </button>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Équipement</label>
          {equipment.map((item, index) => (
            <div key={index} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <input type="text" value={item} onChange={(e) => handleEquipmentChange(index, e.target.value)}
                placeholder="Ex: Fouet, Casserole, Four"
                style={{ flex: 1, padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
              {equipment.length > 1 && (
                <button type="button" onClick={() => handleRemoveEquipment(index)}
                  style={{ padding: '0.5rem 1rem', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  ✕
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={handleAddEquipment}
            style={{ marginTop: '0.5rem', padding: '0.5rem 1rem', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            + Ajouter un équipement
          </button>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Instructions *</label>
          <textarea value={instructions} onChange={(e) => setInstructions(e.target.value)} required rows={8}
            placeholder="Étape 1: ...&#10;Étape 2: ..."
            style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Portions</label>
            <input type="number" value={servings || ''} onChange={(e) => setServings(e.target.value ? parseInt(e.target.value) : null)} min="1"
              style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Temps de préparation (min)</label>
            <input type="number" value={prepTime || ''} onChange={(e) => setPrepTime(e.target.value ? parseInt(e.target.value) : null)} min="0"
              style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Temps de cuisson (min)</label>
            <input type="number" value={cookTime || ''} onChange={(e) => setCookTime(e.target.value ? parseInt(e.target.value) : null)} min="0"
              style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Catégorie</label>
            <input type="text" value={category} onChange={(e) => setCategory(e.target.value)}
              placeholder="Ex: Dessert, Entrée, Plat principal"
              style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Cuisine</label>
            <input type="text" value={cuisine} onChange={(e) => setCuisine(e.target.value)}
              placeholder="Ex: Française, Italienne, Mexicaine"
              style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' }} />
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
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input type="checkbox" checked={isPublic} onChange={(e) => setIsPublic(e.target.checked)}
              style={{ width: '20px', height: '20px', cursor: 'pointer' }} />
            <span style={{ fontWeight: 'bold' }}>Recette publique</span>
          </label>
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button type="submit" disabled={saving}
            style={{ flex: 1, padding: '0.75rem 2rem', fontSize: '1rem', backgroundColor: saving ? '#6c757d' : '#28a745',
              color: 'white', border: 'none', borderRadius: '4px', cursor: saving ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}>
            {saving ? 'Création...' : '✨ Créer la recette'}
          </button>
          <button 
            type="button"
            onClick={() => router.back()} 
            className="btn btn-secondary" 
            style={{ padding: '0.75rem 2rem', fontSize: '1rem', backgroundColor: '#6c757d', color: 'white', 
              border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            Annuler
          </button>
        </div>
      </form>
    </div>
  );
}
