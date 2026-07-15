import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const JOURNEY_NAMES = {
  A: { name: 'Jornada RH → Financeiro → Compliance', icon: '👥', channel: 'Microsoft + Salesforce' },
  B: { name: 'Jornada Fiscal → ESG → Carbono', icon: '🌱', channel: 'Google Cloud' },
  C: { name: 'Jornada AEC → Regulatório → Microsoft', icon: '🏗️', channel: 'Google Cloud → Microsoft (Co-sell)' },
};

const JOURNEY_COLORS = {
  A: '#2563eb',
  B: '#059669',
  C: '#7c3aed',
};

export default function Journey() {
  const { t } = useTranslation();
  const [journeys, setJourneys] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_URL || '';
    fetch(`${apiBase}/api/cross-sell/journeys`)
      .then((r) => r.json())
      .then((data) => setJourneys(data.journeys || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">{t('common.loading')}</div>;

  return (
    <div className="journey-page" style={{ maxWidth: 1000 }}>
      <h1 style={{ fontSize: '1.8rem', marginBottom: 8 }}>🗺️ Jornadas do Cliente</h1>
      <p style={{ color: '#4b5563', marginBottom: 32 }}>
        Expanda seu uso do EcoSystem conforme suas obrigações crescem.
        Cada jornada conecta agentes que se complementam naturalmente.
      </p>

      {journeys.map((journey) => {
        const meta = JOURNEY_NAMES[journey.id] || {};
        const color = JOURNEY_COLORS[journey.id] || '#2563eb';
        return (
          <div key={journey.id} style={{
            background: '#fff',
            borderRadius: 12,
            border: '1px solid #e5e7eb',
            marginBottom: 24,
            overflow: 'hidden',
          }}>
            <div style={{
              background: color,
              color: '#fff',
              padding: '16px 20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <div>
                <strong style={{ fontSize: '1.1rem' }}>{meta.icon} {meta.name}</strong>
                <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: 2 }}>{meta.channel}</div>
              </div>
              <span style={{
                background: 'rgba(255,255,255,0.2)',
                padding: '4px 12px',
                borderRadius: 20,
                fontSize: '0.8rem',
              }}>
                {journey.progress}
              </span>
            </div>

            <div style={{ padding: 16 }}>
              {journey.steps?.length === 0 ? (
                <p style={{ color: '#6b7280', fontStyle: 'italic', padding: 16, textAlign: 'center' }}>
                  Nenhum passo disponível ainda. Comece usando um agente para ativar esta jornada.
                </p>
              ) : (
                journey.steps.map((step, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '10px 0',
                    borderBottom: idx < journey.steps.length - 1 ? '1px solid #e5e7eb' : 'none',
                  }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: '50%',
                      background: step.can_advance ? color : '#e5e7eb',
                      color: step.can_advance ? '#fff' : '#9ca3af',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 700, fontSize: '0.85rem', flexShrink: 0,
                    }}>
                      {step.can_advance ? '✓' : idx + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                        {step.current_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                        → {step.next_name}
                        {step.can_advance && (
                          <Link
                            to={`/agent/${step.next.replace(/_/g, '-')}`}
                            style={{ color, marginLeft: 8, fontWeight: 600, textDecoration: 'none' }}
                          >
                            Ativar com 15% off
                          </Link>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {journey.steps?.length > 0 && (
              <div style={{
                padding: '10px 20px',
                background: '#f9fafb',
                borderTop: '1px solid #e5e7eb',
                fontSize: '0.85rem',
                color: '#6b7280',
                display: 'flex',
                justifyContent: 'space-between',
              }}>
                <span>Passos: {journey.steps.filter(s => s.can_advance).length}/{journey.steps.length}</span>
                <span>Desconto de ativação: 15%</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
