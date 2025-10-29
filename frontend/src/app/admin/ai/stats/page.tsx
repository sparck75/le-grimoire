'use client';

import { useEffect, useState, useMemo } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ExtractionStats {
  period: {
    days: number;
    start_date: string;
    end_date: string;
  };
  summary: {
    total_extractions: number;
    successful: number;
    failed: number;
    success_rate: number;
    average_confidence: number;
    average_processing_time_ms: number;
  };
  by_provider: {
    [key: string]: {
      count: number;
      successful: number;
      failed: number;
      total_tokens: number;
      total_cost_usd: number;
    };
  };
  by_method: {
    [key: string]: number;
  };
  tokens: {
    total: number;
    prompt: number;
    completion: number;
    ai_extractions: number;
  };
  costs: {
    total_usd: number;
    average_per_extraction_usd: number;
    by_provider: {
      [key: string]: number;
    };
  };
  daily_breakdown: Array<{
    date: string;
    total: number;
    successful: number;
    failed: number;
    cost_usd: number;
  }>;
}

interface ExtractionLog {
  id: string;
  extraction_method: string;
  provider: string | null;
  model_name: string | null;
  recipe_title: string | null;
  recipe_id: string | null;
  confidence_score: number | null;
  success: boolean;
  error_message: string | null;
  total_tokens: number | null;
  estimated_cost_usd: number | null;
  processing_time_ms: number | null;
  image_url: string | null;
  created_at: string;
}

