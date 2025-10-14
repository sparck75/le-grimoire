'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Category {
  id: string;
  name: string;
  name_en?: string;
  name_fr?: string;
  parent_category_id: string | null;
  icon?: string;
}

interface IngredientFormData {
  english_name: string;
  french_name: string;
  gender: string;
  category_id: string;
  subcategory: string;
  aliases: string[];
  notes: string;
}

export default function NewIngredientPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<IngredientFormData>({
    english_name: '',
    french_name: '',
    gender: 'm',
    category_id: '',
    subcategory: '',
    aliases: [],
    notes: '',
  });
  
  const [aliasInput, setAliasInput] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('http://localhost:8000/api/admin/ingredients/categories');
        const categoriesData = await response.json();
        setCategories(categoriesData);
      } catch (err) {
        setError('Failed to load categories');
      }
    }

    fetchData();
  }, []);

  function handleAddAlias() {
    if (aliasInput.trim() && !formData.aliases.includes(aliasInput.trim())) {
      setFormData({
        ...formData,
        aliases: [...formData.aliases, aliasInput.trim()],
      });
      setAliasInput('');
    }
  }

  function handleRemoveAlias(alias: string) {
    setFormData({
      ...formData,
      aliases: formData.aliases.filter((a) => a !== alias),
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        'http://localhost:8000/api/admin/ingredients/ingredients',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create ingredient');
      }

      // Redirect to ingredients list
      router.push('/admin/ingredients');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="admin-header">
        <h1>Ajouter un Nouvel Ingrédient</h1>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="admin-card">
        <form onSubmit={handleSubmit}>
          <div className="card-content">
            <div style={{ display: 'grid', gap: '1.5rem', maxWidth: '600px' }}>
              {/* English Name */}
              <div>
                <label htmlFor="english_name" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Nom Anglais *
                </label>
                <input
                  id="english_name"
                  type="text"
                  required
                  className="search-input"
                  style={{ width: '100%' }}
                  value={formData.english_name}
                  onChange={(e) => setFormData({ ...formData, english_name: e.target.value })}
                />
              </div>

              {/* French Name */}
              <div>
                <label htmlFor="french_name" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Nom Français *
                </label>
                <input
                  id="french_name"
                  type="text"
                  required
                  className="search-input"
                  style={{ width: '100%' }}
                  value={formData.french_name}
                  onChange={(e) => setFormData({ ...formData, french_name: e.target.value })}
                />
              </div>

              {/* Gender */}
              <div>
                <label htmlFor="gender" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Genre (Grammatical) *
                </label>
                <select
                  id="gender"
                  required
                  className="search-input"
                  style={{ width: '100%' }}
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                >
                  <option value="m">Masculin (m)</option>
                  <option value="f">Féminin (f)</option>
                </select>
              </div>

              {/* Category */}
              <div>
                <label htmlFor="category" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Catégorie *
                </label>
                <select
                  id="category"
                  required
                  className="search-input"
                  style={{ width: '100%' }}
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                >
                  <option value="">Sélectionner une catégorie</option>
                  {categories.filter(cat => cat.name_en).map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name_fr || cat.name} ({cat.name_en})
                    </option>
                  ))}
                </select>
              </div>

              {/* Subcategory */}
              <div>
                <label htmlFor="subcategory" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Sous-catégorie
                </label>
                <input
                  id="subcategory"
                  type="text"
                  className="search-input"
                  style={{ width: '100%' }}
                  placeholder="Ex: Flour, Cereal, Tuber..."
                  value={formData.subcategory}
                  onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })}
                />
              </div>

              {/* Aliases */}
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Alias (Noms Alternatifs)
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <input
                    type="text"
                    className="search-input"
                    style={{ flex: 1 }}
                    placeholder="Ajouter un alias (séparés par des virgules)"
                    value={aliasInput}
                    onChange={(e) => setAliasInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddAlias();
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleAddAlias}
                  >
                    Ajouter
                  </button>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {formData.aliases.map((alias) => (
                    <span
                      key={alias}
                      className="badge badge-active"
                      style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                      onClick={() => handleRemoveAlias(alias)}
                    >
                      {alias} ✕
                    </span>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <label htmlFor="notes" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Notes
                </label>
                <textarea
                  id="notes"
                  className="search-input"
                  style={{ width: '100%', minHeight: '80px', fontFamily: 'inherit' }}
                  placeholder="Informations additionnelles sur l'ingrédient..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </div>

              {/* Active Status - Removed since it's always true for new ingredients */}
              <div style={{ display: 'none' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  <span>Actif</span>
                </label>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div
            style={{
              borderTop: '1px solid #ecf0f1',
              padding: '1.5rem',
              display: 'flex',
              gap: '1rem',
              justifyContent: 'flex-end',
            }}
          >
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => router.push('/admin/ingredients')}
            >
              Annuler
            </button>
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Création...' : 'Créer l\'Ingrédient'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
