'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Ingredient {
  id: string;  // MongoDB _id
  off_id: string;  // OpenFoodFacts ID like "en:tomato"
  name: string;  // Display name
  english_name: string;
  french_name: string;
  names: { [key: string]: string };  // All language names
  is_vegan: boolean;
  is_vegetarian: boolean;
  categories: string[];
  parents: string[];
}

interface PaginatedResponse {
  items: Ingredient[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export default function AdminIngredientsPage() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 20;
  
  // Get API URL - use HTTPS in production
  const getApiUrl = () => {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!envUrl || envUrl.includes('localhost')) {
      // In browser, use current origin (will be https://legrimoireonline.ca)
      if (typeof window !== 'undefined') {
        return window.location.origin;
      }
      return 'https://legrimoireonline.ca'; // Default to HTTPS in production
    }
    return envUrl;
  };

  useEffect(() => {
    fetchIngredients();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search]);

  async function fetchIngredients() {
    try {
      setLoading(true);
      
      const apiUrl = getApiUrl();
      
      // Use MongoDB search endpoint if searching, otherwise list endpoint
      let url: string;
      if (search) {
        const params = new URLSearchParams({
          q: search,
          language: 'fr',  // or 'en' based on user preference
          page: page.toString(),
          limit: limit.toString(),
        });
        url = `${apiUrl}/api/admin/ingredients/search?${params}`;
      } else {
        const params = new URLSearchParams({
          page: page.toString(),
          limit: limit.toString(),
        });
        url = `${apiUrl}/api/admin/ingredients?${params}`;
      }

      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error('Failed to fetch ingredients');
      }

      const data: PaginatedResponse = await response.json();
      setIngredients(data.items);
      setTotalPages(data.pages);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(value: string) {
    setSearch(value);
    setPage(1); // Reset to first page on search
  }

  async function handleDelete(id: string, name: string) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer "${name}" ?`)) {
      return;
    }

    try {
      const apiUrl = getApiUrl();
      const response = await fetch(
        `${apiUrl}/api/admin/ingredients/ingredients/${id}`,
        { method: 'DELETE' }
      );

      if (!response.ok) {
        throw new Error('Échec de la suppression de l\'ingrédient');
      }

      // Refresh the list
      fetchIngredients();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Échec de la suppression de l\'ingrédient');
    }
  }

  return (
    <div>
      <div className="admin-header">
        <h1>Ingrédients</h1>
        <Link href="/admin/ingredients/new" className="btn btn-success">
          ➕ Ajouter un Ingrédient
        </Link>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="admin-card">
        <div className="card-header">
          <h2>Tous les Ingrédients ({total})</h2>
        </div>
        
        <div className="card-content">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Rechercher des ingrédients..."
              className="search-input"
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>

          {loading ? (
            <div className="loading">Chargement des ingrédients...</div>
          ) : (
            <>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Off ID</th>
                      <th>Nom (EN)</th>
                      <th>Nom (FR)</th>
                      <th>Végétalien</th>
                      <th>Végétarien</th>
                      <th>Catégories</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {!ingredients || ingredients.length === 0 ? (
                      <tr>
                        <td colSpan={7} style={{ textAlign: 'center', padding: '2rem' }}>
                          Aucun ingrédient trouvé
                        </td>
                      </tr>
                    ) : (
                      ingredients.map((ingredient) => (
                        <tr key={ingredient.id}>
                          <td>
                            <code style={{ fontSize: '0.85em', color: '#666' }}>
                              {ingredient.off_id}
                            </code>
                          </td>
                          <td style={{ fontWeight: 500 }}>{ingredient.english_name || ingredient.names?.en || '—'}</td>
                          <td>{ingredient.french_name || ingredient.names?.fr || '—'}</td>
                          <td style={{ textAlign: 'center' }}>
                            {ingredient.is_vegan ? '✅' : '—'}
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            {ingredient.is_vegetarian ? '✅' : '—'}
                          </td>
                          <td>
                            {ingredient.categories && ingredient.categories.length > 0 ? (
                              <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
                                {ingredient.categories.slice(0, 2).map((cat, idx) => (
                                  <span key={idx} className="badge" style={{ fontSize: '0.75rem' }}>
                                    {cat}
                                  </span>
                                ))}
                                {ingredient.categories.length > 2 && (
                                  <span style={{ color: '#999', fontSize: '0.85em' }}>
                                    +{ingredient.categories.length - 2}
                                  </span>
                                )}
                              </div>
                            ) : '—'}
                          </td>
                          <td>
                            <div className="table-actions">
                              <Link
                                href={`/admin/ingredients/${ingredient.off_id}`}
                                className="icon-btn"
                                title="Voir détails"
                              >
                                �️
                              </Link>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                  >
                    ← Précédent
                  </button>
                  <span>
                    Page {page} sur {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page === totalPages}
                  >
                    Suivant →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
