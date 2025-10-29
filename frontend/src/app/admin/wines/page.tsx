'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface Wine {
  id: string;
  name: string;
  producer?: string;
  vintage?: number;
  wine_type: string;
  region: string;
  country: string;
  barcode?: string;
  data_source: string;
  created_at: string;
}

interface Stats {
  total: number;
  by_type: Record<string, number>;
  with_barcode: number;
}

export default function AdminWinesPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [wines, setWines] = useState<Wine[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');

  const isAdmin = user && user.role === 'admin';

  useEffect(() => {
    if (!isAdmin && !loading) {
      router.push('/admin');
    }
  }, [isAdmin, loading, router]);

  useEffect(() => {
    if (isAdmin) {
      fetchData();
    }
  }, [isAdmin]);

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

  async function fetchData() {
    try {
      const apiUrl = getApiUrl();
      const token = localStorage.getItem('access_token');
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const [winesRes, statsRes] = await Promise.all([
        fetch(`${apiUrl}/api/admin/wines?limit=100`, { headers }),
        fetch(`${apiUrl}/api/admin/stats/summary`, { headers })
      ]);

      if (winesRes.ok) {
        const winesData = await winesRes.json();
        setWines(winesData);
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading wines');
    } finally {
      setLoading(false);
    }
  }

  async function deleteWine(id: string) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce vin de la base de données maître?')) {
      return;
    }

    try {
      const apiUrl = getApiUrl();
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${apiUrl}/api/admin/wines/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setWines(wines.filter(w => w.id !== id));
        if (stats) {
          setStats({ ...stats, total: stats.total - 1 });
        }
      } else {
        alert('Erreur lors de la suppression du vin');
      }
    } catch (err) {
      alert('Erreur lors de la suppression du vin');
    }
  }

  const filteredWines = wines.filter(wine => {
    const matchesSearch = wine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         wine.producer?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         wine.barcode?.includes(searchTerm);
    const matchesType = filterType === 'all' || wine.wine_type === filterType;
    return matchesSearch && matchesType;
  });

  if (loading) {
    return (
      <div>
        <div className="admin-header">
          <h1>Gestion des Vins</h1>
        </div>
        <div className="loading">Chargement...</div>
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return (
    <div>
      <div className="admin-header">
        <h1>🍷 Base de Données des Vins</h1>
        <Link href="/admin/wines/new" className="btn btn-success">
          ➕ Ajouter un Vin
        </Link>
      </div>

      {stats && (
        <div className="admin-stats">
          <div className="stat-card">
            <h3>Total Vins</h3>
            <div className="stat-value">{stats.total}</div>
          </div>
          <div className="stat-card">
            <h3>Avec Code-Barres</h3>
            <div className="stat-value">{stats.with_barcode}</div>
          </div>
          {Object.entries(stats.by_type).map(([type, count]) => (
            <div key={type} className="stat-card">
              <h3 style={{ textTransform: 'capitalize' }}>{type}</h3>
              <div className="stat-value">{count}</div>
            </div>
          ))}
        </div>
      )}

      <div className="admin-card">
        <div className="card-header">
          <h2>Filtres</h2>
        </div>
        <div className="card-content">
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <input
              type="text"
              placeholder="Rechercher par nom, producteur ou code-barres..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                flex: 1,
                minWidth: '250px',
                padding: '0.75rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px'
              }}
            />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              style={{
                padding: '0.75rem',
                border: '2px solid #e0e0e0',
                borderRadius: '8px'
              }}
            >
              <option value="all">Tous les types</option>
              <option value="red">Rouge</option>
              <option value="white">Blanc</option>
              <option value="rosé">Rosé</option>
              <option value="sparkling">Mousseux</option>
              <option value="dessert">Dessert</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div style={{
          background: '#fee',
          color: '#c33',
          padding: '1rem',
          borderRadius: '8px',
          margin: '1rem 0'
        }}>
          {error}
        </div>
      )}

      <div className="admin-card">
        <div className="card-header">
          <h2>Vins dans la Base de Données ({filteredWines.length})</h2>
        </div>
        <div className="card-content">
          {filteredWines.length === 0 ? (
            <p style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
              Aucun vin trouvé. <Link href="/admin/wines/new">Ajoutez-en un!</Link>
            </p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Nom</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Producteur</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Millésime</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Type</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Région</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Code-Barres</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Source</th>
                  <th style={{ padding: '0.75rem', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredWines.map((wine) => (
                  <tr key={wine.id} style={{ borderBottom: '1px solid #e0e0e0' }}>
                    <td style={{ padding: '0.75rem' }}>{wine.name}</td>
                    <td style={{ padding: '0.75rem' }}>{wine.producer || '-'}</td>
                    <td style={{ padding: '0.75rem' }}>{wine.vintage || 'NV'}</td>
                    <td style={{ padding: '0.75rem' }}>
                      <span style={{
                        background: '#8b4513',
                        color: 'white',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.85rem'
                      }}>
                        {wine.wine_type}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem' }}>{wine.region || '-'}</td>
                    <td style={{ padding: '0.75rem', fontFamily: 'monospace', fontSize: '0.9rem' }}>
                      {wine.barcode || '-'}
                    </td>
                    <td style={{ padding: '0.75rem' }}>
                      <span style={{
                        background: '#f0f0f0',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.85rem'
                      }}>
                        {wine.data_source}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                      <Link
                        href={`/admin/wines/${wine.id}`}
                        className="btn btn-sm btn-primary"
                        style={{ marginRight: '0.5rem' }}
                      >
                        Modifier
                      </Link>
                      <button
                        onClick={() => deleteWine(wine.id)}
                        className="btn btn-sm btn-danger"
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
