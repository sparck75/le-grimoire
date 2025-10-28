'use client';
// Cache buster: 2025-10-25-v2

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface Stats {
  totalIngredients: number;
  totalCategories: number;
  totalRecipes: number;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  
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

  // Check if user is admin
  const isAdmin = user && user.role === 'admin';

  useEffect(() => {
    if (!isAdmin && !loading) {
      router.push('/');
    }
  }, [isAdmin, loading, router]);

  useEffect(() => {
    async function fetchStats() {
      try {
        // Use client-side API calls directly to backend
        const apiUrl = getApiUrl();
        
        // Fetch stats from various endpoints
        const [statsRes, recipesRes] = await Promise.all([
          fetch(`${apiUrl}/api/admin/ingredients/stats/summary`),
          fetch(`${apiUrl}/api/v2/recipes`),
        ]);

        if (!statsRes.ok || !recipesRes.ok) {
          throw new Error('Failed to fetch stats');
        }

        const statsData = await statsRes.json();
        const recipes = await recipesRes.json();

        setStats({
          totalIngredients: statsData.ingredients?.total || 0,
          totalCategories: statsData.categories?.total || 0,
          totalRecipes: recipes.length || 0,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div>
        <div className="admin-header">
          <h1>Tableau de Bord</h1>
        </div>
        <div className="loading">Chargement des statistiques...</div>
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
          <p style={{ fontSize: '1.25rem', color: '#721c24', marginBottom: '2rem' }}>
            🔒 Cette page est réservée aux administrateurs uniquement.
          </p>
          <Link href="/" className="btn btn-primary">
            Retour à l&apos;accueil
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="admin-header">
        <h1>Tableau de Bord</h1>
      </div>

      <div className="admin-stats">
        <div className="stat-card">
          <h3>Total Ingrédients</h3>
          <div className="stat-value">{stats?.totalIngredients || 0}</div>
          <Link href="/admin/ingredients" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Gérer les Ingrédients
          </Link>
        </div>

        <div className="stat-card">
          <h3>Total Catégories</h3>
          <div className="stat-value">{stats?.totalCategories || 0}</div>
          <Link href="/admin/categories" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Gérer les Catégories
          </Link>
        </div>

        <div className="stat-card">
          <h3>Total Recettes</h3>
          <div className="stat-value">{stats?.totalRecipes || 0}</div>
          <Link href="/admin/recipes" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Gérer les Recettes
          </Link>
        </div>

        <div className="stat-card">
          <h3>👥 Utilisateurs</h3>
          <div className="stat-value">🔐</div>
          <Link href="/admin/users" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Gérer les Utilisateurs
          </Link>
        </div>
      </div>

      <div className="admin-card">
        <div className="card-header">
          <h2>Actions Rapides</h2>
        </div>
        <div className="card-content">
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <Link href="/admin/ingredients/new" className="btn btn-success">
              ➕ Ajouter un Ingrédient
            </Link>
            <Link href="/admin/recipes/new" className="btn btn-success">
              ➕ Ajouter une Recette
            </Link>
            <Link href="/admin/categories/new" className="btn btn-success">
              ➕ Ajouter une Catégorie
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
