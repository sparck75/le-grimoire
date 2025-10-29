'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface AIStatus {
  enabled: boolean;
  provider: string;
  openai_configured: boolean;
  openai_model: string | null;
  gemini_configured: boolean;
  fallback_enabled: boolean;
  upload_dir: string;
  max_upload_size: number;
}

interface OpenAIUsage {
  api_key_configured: boolean;
  api_key_prefix: string | null;
  model: string;
  max_tokens: number;
  service_available: boolean;
  usage_dashboard_url: string;
  billing_url: string;
}

interface Provider {
  name: string;
  configured: boolean;
  available: boolean;
  model: string;
  cost_per_1k_tokens?: { input: number; output: number };
  estimated_cost_per_recipe: number;
  accuracy: string;
  setup_url: string | null;
  free_tier?: string;
  status?: string;
}

interface ProvidersData {
  providers: {
    openai: Provider;
    gemini: Provider;
    tesseract: Provider;
  };
  current_provider: string;
  fallback_enabled: boolean;
}

export default function AIAdminPage() {
  const { user } = useAuth();
  const router = useRouter();
  
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [openaiUsage, setOpenaiUsage] = useState<OpenAIUsage | null>(null);
  const [providers, setProviders] = useState<ProvidersData | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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
        
        const [statusRes, usageRes, providersRes] = await Promise.all([
          fetch(`${apiUrl}/api/admin/ai/status`),
          fetch(`${apiUrl}/api/admin/ai/openai/usage`),
          fetch(`${apiUrl}/api/admin/ai/providers`)
        ]);

        if (statusRes.ok) {
          setStatus(await statusRes.json());
        }
        if (usageRes.ok) {
          setOpenaiUsage(await usageRes.json());
        }
        if (providersRes.ok) {
          setProviders(await providersRes.json());
        }
      } catch (err) {
        console.error('Error fetching AI data:', err);
        setError('Erreur lors du chargement des données');
      } finally {
        setLoading(false);
      }
    }

    if (isAdmin) {
      fetchData();
    }
  }, [isAdmin]);

  const updateConfig = async (updates: any) => {
    setUpdating(true);
    setError(null);
    setSuccess(null);

    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/api/admin/ai/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        throw new Error('Échec de la mise à jour');
      }

      const result = await response.json();
      setSuccess(result.message);
      
      // Refresh status
      const statusRes = await fetch(`${apiUrl}/api/admin/ai/status`);
      if (statusRes.ok) {
        setStatus(await statusRes.json());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de mise à jour');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div>
        <div className="admin-header">
          <h1>🤖 Gestion IA</h1>
        </div>
        <div className="loading">Chargement...</div>
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
      <div className="admin-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>🤖 Gestion de l&apos;IA</h1>
        <Link href="/admin" className="btn btn-secondary">
          ← Retour au Tableau de Bord
        </Link>
      </div>

      {error && (
        <div style={{ 
          padding: '1rem', margin: '1rem 0', backgroundColor: '#f8d7da', 
          color: '#721c24', borderRadius: '8px', border: '1px solid #f5c6cb'
        }}>
          ⚠️ {error}
        </div>
      )}

      {success && (
        <div style={{ 
          padding: '1rem', margin: '1rem 0', backgroundColor: '#d4edda', 
          color: '#155724', borderRadius: '8px', border: '1px solid #c3e6cb'
        }}>
          ✅ {success}
        </div>
      )}

      {/* Status Card */}
      <div className="admin-card" style={{ marginBottom: '2rem' }}>
        <div className="card-header">
          <h2>📊 État Actuel</h2>
        </div>
        <div className="card-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
            <div>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: '#666' }}>Extraction IA</h3>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: status?.enabled ? '#28a745' : '#dc3545' }}>
                {status?.enabled ? '✅ Activée' : '❌ Désactivée'}
              </div>
              <button
                onClick={() => updateConfig({ enabled: !status?.enabled })}
                disabled={updating}
                className="btn btn-primary"
                style={{ marginTop: '0.75rem', fontSize: '0.875rem' }}
              >
                {updating ? '⏳' : status?.enabled ? 'Désactiver' : 'Activer'}
              </button>
            </div>

            <div>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: '#666' }}>Fournisseur Actuel</h3>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                {status?.provider === 'openai' ? '🧠 OpenAI' : 
                 status?.provider === 'gemini' ? '🔮 Gemini' : 
                 status?.provider === 'tesseract' ? '📝 OCR' : 
                 status?.provider}
              </div>
              {status?.provider === 'openai' && status?.openai_model && (
                <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.25rem' }}>
                  Modèle: {status.openai_model}
                </div>
              )}
            </div>

            <div>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: '#666' }}>Secours OCR</h3>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: status?.fallback_enabled ? '#28a745' : '#6c757d' }}>
                {status?.fallback_enabled ? '✅ Activé' : '❌ Désactivé'}
              </div>
              <button
                onClick={() => updateConfig({ fallback_enabled: !status?.fallback_enabled })}
                disabled={updating}
                className="btn btn-secondary"
                style={{ marginTop: '0.75rem', fontSize: '0.875rem' }}
              >
                {updating ? '⏳' : status?.fallback_enabled ? 'Désactiver' : 'Activer'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* OpenAI Card */}
      {openaiUsage && (
        <div className="admin-card" style={{ marginBottom: '2rem' }}>
          <div className="card-header">
            <h2>🧠 OpenAI GPT-4 Vision</h2>
          </div>
          <div className="card-content">
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Configuration</h3>
              <div style={{ display: 'grid', gap: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                  <span><strong>Clé API:</strong></span>
                  <span style={{ fontFamily: 'monospace', color: openaiUsage.api_key_configured ? '#28a745' : '#dc3545' }}>
                    {openaiUsage.api_key_configured ? openaiUsage.api_key_prefix : '❌ Non configurée'}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                  <span><strong>Modèle:</strong></span>
                  <span style={{ fontFamily: 'monospace' }}>{openaiUsage.model}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                  <span><strong>Tokens Max:</strong></span>
                  <span style={{ fontFamily: 'monospace' }}>{openaiUsage.max_tokens}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                  <span><strong>Service:</strong></span>
                  <span style={{ color: openaiUsage.service_available ? '#28a745' : '#dc3545', fontWeight: 'bold' }}>
                    {openaiUsage.service_available ? '✅ Disponible' : '❌ Indisponible'}
                  </span>
                </div>
              </div>
            </div>

            <div style={{ padding: '1rem', backgroundColor: '#e7f3ff', borderRadius: '8px', border: '1px solid #bee5eb' }}>
              <h4 style={{ marginTop: 0, marginBottom: '0.75rem', color: '#004085' }}>
                📈 Utilisation et Coûts
              </h4>
              <p style={{ margin: '0.5rem 0', fontSize: '0.95rem', color: '#004085' }}>
                OpenAI ne fournit pas d&apos;API pour consulter l&apos;utilisation et les coûts de manière programmatique. 
                Consultez votre tableau de bord OpenAI pour voir les détails:
              </p>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                <a 
                  href={openaiUsage.usage_dashboard_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ fontSize: '0.875rem' }}
                >
                  📊 Voir l&apos;Utilisation
                </a>
                <a 
                  href={openaiUsage.billing_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                  style={{ fontSize: '0.875rem' }}
                >
                  💳 Voir la Facturation
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Providers Comparison */}
      {providers && (
        <div className="admin-card">
          <div className="card-header">
            <h2>🔧 Fournisseurs Disponibles</h2>
          </div>
          <div className="card-content">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
              {/* OpenAI */}
              <div style={{ 
                padding: '1.5rem', 
                border: '2px solid ' + (providers.current_provider === 'openai' ? '#007bff' : '#dee2e6'),
                borderRadius: '12px',
                backgroundColor: providers.current_provider === 'openai' ? '#e7f3ff' : '#fff'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0, fontSize: '1.25rem' }}>🧠 {providers.providers.openai.name}</h3>
                  {providers.providers.openai.available && (
                    <span style={{ 
                      padding: '0.25rem 0.5rem', 
                      backgroundColor: '#28a745', 
                      color: 'white', 
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: 'bold'
                    }}>
                      ACTIF
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
                  <div><strong>Modèle:</strong> {providers.providers.openai.model}</div>
                  <div><strong>Précision:</strong> {providers.providers.openai.accuracy}</div>
                  <div><strong>Coût/recette:</strong> ~${providers.providers.openai.estimated_cost_per_recipe.toFixed(2)}</div>
                  <div><strong>Statut:</strong> {providers.providers.openai.configured ? '✅ Configuré' : '❌ Non configuré'}</div>
                </div>
                {!providers.providers.openai.configured && providers.providers.openai.setup_url && (
                  <a 
                    href={providers.providers.openai.setup_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                    style={{ fontSize: '0.875rem', width: '100%' }}
                  >
                    Configurer OpenAI
                  </a>
                )}
                {providers.providers.openai.configured && providers.current_provider !== 'openai' && (
                  <button
                    onClick={() => updateConfig({ provider: 'openai' })}
                    disabled={updating}
                    className="btn btn-success"
                    style={{ fontSize: '0.875rem', width: '100%' }}
                  >
                    Utiliser ce Fournisseur
                  </button>
                )}
              </div>

              {/* Gemini */}
              <div style={{ 
                padding: '1.5rem', 
                border: '2px solid ' + (providers.current_provider === 'gemini' ? '#007bff' : '#dee2e6'),
                borderRadius: '12px',
                backgroundColor: providers.current_provider === 'gemini' ? '#e7f3ff' : '#fff',
                opacity: providers.providers.gemini.available ? 1 : 0.6
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0, fontSize: '1.25rem' }}>🔮 {providers.providers.gemini.name}</h3>
                  {providers.providers.gemini.status && (
                    <span style={{ 
                      padding: '0.25rem 0.5rem', 
                      backgroundColor: '#ffc107', 
                      color: '#000', 
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: 'bold'
                    }}>
                      BIENTÔT
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
                  <div><strong>Modèle:</strong> {providers.providers.gemini.model}</div>
                  <div><strong>Précision:</strong> {providers.providers.gemini.accuracy}</div>
                  <div><strong>Gratuit:</strong> {providers.providers.gemini.free_tier}</div>
                  <div><strong>Statut:</strong> {providers.providers.gemini.status || 'Non disponible'}</div>
                </div>
                {providers.providers.gemini.setup_url && (
                  <a 
                    href={providers.providers.gemini.setup_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                    style={{ fontSize: '0.875rem', width: '100%' }}
                  >
                    En Savoir Plus
                  </a>
                )}
              </div>

              {/* Tesseract */}
              <div style={{ 
                padding: '1.5rem', 
                border: '2px solid ' + (providers.current_provider === 'tesseract' ? '#007bff' : '#dee2e6'),
                borderRadius: '12px',
                backgroundColor: providers.current_provider === 'tesseract' ? '#e7f3ff' : '#fff'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0, fontSize: '1.25rem' }}>📝 {providers.providers.tesseract.name}</h3>
                  <span style={{ 
                    padding: '0.25rem 0.5rem', 
                    backgroundColor: '#28a745', 
                    color: 'white', 
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    fontWeight: 'bold'
                  }}>
                    GRATUIT
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
                  <div><strong>Moteur:</strong> {providers.providers.tesseract.model}</div>
                  <div><strong>Précision:</strong> {providers.providers.tesseract.accuracy}</div>
                  <div><strong>Coût/recette:</strong> Gratuit</div>
                  <div><strong>Statut:</strong> ✅ Toujours disponible</div>
                </div>
                {providers.current_provider !== 'tesseract' && (
                  <button
                    onClick={() => updateConfig({ provider: 'tesseract' })}
                    disabled={updating}
                    className="btn btn-success"
                    style={{ fontSize: '0.875rem', width: '100%' }}
                  >
                    Utiliser ce Fournisseur
                  </button>
                )}
              </div>
            </div>

            <div style={{ 
              marginTop: '2rem', 
              padding: '1rem', 
              backgroundColor: '#fff3cd', 
              borderRadius: '8px', 
              border: '1px solid #ffeaa7'
            }}>
              <h4 style={{ marginTop: 0, marginBottom: '0.5rem', color: '#856404' }}>
                💡 Conseil
              </h4>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#856404' }}>
                Pour modifier définitivement la configuration, éditez le fichier <code>.env</code> et redémarrez le service. 
                Les modifications via cette interface sont temporaires et seront perdues au redémarrage.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
