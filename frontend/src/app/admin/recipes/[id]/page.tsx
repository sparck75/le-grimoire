'use client';

import { useEffect, useState, useRef, memo } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

interface RecipeIngredient {
  ingredient_off_id: string;  // MongoDB off_id like "en:tomato"
  ingredient_name: string;
  quantity: number | null;
  unit: string | null;
  preparation_notes?: string;  // Full original text like "12 tomates vertes hachées"
}

interface Recipe {
  id?: string;
  title: string;
  description: string;
  ingredients: RecipeIngredient[];
  instructions: string;
  servings: number | null;
  prep_time: number | null;
  cook_time: number | null;
  total_time: number | null;
  category: string;
  cuisine: string;
  difficulty: string;
  image_url: string;
  is_public: boolean;
}

interface Ingredient {
  id: string;  // MongoDB _id
  off_id: string;  // OpenFoodFacts ID
  name: string;  // Display name
  english_name: string;
  french_name: string;
}

// Ingredient Search Component with autocomplete (memoized to prevent unnecessary re-renders)
const IngredientSearch = memo(function IngredientSearch({ value, ingredientName, preparationNotes, onChange, onTextChange, triggerSearch }: {
  value: string;
  ingredientName: string;
  preparationNotes?: string;
  onChange: (offId: string, name: string) => void;
  onTextChange?: (text: string) => void;
  triggerSearch?: boolean;
}) {
  // Initialize with preparation_notes if no ingredient is linked, otherwise show the linked ingredient name
  const initialSearchTerm = ingredientName || preparationNotes || '';
  const [searchTerm, setSearchTerm] = useState(initialSearchTerm);
  const [searchResults, setSearchResults] = useState<Ingredient[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // DEBUG: Track component lifecycle
  useEffect(() => {
    console.log('🔵 IngredientSearch MOUNTED for:', value || 'new');
    return () => console.log('🔴 IngredientSearch UNMOUNTED for:', value || 'new');
  }, []);
  
  // DEBUG: Track showDropdown changes
  useEffect(() => {
    console.log('🟢 showDropdown changed to:', showDropdown, 'searchResults:', searchResults.length);
  }, [showDropdown]);

  // Update search term only when ingredient value/name changes (not preparation_notes)
  useEffect(() => {
    // Only update if the linked ingredient changed (value changed)
    if (ingredientName) {
      console.log('🔗 Ingredient linked, updating searchTerm to:', ingredientName);
      setSearchTerm(ingredientName);
      console.log('❌ Setting showDropdown = FALSE (ingredient name changed in effect)');
      setShowDropdown(false); // Close dropdown when ingredient is selected
    }
  }, [ingredientName, value]);

  // Track if user is actively typing
  const [userIsTyping, setUserIsTyping] = useState(false);
  const [shouldSearch, setShouldSearch] = useState(false);

  useEffect(() => {
    const delayDebounce = setTimeout(async () => {
      // Search if user is typing OR if shouldSearch is true (for focus events)
      if (searchTerm.length >= 2 && (userIsTyping || shouldSearch)) {
        setIsSearching(true);
        try {
          const response = await fetch(`/api/v2/ingredients/?search=${encodeURIComponent(searchTerm)}&language=fr&limit=20`);
          if (response.ok) {
            const data = await response.json();
            console.log('🔍 Ingredient search results for "' + searchTerm + '":', data?.length || 0, 'results');
            setSearchResults(data || []);
            if (data && data.length > 0) {
              console.log('✅ Setting showDropdown = TRUE (from search results)');
              setShowDropdown(true);
            } else {
              console.log('❌ Setting showDropdown = FALSE (no results)');
              setShowDropdown(false);
            }
          }
        } catch (error) {
          console.error('Error searching ingredients:', error);
        } finally {
          setIsSearching(false);
          setShouldSearch(false); // Reset after search
        }
      } else if (searchTerm.length < 2) {
        setSearchResults([]);
        console.log('❌ Setting showDropdown = FALSE (search term < 2)');
        setShowDropdown(false);
      }
    }, 150); // Reduced from 300ms to 150ms for faster response

    return () => clearTimeout(delayDebounce);
  }, [searchTerm, userIsTyping, shouldSearch]);

  const selectIngredient = (ingredient: Ingredient) => {
    // Link to selected ingredient
    onChange(ingredient.off_id, ingredient.name);
    setSearchTerm(ingredient.name); // Show the selected ingredient name
    console.log('❌ Setting showDropdown = FALSE (ingredient selected)');
    setShowDropdown(false);
    setUserIsTyping(false);
  };

  // Simple dropdown style - use absolute positioning relative to parent
  const dropdownStyle = {
    position: 'absolute' as const,
    top: '100%',  // Position right below the input
    left: '0',
    right: '0',
    marginTop: '4px',
    maxHeight: '250px',
    overflowY: 'auto' as const,
    backgroundColor: 'white',
    border: '2px solid #667eea',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    zIndex: 1000
  };

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <input
        ref={inputRef}
        type="text"
        value={searchTerm}
        onChange={(e) => {
          setUserIsTyping(true);
          setSearchTerm(e.target.value);
        }}
        onFocus={() => {
          console.log('🎯 onFocus triggered - searchTerm:', searchTerm, 'results:', searchResults.length);
          // Trigger search on focus if there's text but no results yet
          if (searchTerm.length >= 2 && searchResults.length === 0) {
            console.log('🔄 Triggering search from focus');
            setShouldSearch(true);
          }
          // Show dropdown if there are already results
          if (searchResults.length > 0 && searchTerm.length >= 2) {
            console.log('✅ Setting showDropdown = TRUE (from focus)');
            setShowDropdown(true);
          }
        }}
        onBlur={(e) => {
          console.log('👋 onBlur triggered');
          // Don't close if user is interacting with the dropdown
          // The dropdown will handle closing itself when an item is selected
          const relatedTarget = e.relatedTarget as HTMLElement;
          if (relatedTarget && relatedTarget.closest('[data-dropdown]')) {
            console.log('⏸️ Not closing - clicking within dropdown');
            return; // Don't close if clicking within dropdown
          }
          // Close dropdown after a short delay (to allow clicking on items)
          setTimeout(() => {
            console.log('❌ Setting showDropdown = FALSE (from blur timeout)');
            setShowDropdown(false);
            setUserIsTyping(false);
          }, 300); // Increased from 200ms to 300ms
        }}
        placeholder="Rechercher pour lier à un ingrédient..."
        style={{ width: '100%', paddingRight: searchTerm ? '35px' : '10px' }}
      />
      {searchTerm && !isSearching && (
        <button
          type="button"
          onMouseDown={(e) => {
            e.preventDefault(); // Prevent input blur
            console.log('🗑️ Clear button clicked');
            setSearchTerm('');
            onChange('', ''); // Clear the ingredient link
            setSearchResults([]);
            console.log('❌ Setting showDropdown = FALSE (clear button)');
            setShowDropdown(false);
            setUserIsTyping(false);
          }}
          style={{
            position: 'absolute',
            right: '8px',
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'none',
            border: 'none',
            color: '#999',
            cursor: 'pointer',
            fontSize: '1.2rem',
            padding: '0 4px',
            lineHeight: '1',
            transition: 'color 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#ff4444'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#999'}
          title="Effacer"
        >
          ×
        </button>
      )}
      {isSearching && (
        <span style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)' }}>
          🔄
        </span>
      )}
      {showDropdown && searchResults.length > 0 ? (
        <div style={dropdownStyle} data-dropdown="true">
          {console.log('🎨 Rendering dropdown with', searchResults.length, 'results')}
          {searchResults.map((ing) => (
            <div
              key={ing.id}
              onMouseDown={(e) => {
                e.preventDefault(); // Prevent input blur
                selectIngredient(ing);
              }}
              style={{
                padding: '10px 15px',
                cursor: 'pointer',
                borderBottom: '1px solid #eee',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
            >
              <div style={{ fontWeight: '500' }}>{ing.name}</div>
              <div style={{ fontSize: '0.85em', color: '#666' }}>{ing.off_id}</div>
            </div>
          ))}
        </div>
      ) : (
        searchTerm.length >= 2 && !isSearching && console.log('Dropdown NOT showing - showDropdown:', showDropdown, 'results:', searchResults.length)
      )}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if value or ingredientName changes
  // Ignore preparationNotes changes to prevent re-rendering while typing
  return prevProps.value === nextProps.value && 
         prevProps.ingredientName === nextProps.ingredientName;
});

export default function AdminRecipeEditPage() {
  const params = useParams();
  const router = useRouter();
  const isNew = params.id === 'new';
  
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [triggerSearchIndex, setTriggerSearchIndex] = useState<number | null>(null);
  
  const [recipe, setRecipe] = useState<Recipe>({
    title: '',
    description: '',
    ingredients: [],
    instructions: '',
    servings: null,
    prep_time: null,
    cook_time: null,
    total_time: null,
    category: '',
    cuisine: '',
    difficulty: 'Facile',
    image_url: '',
    is_public: true,
  });

  useEffect(() => {
    fetchIngredients();
    if (!isNew) {
      fetchRecipe();
    }
  }, []);

  useEffect(() => {
    // Auto-calculate total time
    const prep = recipe.prep_time || 0;
    const cook = recipe.cook_time || 0;
    const total = prep + cook;
    if (total > 0 && total !== recipe.total_time) {
      setRecipe(prev => ({ ...prev, total_time: total }));
    }
  }, [recipe.prep_time, recipe.cook_time]);

  async function fetchIngredients() {
    try {
      // Fetch from MongoDB endpoint (v2 public API for reading ingredients)
      const response = await fetch('/api/v2/ingredients/?language=fr&limit=1000');
      if (response.ok) {
        const data = await response.json();
        setIngredients(data || []);
      }
    } catch (err) {
      console.error('Error fetching ingredients:', err);
    }
  }

  async function fetchRecipe() {
    try {
      setLoading(true);
      const response = await fetch(`/api/admin/recipes/${params.id}`);
      
      if (!response.ok) {
        throw new Error('Recette non trouvée');
      }
      
      const data = await response.json();
      setRecipe(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    if (!recipe.title.trim()) {
      alert('Le titre est requis');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const url = isNew 
        ? '/api/admin/recipes'
        : `/api/admin/recipes/${params.id}`;
      
      const method = isNew ? 'POST' : 'PUT';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recipe),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la sauvegarde');
      }

      router.push('/admin/recipes');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  }

  function addIngredient() {
    setRecipe(prev => ({
      ...prev,
      ingredients: [
        ...prev.ingredients,
        { ingredient_off_id: '', ingredient_name: '', quantity: null, unit: null }
      ]
    }));
  }

  function removeIngredient(index: number) {
    setRecipe(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index)
    }));
  }

  function updateIngredient(index: number, field: keyof RecipeIngredient, value: any) {
    setRecipe(prev => ({
      ...prev,
      ingredients: prev.ingredients.map((ing, i) => {
        if (i === index) {
          const updated = { ...ing, [field]: value };
          
          // If changing ingredient_off_id, also update ingredient_name
          if (field === 'ingredient_off_id') {
            const selectedIngredient = ingredients.find(item => item.off_id === value);
            if (selectedIngredient) {
              updated.ingredient_name = selectedIngredient.name;
            }
          }
          
          return updated;
        }
        return ing;
      })
    }));
  }

  if (loading) {
    return (
      <div>
        <div className="admin-header">
          <h1>Chargement...</h1>
        </div>
        <div className="loading">Chargement de la recette...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="admin-header">
        <h1>{isNew ? '➕ Nouvelle Recette' : '✏️ Modifier la Recette'}</h1>
        <Link href="/admin/recipes" className="btn btn-secondary">
          ← Retour
        </Link>
      </div>

      {error && (
        <div style={{
          padding: '1rem',
          marginBottom: '1rem',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '12px',
          color: '#c00'
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="admin-card">
          <div className="card-header">
            <h2>Informations de base</h2>
          </div>
          <div className="card-content">
            <div className="form-grid">
              <div className="form-group full-width">
                <label>Titre *</label>
                <input
                  type="text"
                  value={recipe.title}
                  onChange={(e) => setRecipe({ ...recipe, title: e.target.value })}
                  required
                  placeholder="Ex: Poulet rôti aux herbes"
                />
              </div>

              <div className="form-group full-width">
                <label>Description</label>
                <textarea
                  value={recipe.description}
                  onChange={(e) => setRecipe({ ...recipe, description: e.target.value })}
                  rows={3}
                  placeholder="Décrivez brièvement cette recette..."
                />
              </div>

              <div className="form-group">
                <label>Catégorie</label>
                <select
                  value={recipe.category}
                  onChange={(e) => setRecipe({ ...recipe, category: e.target.value })}
                >
                  <option value="">Sélectionner...</option>
                  <option value="Entrée">Entrée</option>
                  <option value="Plat principal">Plat principal</option>
                  <option value="Accompagnement">Accompagnement</option>
                  <option value="Dessert">Dessert</option>
                  <option value="Boisson">Boisson</option>
                  <option value="Soupe">Soupe</option>
                  <option value="Salade">Salade</option>
                </select>
              </div>

              <div className="form-group">
                <label>Cuisine</label>
                <select
                  value={recipe.cuisine}
                  onChange={(e) => setRecipe({ ...recipe, cuisine: e.target.value })}
                >
                  <option value="">Sélectionner...</option>
                  <option value="Française">Française</option>
                  <option value="Italienne">Italienne</option>
                  <option value="Asiatique">Asiatique</option>
                  <option value="Mexicaine">Mexicaine</option>
                  <option value="Indienne">Indienne</option>
                  <option value="Méditerranéenne">Méditerranéenne</option>
                  <option value="Américaine">Américaine</option>
                  <option value="Autre">Autre</option>
                </select>
              </div>

              <div className="form-group">
                <label>Difficulté</label>
                <select
                  value={recipe.difficulty}
                  onChange={(e) => setRecipe({ ...recipe, difficulty: e.target.value })}
                >
                  <option value="Facile">Facile</option>
                  <option value="Moyenne">Moyenne</option>
                  <option value="Difficile">Difficile</option>
                </select>
              </div>

              <div className="form-group">
                <label>Portions</label>
                <input
                  type="number"
                  min="1"
                  value={recipe.servings || ''}
                  onChange={(e) => setRecipe({ ...recipe, servings: e.target.value ? parseInt(e.target.value) : null })}
                  placeholder="Ex: 4"
                />
              </div>

              <div className="form-group">
                <label>Temps de préparation (min)</label>
                <input
                  type="number"
                  min="0"
                  value={recipe.prep_time || ''}
                  onChange={(e) => setRecipe({ ...recipe, prep_time: e.target.value ? parseInt(e.target.value) : null })}
                  placeholder="Ex: 15"
                />
              </div>

              <div className="form-group">
                <label>Temps de cuisson (min)</label>
                <input
                  type="number"
                  min="0"
                  value={recipe.cook_time || ''}
                  onChange={(e) => setRecipe({ ...recipe, cook_time: e.target.value ? parseInt(e.target.value) : null })}
                  placeholder="Ex: 30"
                />
              </div>

              <div className="form-group">
                <label>Temps total (min)</label>
                <input
                  type="number"
                  min="0"
                  value={recipe.total_time || ''}
                  onChange={(e) => setRecipe({ ...recipe, total_time: e.target.value ? parseInt(e.target.value) : null })}
                  placeholder="Auto-calculé"
                  readOnly
                  style={{ backgroundColor: '#f5f5f5' }}
                />
              </div>

              <div className="form-group full-width">
                <label>URL de l'image</label>
                <input
                  type="url"
                  value={recipe.image_url}
                  onChange={(e) => setRecipe({ ...recipe, image_url: e.target.value })}
                  placeholder="https://example.com/image.jpg"
                />
              </div>

              <div className="form-group full-width">
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input
                    type="checkbox"
                    checked={recipe.is_public}
                    onChange={(e) => setRecipe({ ...recipe, is_public: e.target.checked })}
                    style={{ width: 'auto', margin: 0 }}
                  />
                  <span>Publier la recette (visible sur le site public)</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Ingredients Section */}
        <div className="admin-card" style={{ marginTop: '2rem' }}>
          <div className="card-header">
            <h2>Ingrédients</h2>
            <button
              type="button"
              onClick={addIngredient}
              className="btn btn-success"
            >
              ➕ Ajouter un ingrédient
            </button>
          </div>
          <div className="card-content">
            {recipe.ingredients.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#999', padding: '2rem' }}>
                Aucun ingrédient ajouté. Cliquez sur "Ajouter un ingrédient" pour commencer.
              </p>
            ) : (
              <div className="ingredients-list">
                {recipe.ingredients.map((ingredient, index) => (
                  <div key={index} className="ingredient-row">
                    <div style={{ flex: '1', minWidth: '250px' }}>
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', fontWeight: '500', color: '#555' }}>
                        Texte de l'ingrédient
                      </label>
                      <input
                        type="text"
                        value={ingredient.preparation_notes || ''}
                        onChange={(e) => updateIngredient(index, 'preparation_notes', e.target.value)}
                        placeholder="Ex: 12 tomates vertes hachées"
                        style={{ width: '100%', marginBottom: '0.5rem' }}
                      />
                      
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', fontWeight: '500', color: '#555' }}>
                        Lier à l'ingrédient
                      </label>
                      <IngredientSearch
                        value={ingredient.ingredient_off_id}
                        ingredientName={ingredient.ingredient_name}
                        preparationNotes={ingredient.preparation_notes}
                        onChange={(offId, name) => {
                          updateIngredient(index, 'ingredient_off_id', offId);
                          updateIngredient(index, 'ingredient_name', name);
                          setTriggerSearchIndex(null);
                        }}
                        onTextChange={() => {}}
                        triggerSearch={triggerSearchIndex === index}
                      />
                      {ingredient.ingredient_name && (
                        <small style={{ display: 'block', marginTop: '0.25rem', color: '#4CAF50', fontSize: '0.8rem', fontStyle: 'italic' }}>
                          ✓ Lié à: {ingredient.ingredient_name}
                        </small>
                      )}
                    </div>
                    
                    <div style={{ width: '90px' }}>
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', fontWeight: '500', color: '#555' }}>
                        Quantité
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={ingredient.quantity || ''}
                        onChange={(e) => updateIngredient(index, 'quantity', e.target.value ? parseFloat(e.target.value) : null)}
                        placeholder="Ex: 2"
                        style={{ width: '100%' }}
                      />
                    </div>
                    
                    <div style={{ width: '110px' }}>
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', fontWeight: '500', color: '#555' }}>
                        Unité
                      </label>
                      <input
                        type="text"
                        value={ingredient.unit || ''}
                        onChange={(e) => updateIngredient(index, 'unit', e.target.value)}
                        placeholder="Ex: cup, g"
                        style={{ width: '100%' }}
                      />
                    </div>
                    
                    <div style={{ alignSelf: 'flex-end' }}>
                      <button
                        type="button"
                        onClick={() => removeIngredient(index)}
                        className="btn btn-danger"
                        style={{ padding: '0.5rem 1rem', flexShrink: 0 }}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Instructions Section */}
        <div className="admin-card" style={{ marginTop: '2rem' }}>
          <div className="card-header">
            <h2>Instructions</h2>
          </div>
          <div className="card-content">
            <div className="form-group full-width">
              <textarea
                value={recipe.instructions}
                onChange={(e) => setRecipe({ ...recipe, instructions: e.target.value })}
                rows={10}
                placeholder="Décrivez les étapes de préparation..."
                style={{ fontFamily: 'inherit' }}
              />
              <small style={{ color: '#666', marginTop: '0.5rem', display: 'block' }}>
                Écrivez chaque étape sur une nouvelle ligne pour une meilleure lisibilité.
              </small>
            </div>
          </div>
        </div>

        {/* Submit Buttons */}
        <div style={{ 
          marginTop: '2rem', 
          display: 'flex', 
          gap: '1rem', 
          justifyContent: 'flex-end',
          paddingBottom: '2rem'
        }}>
          <Link href="/admin/recipes" className="btn btn-secondary">
            Annuler
          </Link>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={saving}
          >
            {saving ? 'Enregistrement...' : (isNew ? '✓ Créer la recette' : '✓ Enregistrer les modifications')}
          </button>
        </div>
      </form>

      <style jsx>{`
        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.5rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group.full-width {
          grid-column: 1 / -1;
        }

        .form-group label {
          font-weight: 600;
          color: #333;
          font-size: 0.95rem;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
          padding: 0.75rem;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          font-size: 1rem;
          transition: all 0.3s ease;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .ingredients-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .ingredient-row {
          display: flex;
          gap: 1rem;
          align-items: center;
          padding: 1rem;
          background: rgba(102, 126, 234, 0.05);
          border-radius: 12px;
          border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .ingredient-row select {
          flex: 1;
          padding: 0.75rem;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          font-size: 1rem;
        }

        .ingredient-row input {
          padding: 0.75rem;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          font-size: 1rem;
        }

        @media (max-width: 768px) {
          .form-grid {
            grid-template-columns: 1fr;
          }
          
          .ingredient-row {
            flex-wrap: wrap;
          }
          
          .ingredient-row select,
          .ingredient-row input {
            width: 100% !important;
          }
        }
      `}</style>
    </div>
  );
}
