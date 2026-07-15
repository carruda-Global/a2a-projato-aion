import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export default function UpsellNotification({ completedAgent, tenantId = 'default' }) {
  const { t } = useTranslation();
  const [notification, setNotification] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (!completedAgent || dismissed) return;
    const apiBase = import.meta.env.VITE_API_URL || '';
    fetch(`${apiBase}/api/cross-sell/recommend/${tenantId}?completed_agent=${completedAgent}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.notification) setNotification(data.notification);
      })
      .catch(() => {});
  }, [completedAgent, tenantId, dismissed]);

  if (!notification || dismissed) return null;

  const urgencyColor = notification.urgency?.is_urgent ? '#dc2626' : '#2563eb';

  return (
    <div className="upsell-notification" style={{
      background: 'linear-gradient(135deg, #1e40af, #3b82f6)',
      color: '#fff',
      borderRadius: 12,
      padding: '16px 20px',
      marginBottom: 20,
      display: 'flex',
      alignItems: 'flex-start',
      gap: 12,
      position: 'relative',
    }}>
      <span style={{ fontSize: '1.5rem' }}>💡</span>
      <div style={{ flex: 1 }}>
        <strong style={{ display: 'block', marginBottom: 4, fontSize: '0.95rem' }}>
          {notification.title}
        </strong>
        <p style={{ fontSize: '0.85rem', opacity: 0.9, marginBottom: 8 }}>
          {notification.body}
        </p>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button
            className="btn-primary"
            style={{ background: '#fff', color: '#1e40af', border: 'none', padding: '6px 16px', borderRadius: 8, fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}
            onClick={() => window.location.href = `/subscription?plan=${notification.cta?.split(' ')[1] || ''}`}
          >
            {notification.cta || 'Ver plano'}
          </button>
          {notification.urgency && (
            <span style={{ fontSize: '0.75rem', color: urgencyColor, background: 'rgba(255,255,255,0.2)', padding: '2px 10px', borderRadius: 20 }}>
              {notification.urgency.regulation} - {notification.urgency.deadline_days} dias
            </span>
          )}
        </div>
      </div>
      <button
        onClick={() => setDismissed(true)}
        style={{
          background: 'none', border: 'none', color: '#fff', opacity: 0.6,
          cursor: 'pointer', fontSize: '1.2rem', lineHeight: 1, padding: 0,
        }}
        aria-label="Fechar"
      >
        ×
      </button>
    </div>
  );
}