export default function AIStatsPage() {
  const { user } = useAuth();
  const router = useRouter();
  
  const [stats, setStats] = useState<ExtractionStats | null>(null);
  const [logs, setLogs] = useState<ExtractionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const [logsLimit, setLogsLimit] = useState(50);
  const [logsProvider, setLogsProvider] = useState<string>('');
  const [logsSuccess, setLogsSuccess] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(60); // seconds
  const [customDateRange, setCustomDateRange] = useState<{start: string; end: string} | null>(null);

  const isAdmin = user && user.role === 'admin';

  // Chart colors
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  // Filter logs based on search query
  const filteredLogs = useMemo(() => {
    if (!searchQuery) return logs;
    const query = searchQuery.toLowerCase();
    return logs.filter(log => 
      log.recipe_title?.toLowerCase().includes(query) ||
      log.extraction_method.toLowerCase().includes(query) ||
      log.provider?.toLowerCase().includes(query)
    );
  }, [logs, searchQuery]);

  // Calculate cost projections
  const costProjections = useMemo(() => {
    if (!stats || stats.summary.total_extractions === 0) return null;
    
    const daysInPeriod = stats.period.days;
    const dailyAverage = stats.costs.total_usd / daysInPeriod;
    const monthlyProjection = dailyAverage * 30;
    const yearlyProjection = dailyAverage * 365;
    
    return {
      daily: dailyAverage,
      monthly: monthlyProjection,
      yearly: yearlyProjection,
      perExtraction: stats.costs.average_per_extraction_usd,
    };
  }, [stats]);

  // Export functions
  const exportToCSV = (data: any[], filename: string) => {
    if (data.length === 0) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value;
        }).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const exportToJSON = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleExportStats = () => {
    if (!stats) return;
    exportToJSON(stats, 'ai_stats');
  };

  const handleExportLogs = () => {
    if (filteredLogs.length === 0) return;
    exportToCSV(filteredLogs.map(log => ({
      date: new Date(log.created_at).toISOString(),
      recipe_title: log.recipe_title || 'Sans titre',
      method: log.extraction_method,
      provider: log.provider || '',
      model: log.model_name || '',
      confidence: log.confidence_score !== null ? (log.confidence_score * 100).toFixed(1) + '%' : '',
      tokens: log.total_tokens || '',
      cost: log.estimated_cost_usd !== null ? log.estimated_cost_usd.toFixed(4) : '',
      time_ms: log.processing_time_ms || '',
      success: log.success ? 'Oui' : 'Non',
      error: log.error_message || '',
    })), 'ai_extraction_logs');
  };

  useEffect(() => {
    if (!isAdmin && !loading) {
      router.push('/');
    }
  }, [isAdmin, loading, router]);

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

  useEffect(() => {
    async function fetchData() {
      try {
        const apiUrl = getApiUrl();
        
        // Fetch stats
        const statsUrl = `${apiUrl}/api/admin/ai/stats?days=${days}`;
        const statsRes = await fetch(statsUrl);
        if (statsRes.ok) {
          setStats(await statsRes.json());
        }

        // Fetch logs
        let logsUrl = `${apiUrl}/api/admin/ai/logs?limit=${logsLimit}`;
        if (logsProvider) logsUrl += `&provider=${logsProvider}`;
        if (logsSuccess) logsUrl += `&success_only=${logsSuccess}`;
        
        const logsRes = await fetch(logsUrl);
        if (logsRes.ok) {
          setLogs(await logsRes.json());
        }

        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setLoading(false);
      }
    }

    fetchData();
  }, [days, logsLimit, logsProvider, logsSuccess]);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(async () => {
      try {
        const apiUrl = getApiUrl();
        
        const statsUrl = `${apiUrl}/api/admin/ai/stats?days=${days}`;
        const statsRes = await fetch(statsUrl);
        if (statsRes.ok) {
          setStats(await statsRes.json());
        }

        let logsUrl = `${apiUrl}/api/admin/ai/logs?limit=${logsLimit}`;
        if (logsProvider) logsUrl += `&provider=${logsProvider}`;
        if (logsSuccess) logsUrl += `&success_only=${logsSuccess}`;
        
        const logsRes = await fetch(logsUrl);
        if (logsRes.ok) {
          setLogs(await logsRes.json());
        }
      } catch (err) {
        console.error('Auto-refresh failed:', err);
      }
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, days, logsLimit, logsProvider, logsSuccess]);

  if (!isAdmin) {
    return null;
  }

  if (loading) {
    return (
      <>
        <style jsx global>{`
          .admin-main {
            background: linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%) !important;
            padding: 0 !important;
            margin-left: 280px !important;
          }
        `}</style>
        <div style={{ minHeight: '100vh', padding: '2rem' }}>
          <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ animation: 'spin 1s linear infinite', borderRadius: '50%', height: '3rem', width: '3rem', border: '2px solid #D4A373', borderTopColor: 'transparent', margin: '0 auto 1rem' }}></div>
                <p style={{ color: '#F5E6D3' }}>Chargement des statistiques...</p>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <style jsx global>{`
        .admin-main {
          background: linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%) !important;
          padding: 0 !important;
          margin-left: 280px !important;
        }
        .stat-card-hover:hover {
          transform: translateY(-5px);
          box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3) !important;
          background: rgba(255, 255, 255, 1) !important;
        }
        tbody tr:hover {
          background: rgba(102, 126, 234, 0.05) !important;
          transform: scale(1.005);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }
        .desktop-table {
          display: block;
        }
        .mobile-cards {
          display: none;
        }
        @media (max-width: 768px) {
          .desktop-table {
            display: none;
          }
          .mobile-cards {
            display: flex;
          }
        }
      `}</style>
      <div style={{ minHeight: '100vh', padding: '2rem' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ backgroundColor: 'rgba(212, 163, 115, 0.9)', borderRadius: '16px', padding: '2rem', marginBottom: '2rem', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
              <Link
                href="/admin/ai"
                style={{ color: '#2C1810', textDecoration: 'none', fontSize: '1rem', fontWeight: '600' }}
              >
                ← Retour à la gestion IA
              </Link>
              <Link
                href="/admin"
                style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', color: '#5C4033', padding: '0.75rem 1.5rem', borderRadius: '8px', textDecoration: 'none', fontSize: '0.875rem', fontWeight: '500', border: '2px solid #D4A373' }}
              >
                ← Retour au Tableau de Bord
              </Link>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
              <div>
                <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2C1810', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>📊</span> Statistiques d&apos;extraction IA
                </h1>
                <p style={{ color: '#5C4033', fontSize: '1rem' }}>
                  Suivi détaillé de l&apos;utilisation et des coûts
                </p>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {/* Auto-refresh toggle */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(255, 255, 255, 0.9)', padding: '0.5rem 1rem', borderRadius: '8px', border: '2px solid #D4A373' }}>
                  <input
                    type="checkbox"
                    id="autoRefresh"
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                    style={{ cursor: 'pointer' }}
                  />
                  <label htmlFor="autoRefresh" style={{ fontSize: '0.875rem', color: '#5C4033', cursor: 'pointer', fontWeight: '500' }}>
                    Auto-refresh
                  </label>
                  {autoRefresh && (
                    <select
                      value={refreshInterval}
                      onChange={(e) => setRefreshInterval(Number(e.target.value))}
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid #D4A373', backgroundColor: 'white' }}
                    >
                      <option value={30}>30s</option>
                      <option value={60}>1min</option>
                      <option value={300}>5min</option>
                    </select>
                  )}
                </div>
                {/* Export buttons */}
                <button
                  onClick={handleExportStats}
                  disabled={!stats}
                  style={{ padding: '0.5rem 1rem', backgroundColor: '#5C4033', color: 'white', fontSize: '0.875rem', borderRadius: '8px', border: 'none', cursor: stats ? 'pointer' : 'not-allowed', opacity: stats ? 1 : 0.5, fontWeight: '500' }}
                >
                  📊 Exporter Stats (JSON)
                </button>
                <button
                  onClick={handleExportLogs}
                  disabled={filteredLogs.length === 0}
                  style={{ padding: '0.5rem 1rem', backgroundColor: '#8B7355', color: 'white', fontSize: '0.875rem', borderRadius: '8px', border: 'none', cursor: filteredLogs.length > 0 ? 'pointer' : 'not-allowed', opacity: filteredLogs.length > 0 ? 1 : 0.5, fontWeight: '500' }}
                >
                  📥 Exporter Logs (CSV)
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#f8d7da', border: '2px solid #f5c6cb', borderRadius: '12px', color: '#721c24' }}>
            <strong>Erreur:</strong> {error}
          </div>
        )}

        {/* Empty State */}
        {!stats || stats.summary.total_extractions === 0 ? (
          <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', padding: '3rem 2rem', textAlign: 'center' }}>
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📊</div>
              <h2 style={{ fontSize: '1.875rem', fontWeight: '700', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '1rem', display: 'inline-block' }}>
                Aucune extraction IA pour le moment
              </h2>
              <p style={{ color: '#5C4033', marginBottom: '2rem', fontSize: '1.125rem' }}>
                Les statistiques d&apos;extraction IA apparaîtront ici une fois que vous aurez commencé à utiliser la fonctionnalité d&apos;extraction automatique de recettes.
              </p>
              <div style={{ backgroundColor: '#E8D5C4', border: '2px solid #D4A373', borderRadius: '12px', padding: '1.5rem', textAlign: 'left', marginBottom: '2rem' }}>
                <h3 style={{ fontWeight: '600', color: '#2C1810', marginBottom: '1rem', fontSize: '1.125rem' }}>🚀 Pour commencer:</h3>
                <ol style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  <li style={{ marginBottom: '0.75rem', color: '#5C4033' }}>1. Allez dans <Link href="/admin/ai" style={{ textDecoration: 'underline', fontWeight: '500', color: '#5C4033' }}>Gestion IA</Link></li>
                  <li style={{ marginBottom: '0.75rem', color: '#5C4033' }}>2. Configurez votre clé API OpenAI</li>
                  <li style={{ marginBottom: '0.75rem', color: '#5C4033' }}>3. Utilisez l&apos;onglet &quot;Extraction de Recette&quot; pour extraire du contenu d&apos;une image</li>
                  <li style={{ color: '#5C4033' }}>4. Les statistiques et les coûts apparaîtront automatiquement ici</li>
                </ol>
              </div>
              <div>
                <Link
                  href="/admin/ai"
                  style={{ display: 'inline-block', padding: '0.875rem 2rem', backgroundColor: '#5C4033', color: 'white', borderRadius: '12px', textDecoration: 'none', fontWeight: '500', fontSize: '1.125rem', border: '2px solid #5C4033' }}
                >
                  Aller à la Gestion IA
                </Link>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* Period Selector */}
            <div style={{ marginBottom: '1.5rem', backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#2C1810', marginBottom: '0.75rem' }}>
                Période d&apos;analyse
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <select
                  value={days}
                  onChange={(e) => setDays(Number(e.target.value))}
                  style={{ padding: '0.75rem 1rem', border: '2px solid #D4A373', borderRadius: '8px', backgroundColor: 'white', fontSize: '0.875rem', color: '#2C1810', cursor: 'pointer' }}
                >
                  <option value={7}>7 derniers jours</option>
                  <option value={30}>30 derniers jours</option>
                  <option value={90}>90 derniers jours</option>
                  <option value={365}>1 an</option>
                </select>
                <div style={{ fontSize: '0.875rem', color: '#5C4033' }}>
                  Du {new Date(stats.period.start_date).toLocaleDateString('fr-FR')} au {new Date(stats.period.end_date).toLocaleDateString('fr-FR')}
                </div>
              </div>
            </div>

            {/* Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
              <div className="stat-card-hover" style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '2rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', transition: 'all 0.3s ease' }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#8B5A3C', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Total Extractions
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2C1810' }}>
                  {stats.summary.total_extractions}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#5C4033', marginTop: '0.5rem' }}>
                  {stats.summary.successful} réussies · {stats.summary.failed} échouées
                </div>
                <div style={{ marginTop: '0.75rem', width: '100%', backgroundColor: '#E8D5C4', borderRadius: '9999px', height: '0.5rem' }}>
                  <div
                    style={{ backgroundColor: '#28a745', height: '0.5rem', borderRadius: '9999px', width: `${stats.summary.success_rate}%` }}
                  ></div>
                </div>
              </div>

              <div className="stat-card-hover" style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '2rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', transition: 'all 0.3s ease' }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#8B5A3C', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Taux de réussite
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
                  {stats.summary.success_rate.toFixed(1)}%
                </div>
                <div style={{ fontSize: '0.875rem', color: '#5C4033', marginTop: '0.5rem' }}>
                  Confiance: {(stats.summary.average_confidence * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '0.75rem', color: '#8B7355', marginTop: '0.25rem' }}>
                  Temps moy: {(stats.summary.average_processing_time_ms / 1000).toFixed(1)}s
                </div>
              </div>

              <div className="stat-card-hover" style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '2rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', transition: 'all 0.3s ease' }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#8B5A3C', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Coût Total
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2C1810' }}>
                  ${stats.costs.total_usd.toFixed(2)}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#5C4033', marginTop: '0.5rem' }}>
                  ${stats.costs.average_per_extraction_usd.toFixed(4)} / extraction
                </div>
                {costProjections && (
                  <div style={{ fontSize: '0.75rem', color: '#ff6b00', marginTop: '0.25rem', fontWeight: '500' }}>
                    📈 ~${costProjections.monthly.toFixed(2)}/mois
                  </div>
                )}
              </div>

              <div className="stat-card-hover" style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '2rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', transition: 'all 0.3s ease' }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#8B5A3C', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Tokens utilisés
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#6f42c1' }}>
                  {(stats.tokens.total / 1000).toFixed(1)}K
                </div>
                <div style={{ fontSize: '0.875rem', color: '#5C4033', marginTop: '0.5rem' }}>
                  {stats.tokens.ai_extractions} extractions IA
                </div>
                <div style={{ fontSize: '0.75rem', color: '#8B7355', marginTop: '0.25rem' }}>
                  Prompt: {(stats.tokens.prompt / 1000).toFixed(1)}K · Complétion: {(stats.tokens.completion / 1000).toFixed(1)}K
                </div>
              </div>
            </div>

            {/* Cost Projections Alert */}
            {costProjections && costProjections.monthly > 10 && (
              <div style={{ marginBottom: '1.5rem', padding: '1.5rem', backgroundColor: '#fff3cd', border: '2px solid #ffc107', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                  <span style={{ fontSize: '2rem' }}>⚠️</span>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontWeight: '600', color: '#856404', marginBottom: '0.5rem', fontSize: '1.125rem' }}>Projection des coûts</h3>
                    <p style={{ fontSize: '0.875rem', color: '#856404', marginBottom: '0.75rem' }}>
                      Basé sur votre utilisation actuelle, vos coûts mensuels sont estimés à <strong>${costProjections.monthly.toFixed(2)}</strong>.
                    </p>
                    <div style={{ fontSize: '0.75rem', color: '#856404' }}>
                      <div style={{ marginBottom: '0.25rem' }}>• Coût quotidien moyen: ${costProjections.daily.toFixed(2)}</div>
                      <div style={{ marginBottom: '0.25rem' }}>• Projection annuelle: ${costProjections.yearly.toFixed(2)}</div>
                      <div>• Coût par extraction: ${costProjections.perExtraction.toFixed(4)}</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Charts Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
              {/* Provider Distribution Pie Chart */}
              <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '700', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '1rem' }}>
                  Distribution par fournisseur
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={Object.entries(stats.by_provider).map(([name, data]) => ({
                        name: name.charAt(0).toUpperCase() + name.slice(1),
                        value: data.count,
                        cost: data.total_cost_usd,
                      }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry: any) => `${entry.name}: ${(entry.percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {Object.keys(stats.by_provider).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any, name: any, props: any) => [
                      `${value} extractions (${props.payload.cost ? '$' + props.payload.cost.toFixed(2) : 'N/A'})`,
                      props.payload.name
                    ]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Success Rate Bar Chart */}
              <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '700', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '1rem' }}>
                  Taux de réussite par fournisseur
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={Object.entries(stats.by_provider).map(([name, data]) => ({
                      name: name.charAt(0).toUpperCase() + name.slice(1),
                      Réussis: data.successful,
                      Échoués: data.failed,
                      rate: ((data.successful / data.count) * 100).toFixed(1),
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Réussis" stackId="a" fill="#10B981" />
                    <Bar dataKey="Échoués" stackId="a" fill="#EF4444" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* By Provider Cards */}
            <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '700', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '1rem' }}>
                Détails par fournisseur
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                {Object.entries(stats.by_provider).map(([provider, data]) => (
                  <div key={provider} style={{ backgroundColor: 'rgba(232, 213, 196, 0.5)', border: '2px solid #D4A373', borderRadius: '12px', padding: '1.25rem', transition: 'all 0.3s ease' }} className="stat-card-hover">
                    <div style={{ fontWeight: '700', color: '#2C1810', marginBottom: '1rem', textTransform: 'capitalize', fontSize: '1.25rem', borderBottom: '2px solid #D4A373', paddingBottom: '0.5rem' }}>
                      {provider}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: '#5C4033', fontWeight: '500' }}>Total:</span>
                        <span style={{ fontWeight: '600', color: '#2C1810', fontSize: '1rem' }}>{data.count}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: '#5C4033', fontWeight: '500' }}>Réussis:</span>
                        <span style={{ fontWeight: '600', color: '#16a34a' }}>{data.successful}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: '#5C4033', fontWeight: '500' }}>Échoués:</span>
                        <span style={{ fontWeight: '600', color: '#dc2626' }}>{data.failed}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px solid rgba(212, 163, 115, 0.3)' }}>
                        <span style={{ color: '#5C4033', fontWeight: '600' }}>Taux:</span>
                        <span style={{ fontWeight: '700', color: '#8B5A3C', fontSize: '1rem' }}>
                          {((data.successful / data.count) * 100).toFixed(1)}%
                        </span>
                      </div>
                      {data.total_tokens > 0 && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ color: '#5C4033', fontWeight: '500' }}>Tokens:</span>
                          <span style={{ fontWeight: '600', color: '#2C1810' }}>{(data.total_tokens / 1000).toFixed(1)}K</span>
                        </div>
                      )}
                      {data.total_cost_usd > 0 && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '2px solid #D4A373', paddingTop: '0.75rem', marginTop: '0.5rem' }}>
                          <span style={{ color: '#5C4033', fontWeight: '700' }}>Coût:</span>
                          <span style={{ fontWeight: '700', color: '#8B5A3C', fontSize: '1.125rem' }}>${data.total_cost_usd.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Daily Trend Line Chart */}
            <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '700', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '1rem' }}>
                Tendance quotidienne (7 derniers jours)
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart
                  data={stats.daily_breakdown.map(day => ({
                    date: new Date(day.date).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }),
                    Total: day.total,
                    Réussis: day.successful,
                    Échoués: day.failed,
                    'Coût ($)': parseFloat(day.cost_usd.toFixed(2)),
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="Total" stroke="#6B7280" strokeWidth={2} />
                  <Line yAxisId="left" type="monotone" dataKey="Réussis" stroke="#10B981" strokeWidth={2} />
                  <Line yAxisId="left" type="monotone" dataKey="Échoués" stroke="#EF4444" strokeWidth={2} />
                  <Line yAxisId="right" type="monotone" dataKey="Coût ($)" stroke="#3B82F6" strokeWidth={2} strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>

              {/* Table for mobile/detailed view */}
              <div className="mt-6 overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                      <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Réussis
                      </th>
                      <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Échoués
                      </th>
                      <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Coût
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stats.daily_breakdown.map((day) => (
                      <tr key={day.date} className="hover:bg-gray-50">
                        <td className="px-3 md:px-6 py-2 md:py-4 whitespace-nowrap text-gray-900">
                          {new Date(day.date).toLocaleDateString('fr-FR')}
                        </td>
                        <td className="px-3 md:px-6 py-2 md:py-4 whitespace-nowrap text-gray-900 font-medium">
                          {day.total}
                        </td>
                        <td className="px-3 md:px-6 py-2 md:py-4 whitespace-nowrap text-green-600 font-medium">
                          {day.successful}
                        </td>
                        <td className="px-3 md:px-6 py-2 md:py-4 whitespace-nowrap text-red-600 font-medium">
                          {day.failed}
                        </td>
                        <td className="px-3 md:px-6 py-2 md:py-4 whitespace-nowrap text-blue-600 font-medium">
                          ${day.cost_usd.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Recent Extractions */}
        <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '700', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                Extractions récentes
              </h2>
              <div style={{ fontSize: '0.875rem', color: '#5C4033' }}>
                {filteredLogs.length} {filteredLogs.length !== logs.length && `sur ${logs.length}`} résultat{filteredLogs.length > 1 ? 's' : ''}
              </div>
            </div>
            
            {/* Search and Filters */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {/* Search Box */}
              <div style={{ flex: 1 }}>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="🔍 Rechercher par recette, méthode, fournisseur..."
                  style={{ width: '100%', padding: '0.75rem 1rem', border: '2px solid #D4A373', borderRadius: '8px', fontSize: '0.875rem', backgroundColor: 'white' }}
                />
              </div>
              
              {/* Filters */}
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <select
                  value={logsProvider}
                  onChange={(e) => setLogsProvider(e.target.value)}
                  style={{ padding: '0.5rem 0.75rem', border: '2px solid #D4A373', borderRadius: '8px', fontSize: '0.875rem', backgroundColor: 'white' }}
                >
                  <option value="">Tous les fournisseurs</option>
                  <option value="openai">OpenAI</option>
                  <option value="tesseract">Tesseract</option>
                </select>
                <select
                  value={logsSuccess}
                  onChange={(e) => setLogsSuccess(e.target.value)}
                  style={{ padding: '0.5rem 0.75rem', border: '2px solid #D4A373', borderRadius: '8px', fontSize: '0.875rem', backgroundColor: 'white' }}
                >
                  <option value="">Tous</option>
                  <option value="true">Réussis</option>
                  <option value="false">Échoués</option>
                </select>
                <select
                  value={logsLimit}
                  onChange={(e) => setLogsLimit(Number(e.target.value))}
                  style={{ padding: '0.5rem 0.75rem', border: '2px solid #D4A373', borderRadius: '8px', fontSize: '0.875rem', backgroundColor: 'white' }}
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
          </div>

          {/* Desktop Table View */}
          <div className="desktop-table" style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
              <thead>
                <tr>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Date
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Recette
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Méthode
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Confiance
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Tokens
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Coût
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Temps
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'white', textTransform: 'uppercase', letterSpacing: '1px', background: 'linear-gradient(135deg, #8B5A3C 0%, #A67C52 100%)' }}>
                    Statut
                  </th>
                </tr>
              </thead>
              <tbody style={{ backgroundColor: 'white' }}>
                {filteredLogs.map((log) => (
                  <tr key={log.id} style={{ backgroundColor: log.success ? 'white' : '#fee2e2', borderBottom: '1px solid rgba(102, 126, 234, 0.1)', transition: 'all 0.2s ease' }}>
                    <td style={{ padding: '1rem', whiteSpace: 'nowrap', color: '#2C1810' }}>
                      {new Date(log.created_at).toLocaleString('fr-FR', { 
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td style={{ padding: '1rem', color: '#2C1810', maxWidth: '300px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.recipe_title || 'Sans titre'}</span>
                        {log.recipe_id && (
                          <Link 
                            href={`/recipes/${log.recipe_id}`}
                            style={{ color: '#8B5A3C', textDecoration: 'none', flexShrink: 0, fontWeight: '600' }}
                            title="Voir la recette"
                          >
                            →
                          </Link>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '1rem', whiteSpace: 'nowrap' }}>
                      <span style={{ textTransform: 'capitalize', fontWeight: '500', color: '#2C1810' }}>
                        {log.provider || log.extraction_method}
                      </span>
                      {log.model_name && (
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>{log.model_name}</div>
                      )}
                    </td>
                    <td style={{ padding: '1rem', whiteSpace: 'nowrap', color: '#2C1810' }}>
                      {log.confidence_score !== null 
                        ? <span style={{ fontWeight: '500', color: log.confidence_score > 0.8 ? '#16a34a' : log.confidence_score > 0.6 ? '#ca8a04' : '#ea580c' }}>
                            {(log.confidence_score * 100).toFixed(0)}%
                          </span>
                        : '-'}
                    </td>
                    <td style={{ padding: '1rem', whiteSpace: 'nowrap', color: '#2C1810' }}>
                      {log.total_tokens ? log.total_tokens.toLocaleString() : '-'}
                    </td>
                    <td style={{ padding: '1rem', whiteSpace: 'nowrap', color: '#8B5A3C', fontWeight: '500' }}>
                      {log.estimated_cost_usd !== null
                        ? `$${log.estimated_cost_usd.toFixed(4)}`
                        : '-'}
                    </td>
                    <td style={{ padding: '1rem', whiteSpace: 'nowrap', color: '#2C1810' }}>
                      {log.processing_time_ms !== null
                        ? `${(log.processing_time_ms / 1000).toFixed(1)}s`
                        : '-'}
                    </td>
                    <td style={{ padding: '1rem', whiteSpace: 'nowrap' }}>
                      {log.success ? (
                        <span style={{ padding: '0.25rem 0.75rem', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: '500' }}>
                          ✓ Réussi
                        </span>
                      ) : (
                        <span 
                          style={{ padding: '0.25rem 0.75rem', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: '500', cursor: 'help' }}
                          title={log.error_message || 'Erreur'}
                        >
                          ✗ Échec
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card View */}
          <div className="mobile-cards" style={{ flexDirection: 'column', gap: '1rem' }}>
            {filteredLogs.map((log) => (
              <div 
                key={log.id} 
                style={{ border: log.success ? '2px solid #D4A373' : '2px solid #fecaca', borderRadius: '12px', padding: '1rem', backgroundColor: log.success ? 'white' : '#fef2f2' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '500', color: '#2C1810', marginBottom: '0.25rem' }}>
                      {log.recipe_title || 'Sans titre'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                      {new Date(log.created_at).toLocaleString('fr-FR')}
                    </div>
                  </div>
                  {log.success ? (
                    <span style={{ padding: '0.25rem 0.5rem', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: '500' }}>
                      ✓
                    </span>
                  ) : (
                    <span style={{ padding: '0.25rem 0.5rem', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: '500' }}>
                      ✗
                    </span>
                  )}
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.875rem' }}>
                  <div>
                    <span style={{ color: '#6b7280' }}>Méthode:</span>
                    <div style={{ fontWeight: '500', textTransform: 'capitalize', color: '#2C1810' }}>{log.provider || log.extraction_method}</div>
                  </div>
                  {log.confidence_score !== null && (
                    <div>
                      <span style={{ color: '#6b7280' }}>Confiance:</span>
                      <div style={{ fontWeight: '500', color: '#2C1810' }}>{(log.confidence_score * 100).toFixed(0)}%</div>
                    </div>
                  )}
                  {log.total_tokens !== null && (
                    <div>
                      <span style={{ color: '#6b7280' }}>Tokens:</span>
                      <div style={{ fontWeight: '500', color: '#2C1810' }}>{log.total_tokens.toLocaleString()}</div>
                    </div>
                  )}
                  {log.estimated_cost_usd !== null && (
                    <div>
                      <span style={{ color: '#6b7280' }}>Coût:</span>
                      <div style={{ fontWeight: '500', color: '#8B5A3C' }}>${log.estimated_cost_usd.toFixed(4)}</div>
                    </div>
                  )}
                  {log.processing_time_ms !== null && (
                    <div>
                      <span style={{ color: '#6b7280' }}>Temps:</span>
                      <div style={{ fontWeight: '500', color: '#2C1810' }}>{(log.processing_time_ms / 1000).toFixed(1)}s</div>
                    </div>
                  )}
                  {log.recipe_id && (
                    <div className="col-span-2">
                      <Link 
                        href={`/recipes/${log.recipe_id}`}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        Voir la recette →
                      </Link>
                    </div>
                  )}
                </div>

                {!log.success && log.error_message && (
                  <div className="mt-3 pt-3 border-t border-red-200 text-xs text-red-700">
                    <strong>Erreur:</strong> {log.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>

          {filteredLogs.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <div className="text-4xl mb-3">🔍</div>
              <p className="text-lg font-medium mb-1">Aucune extraction trouvée</p>
              <p className="text-sm">
                {searchQuery ? 'Essayez une autre recherche' : 'Aucun log ne correspond aux filtres sélectionnés'}
              </p>
            </div>
          )}
        </div>
        </div>
      </div>
    </>
  );
}
