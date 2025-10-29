'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

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

  const isAdmin = user && user.role === 'admin';

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

  if (!isAdmin) {
    return null;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <p className="text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Link
              href="/admin/ai"
              className="text-blue-600 hover:text-blue-800"
            >
              ← Retour à la gestion IA
            </Link>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📊 Statistiques d&apos;extraction IA
          </h1>
          <p className="text-gray-600">
            Suivi détaillé de l&apos;utilisation et des coûts
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {stats && (
          <>
            {/* Period Selector */}
            <div className="mb-6 bg-white p-4 rounded-lg shadow-sm">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Période d&apos;analyse
              </label>
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={7}>7 derniers jours</option>
                <option value={30}>30 derniers jours</option>
                <option value={90}>90 derniers jours</option>
                <option value={365}>1 an</option>
              </select>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-sm font-medium text-gray-600 mb-2">
                  Total Extractions
                </div>
                <div className="text-3xl font-bold text-gray-900">
                  {stats.summary.total_extractions}
                </div>
                <div className="text-sm text-gray-500 mt-2">
                  {stats.summary.successful} réussies · {stats.summary.failed} échouées
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-sm font-medium text-gray-600 mb-2">
                  Taux de réussite
                </div>
                <div className="text-3xl font-bold text-green-600">
                  {stats.summary.success_rate.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500 mt-2">
                  Confiance moyenne: {(stats.summary.average_confidence * 100).toFixed(1)}%
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-sm font-medium text-gray-600 mb-2">
                  Coût Total
                </div>
                <div className="text-3xl font-bold text-blue-600">
                  ${stats.costs.total_usd.toFixed(2)}
                </div>
                <div className="text-sm text-gray-500 mt-2">
                  ${stats.costs.average_per_extraction_usd.toFixed(4)} / extraction
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-sm font-medium text-gray-600 mb-2">
                  Tokens utilisés
                </div>
                <div className="text-3xl font-bold text-purple-600">
                  {(stats.tokens.total / 1000).toFixed(1)}K
                </div>
                <div className="text-sm text-gray-500 mt-2">
                  {stats.tokens.ai_extractions} extractions IA
                </div>
              </div>
            </div>

            {/* By Provider */}
            <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Par fournisseur
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(stats.by_provider).map(([provider, data]) => (
                  <div key={provider} className="border border-gray-200 rounded-lg p-4">
                    <div className="font-semibold text-gray-900 mb-2 capitalize">
                      {provider}
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total:</span>
                        <span className="font-medium">{data.count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Réussis:</span>
                        <span className="font-medium text-green-600">{data.successful}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Échoués:</span>
                        <span className="font-medium text-red-600">{data.failed}</span>
                      </div>
                      {data.total_tokens > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Tokens:</span>
                          <span className="font-medium">{(data.total_tokens / 1000).toFixed(1)}K</span>
                        </div>
                      )}
                      {data.total_cost_usd > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Coût:</span>
                          <span className="font-medium text-blue-600">${data.total_cost_usd.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Daily Breakdown */}
            <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Tendance quotidienne (7 derniers jours)
              </h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Réussis
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Échoués
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Coût
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stats.daily_breakdown.map((day) => (
                      <tr key={day.date}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(day.date).toLocaleDateString('fr-FR')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {day.total}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                          {day.successful}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                          {day.failed}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600">
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
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              Extractions récentes
            </h2>
            <div className="flex gap-2">
              <select
                value={logsProvider}
                onChange={(e) => setLogsProvider(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="">Tous les fournisseurs</option>
                <option value="openai">OpenAI</option>
                <option value="tesseract">Tesseract</option>
              </select>
              <select
                value={logsSuccess}
                onChange={(e) => setLogsSuccess(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="">Tous</option>
                <option value="true">Réussis seulement</option>
                <option value="false">Échoués seulement</option>
              </select>
              <select
                value={logsLimit}
                onChange={(e) => setLogsLimit(Number(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recette
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Méthode
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confiance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tokens
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Coût
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Temps
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr key={log.id} className={log.success ? '' : 'bg-red-50'}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(log.created_at).toLocaleString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {log.recipe_title || 'Sans titre'}
                      {log.recipe_id && (
                        <Link 
                          href={`/recipes/${log.recipe_id}`}
                          className="ml-2 text-blue-600 hover:text-blue-800"
                        >
                          →
                        </Link>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="capitalize font-medium">
                        {log.provider || log.extraction_method}
                      </span>
                      {log.model_name && (
                        <div className="text-xs text-gray-500">{log.model_name}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.confidence_score !== null 
                        ? `${(log.confidence_score * 100).toFixed(0)}%`
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.total_tokens || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600">
                      {log.estimated_cost_usd !== null
                        ? `$${log.estimated_cost_usd.toFixed(4)}`
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.processing_time_ms !== null
                        ? `${(log.processing_time_ms / 1000).toFixed(1)}s`
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {log.success ? (
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                          ✓ Réussi
                        </span>
                      ) : (
                        <span 
                          className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium cursor-help"
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

          {logs.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Aucune extraction trouvée
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
