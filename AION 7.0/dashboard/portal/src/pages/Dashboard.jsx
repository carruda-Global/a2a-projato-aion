import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import AgentCard from '../components/AgentCard';
import UpsellNotification from '../components/UpsellNotification';

const agentKeys = [
  'spec_analyst', 'procurement', 'inventory', 'logistics', 'field_execution',
  'bim_coordinator', 'requirements_analyst', 'engineering_assistant', 'work_synopsis',
  'photo_intelligence', 'rfi_creation', 'compliance',
  'nr1_psicossocial', 'tributario_cbs_ibs', 'lgpd_operacional', 'esg_ifrs',
  'inventario_carbono', 'escopo3_fornecedores', 'canal_denuncias',
  'igualdade_salarial', 'compliance_anticorrupcao',
  'onboarding_funcionarios', 'atendimento_cliente_ptbr', 'conciliacao_financeira',
];

const agentTags = {
  spec_analyst: ['1M tokens', 'OCR'],
  procurement: ['Cross-selling'],
  inventory: ['Tempo real'],
  logistics: ['Tracking'],
  field_execution: ['BIM', 'RA'],
  bim_coordinator: ['BIM', '3D'],
  requirements_analyst: ['Qualidade'],
  engineering_assistant: ['Chat', 'IA'],
  work_synopsis: ['Resumo'],
  photo_intelligence: ['Visão'],
  rfi_creation: ['RFI', 'Docs'],
  compliance: ['PGRS', 'Normas'],
  nr1_psicossocial: ['NR-1', 'MTE'],
  tributario_cbs_ibs: ['CBS', 'IBS'],
  lgpd_operacional: ['LGPD', 'ANPD'],
  esg_ifrs: ['ESG', 'CVM'],
  inventario_carbono: ['SBCE', 'GHG'],
  escopo3_fornecedores: ['CBAM', 'IFRS'],
  canal_denuncias: ['CIPA', '14.457'],
  igualdade_salarial: ['14.611', 'MTE'],
  compliance_anticorrupcao: ['CGU', '12.846'],
  onboarding_funcionarios: ['eSocial', 'RH'],
  atendimento_cliente_ptbr: ['WhatsApp', 'L1'],
  conciliacao_financeira: ['NFs', 'Extratos'],
};

export default function Dashboard() {
  const { t } = useTranslation();
  const [health, setHealth] = useState(null);
  const [apiOk, setApiOk] = useState(false);
  const [recentAgent, setRecentAgent] = useState(null);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL || ''}/health`)
      .then((r) => r.json())
      .then((d) => { setHealth(d); setApiOk(true); })
      .catch(() => setApiOk(false));
    const last = localStorage.getItem('last_agent_used');
    if (last) setRecentAgent(last);
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{t('dashboard.title')}</h1>
        <div className={`status-badge ${apiOk ? 'online' : 'offline'}`}>
          {apiOk ? t('dashboard.api_online') : t('dashboard.api_offline')}
        </div>
      </div>

      {health && (
        <div className="health-bar">
          <span>🤖 {t('dashboard.agents_label')}: {health.agents?.join(', ') || 'N/A'}</span>
          <span>🧠 {t('dashboard.deepseek')}: {health.deepseek === 'connected' ? t('dashboard.connected') : t('dashboard.disconnected')}</span>
          <span>📦 {t('dashboard.version')}: {health.version}</span>
        </div>
      )}

      {recentAgent && <UpsellNotification completedAgent={recentAgent} />}

      <div className="agent-grid">
        {agentKeys.map((key) => {
          const agent = t(`agents.${key}`, { returnObjects: true });
          return (
            <AgentCard
              key={key}
              id={key.replace(/_/g, '-')}
              icon={agent.icon}
              title={agent.name}
              description={agent.description}
              tags={agentTags[key] || []}
            />
          );
        })}
      </div>
    </div>
  );
}
