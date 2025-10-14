'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Category {
  off_id: string;  // MongoDB OpenFoodFacts ID
  name: string;
  english_name: string;
  french_name: string;
  icon?: string;
  parent_count: number;
  children_count: number;
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topLevelOnly, setTopLevelOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'children_count' | 'name'>('children_count');
  const [limit, setLimit] = useState(100);

  useEffect(() => {
    fetchCategories();
  }, [topLevelOnly, sortBy, limit]);

  async function fetchCategories() {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        top_level_only: topLevelOnly.toString(),
        sort_by: sortBy,
        limit: limit.toString()
      });
      
      const response = await fetch(`http://localhost:8000/api/admin/ingredients/categories?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch categories');
      }

      const data = await response.json();
      setCategories(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="admin-header">
        <h1>Catégories d'Ingrédients (MongoDB)</h1>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="admin-card">
        <div className="card-header">
          <h2>Catégories OpenFoodFacts ({categories.length})</h2>
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={topLevelOnly}
                onChange={(e) => setTopLevelOnly(e.target.checked)}
              />
              <span>Top-level only (Root categories)</span>
            </label>
            
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'children_count' | 'name')}
                style={{ padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
              >
                <option value="children_count">Most subcategories</option>
                <option value="name">Name (A-Z)</option>
              </select>
            </label>
            
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>Show:</span>
              <select
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value))}
                style={{ padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
              >
                <option value="50">50 categories</option>
                <option value="100">100 categories</option>
                <option value="200">200 categories</option>
                <option value="500">500 categories</option>
              </select>
            </label>
          </div>
        </div>
        
        <div className="card-content">
          {loading ? (
            <div className="loading">Chargement des catégories...</div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Off ID</th>
                    <th>Nom (EN)</th>
                    <th>Nom (FR)</th>
                    <th>Icône</th>
                    <th>Parents</th>
                    <th>Sous-catégories</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.length === 0 ? (
                    <tr>
                      <td colSpan={7} style={{ textAlign: 'center', padding: '2rem' }}>
                        Aucune catégorie trouvée
                      </td>
                    </tr>
                  ) : (
                    categories.map((category) => (
                      <tr key={category.off_id}>
                        <td>
                          <code style={{ fontSize: '0.85em', color: '#666' }}>
                            {category.off_id}
                          </code>
                        </td>
                        <td style={{ fontWeight: 500 }}>{category.english_name}</td>
                        <td>{category.french_name}</td>
                        <td style={{ fontSize: '1.5em', textAlign: 'center' }}>
                          {category.icon || '📦'}
                        </td>
                        <td style={{ textAlign: 'center' }}>
                          {category.parent_count}
                        </td>
                        <td style={{ textAlign: 'center' }}>
                          {category.children_count}
                        </td>
                        <td>
                          <div className="table-actions">
                            <Link
                              href={`/admin/categories/${category.off_id}`}
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
          )}
        </div>
      </div>
    </div>
  );
}
