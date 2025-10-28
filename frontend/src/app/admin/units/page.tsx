'use client';

import { useEffect, useState } from 'react';

interface Unit {
  id: string;
  symbol: string;
  name: string;
  unit_type: string;
  conversion_to_base: number | null;
  base_unit: string | null;
}

export default function UnitsPage() {
  // Use HTTPS in production if NEXT_PUBLIC_API_URL is not set or is localhost
  const getApiUrl = () => {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!envUrl || envUrl.includes('localhost')) {
      // In browser, use current origin (will be https://legrimoireonline.ca)
      if (typeof window !== 'undefined') {
        return window.location.origin;
      }
      return 'http://localhost:8000';
    }
    return envUrl;
  };
  const apiUrl = getApiUrl();
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUnits();
  }, []);

  async function fetchUnits() {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/admin/ingredients/units`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch units');
      }

      const data = await response.json();
      setUnits(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }

  // Group units by type
  const groupedUnits = units.reduce((acc, unit) => {
    if (!acc[unit.unit_type]) {
      acc[unit.unit_type] = [];
    }
    acc[unit.unit_type].push(unit);
    return acc;
  }, {} as Record<string, Unit[]>);

  return (
    <div>
      <div className="admin-header">
        <h1>Unités de Mesure</h1>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="admin-card">
        <div className="card-header">
          <h2>Toutes les Unités ({units.length})</h2>
        </div>
        
        <div className="card-content">
          {loading ? (
            <div className="loading">Chargement des unités...</div>
          ) : (
            <div style={{ display: 'grid', gap: '2rem' }}>
              {Object.entries(groupedUnits).map(([type, typeUnits]) => (
                <div key={type}>
                  <h3 style={{ marginBottom: '1rem', color: '#2c3e50', textTransform: 'capitalize' }}>
                    {type}
                  </h3>
                  <div className="table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Symbole</th>
                          <th>Nom</th>
                          <th>Unité de Base</th>
                          <th>Facteur de Conversion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {typeUnits.map((unit) => (
                          <tr key={unit.id}>
                            <td style={{ fontWeight: 600 }}>{unit.symbol}</td>
                            <td>{unit.name}</td>
                            <td>{unit.base_unit || '—'}</td>
                            <td>
                              {unit.conversion_to_base
                                ? `× ${unit.conversion_to_base}`
                                : '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
