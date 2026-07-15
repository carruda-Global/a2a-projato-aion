import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const PLANS_DATA = [
  { key: 'compliance_essencial', id: 'regulatory_starter', name: 'Compliance Essencial — NR-1 + LGPD', price: 59000, agents: ['NR-1', 'LGPD'], features: ['NR-1 Riscos Psicossociais (Portaria MTE 1.419/2024)', 'LGPD Operacional (Lei 13.709/2018)', 'Inventario FRPRT e plano de acao', 'RoPA e mapeamento de dados', 'Relatorios para fiscalizacao', 'Resultado em 48h'], icon: '⚖️', color: '#25D366' },
  { key: 'regulatory_pro', id: 'regulatory_professional', name: 'Regulatory Pro — Obrigacoes Completas', price: 149000, agents: ['NR-1', 'LGPD', 'Denuncias', 'Igualdade', 'Anticorrupcao'], features: ['NR-1 Psicossocial', 'LGPD Operacional', 'Canal de Denuncias (Lei 14.457/2022)', 'Igualdade Salarial (Lei 14.611/2023)', 'Compliance Anticorrupcao (Lei 12.846/2013)'], icon: '⚡', color: '#6366f1' },
  { key: 'esg_carbon', id: 'esg_carbon_pack', name: 'ESG + Carbono PME', price: 249000, agents: ['ESG', 'Carbono', 'Escopo 3'], features: ['ESG IFRS S1/S2 (Res. CVM 193/2023)', 'Inventario de Carbono Escopo 1/2 (GHG Protocol)', 'Escopo 3 Fornecedores (SBCE + CBAM)', 'Relatorios para SBCE e IFRS'], icon: '🌱', color: '#059669' },
  { key: 'full_suite', id: 'full_suite', name: 'Full Suite — Todos os Agentes', price: 949700, agents: ['27 agentes'], features: ['AEC Core + Especializados + Conformidade', 'Regulatorios + ESG + Carbono + Escopo 3', 'Microsoft Pack completo (6 agentes M365)', 'Suporte prioritario 24/7'], icon: '🚀', color: '#10b981' },
  { key: 'microsoft_pack', id: 'microsoft_pack', name: 'Microsoft Compliance Pack', price: 448200, agents: ['Reg Analyst', 'Compliance PM', 'Channel', 'Knowledge', 'Facilitator', 'Dev Exp'], features: ['Regulatory Analyst (SharePoint/OneDrive)', 'Compliance PM (Planner)', 'Channel Agent Regulatorio (Teams)', 'Knowledge Agent com RAG', 'Facilitator Agent (reunioes)', 'Dev Experience Agent (PRs)'], icon: '🪟', color: '#0078d4' },
  { key: 'starter', id: 'starter', name: 'Starter — Spec Analyst', price: 99700, agents: ['Spec Analyst'], features: ['Analise de ate 50 documentos/mes', 'Extracao de requisitos tecnicos', 'Sinalizacao de nao-conformidades'], icon: '🔍', color: '#6366f1', hidden: true },
  { key: 'professional', id: 'professional', name: 'Professional — 3 Agentes AEC', price: 239100, agents: ['Spec Analyst', 'Procurement', 'Inventory'], features: ['Analise de documentos ilimitada', 'Compras e pedidos automatizados', 'Monitoramento de estoque'], icon: '🛒', color: '#6366f1', hidden: true },
  { key: 'enterprise', id: 'enterprise', name: 'Enterprise — 5 Agentes AEC', price: 468500, agents: ['Spec Analyst', 'Procurement', 'Inventory', 'Logistics', 'Field Exec'], features: ['Logistica e rastreamento', 'Instrucoes de campo com IA', 'Cross-selling automatico'], icon: '🏢', color: '#6366f1', hidden: true },
  { key: 'compliance_pack', id: 'compliance_pack', name: 'Compliance Pack — Conformidade AEC', price: 239100, agents: ['Photo Intelligence', 'RFI Creation', 'Compliance'], features: ['Photo Intelligence para obras', 'Criacao automatica de RFIs', 'Gestao de conformidade PGRS/PGRSS'], icon: '⚖️', color: '#6366f1', hidden: true },
  { key: 'regulatory_full', id: 'regulatory_full', name: 'Regulatory Full — Todos os Regulatorios', price: 349000, agents: ['9 agentes'], features: ['Todos os 9 agentes regulatorios', 'Tributario CBS/IBS', 'ESG IFRS S1/S2', 'Inventario Carbono + Escopo 3'], icon: '🏛️', color: '#6366f1', hidden: true },
];

export default function Subscription() {
  const { t } = useTranslation();
  const [checkoutLoading, setCheckoutLoading] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const planParam = params.get('plan');
    if (planParam) {
      setTimeout(() => {
        const el = document.getElementById(`plan-${planParam}`);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 500);
    }
  }, []);

  const formatPrice = (cents) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);

  const handleSubscribe = async (planId) => {
    setCheckoutLoading(planId);
    try {
      const plan = PLANS_DATA.find(p => p.key === planId);
      const mappedId = plan ? plan.id : planId;
      const data = await api.createCheckout(mappedId);
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert('Erro ao criar checkout. Tente novamente.');
      }
    } catch (err) {
      alert('Erro: ' + err.message);
    } finally {
      setCheckoutLoading(null);
    }
  };

  return (
    <div className="subscription-page">
      <h1>💳 {t('subscription.title')}</h1>
      <p className="subtitle">{t('subscription.subtitle')}</p>

      <div className="plans-grid">
        {PLANS_DATA.filter(p => !p.hidden).map((plan) => (
          <div key={plan.key} id={`plan-${plan.id}`} className="plan-card"
               style={{ borderTop: `4px solid ${plan.color}` }}>
            <div className="plan-icon">{plan.icon}</div>
            <h3>{plan.name}</h3>
            <div className="plan-price">{formatPrice(plan.price)}<span>{t('subscription.per_month')}</span></div>
            <div className="plan-agent-count">
              {plan.agents.length} {plan.agents.length === 1 ? t('subscription.agent') : t('subscription.agents')}
            </div>
            <ul className="plan-features">
              {plan.features.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
            <div className="plan-agents">
              {plan.agents.map((a) => (
                <span key={a} className="tag">{a}</span>
              ))}
            </div>
            <button
              className="btn-primary"
              onClick={() => handleSubscribe(plan.key)}
              disabled={checkoutLoading === plan.key}
            >
              {checkoutLoading === plan.key ? t('subscription.redirecting') : t('subscription.subscribe')}
            </button>
          </div>
        ))}
      </div>

      <div className="upgrade-info" style={{ marginTop: 32, padding: 20, background: '#f8fafc', borderRadius: 12 }}>
        <h3>🔄 {t('subscription.upgrade_title')}</h3>
        <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
          {t('subscription.trial_info')}
        </p>
      </div>
    </div>
  );
}
