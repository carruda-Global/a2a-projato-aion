import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const agentConfig = {
  'spec-analyst': {
    key: 'spec_analyst', fields: [{ key: 'document', type: 'textarea', placeholderKey: 'Cole o documento de engenharia aqui...' }],
    action: (d) => api.analyzeDocument(d.document),
  },
  procurement: {
    key: 'procurement', fields: [{ key: 'materials', type: 'textarea', placeholderKey: '[{"name": "Cimento", "quantity": 100, "unit": "kg"}]' }],
    action: (d) => api.processOrder(JSON.parse(d.materials || '[]')),
  },
  inventory: {
    key: 'inventory', fields: [{ key: 'items', type: 'textarea', placeholderKey: '[{"name": "Cimento", "stock": 10, "min_stock": 20, "daily_use": 5}]' }],
    action: (d) => api.checkStock(JSON.parse(d.items || '[]')),
  },
  logistics: {
    key: 'logistics', fields: [{ key: 'shipment', type: 'textarea', placeholderKey: '{"product": "Cimento", "origin": "SP", "destination": "RJ"}' }],
    action: (d) => api.trackShipment(JSON.parse(d.shipment || '{}')),
  },
  'field-execution': {
    key: 'field_execution', fields: [{ key: 'specs', type: 'textarea', placeholderKey: 'Descreva o projeto...' }],
    action: (d) => api.fieldInstructions(d.specs),
  },
  'bim-coordinator': {
    key: 'bim_coordinator', fields: [{ key: 'description', type: 'textarea', placeholderKey: 'Descreva o elemento 3D...' }],
    action: (d) => api.agentAction('bim-coordinator', 'generate-bim-element', { description: d.description }),
  },
  'requirements-analyst': {
    key: 'requirements_analyst', fields: [{ key: 'requirements', type: 'textarea', placeholderKey: 'Cole os requisitos...' }],
    action: (d) => api.agentAction('requirements-analyst', 'analyze-requirements', { requirements: d.requirements }),
  },
  'engineering-assistant': {
    key: 'engineering_assistant', fields: [{ key: 'question', type: 'textarea', placeholderKey: 'Digite sua pergunta...' }],
    action: (d) => api.agentAction('engineering-assistant', 'answer-question', { question: d.question }),
  },
  'work-synopsis': {
    key: 'work_synopsis', fields: [{ key: 'task_data', type: 'textarea', placeholderKey: 'Descreva a tarefa...' }],
    action: (d) => api.agentAction('work-synopsis', 'generate-synopsis', { task_data: d.task_data }),
  },
  'photo-intelligence': {
    key: 'photo_intelligence', fields: [{ key: 'photo_description', type: 'textarea', placeholderKey: 'Descreva a foto...' }],
    action: (d) => api.agentAction('photo-intelligence', 'analyze-photo', { photo_description: d.photo_description }),
  },
  'rfi-creation': {
    key: 'rfi_creation', fields: [{ key: 'question', type: 'textarea', placeholderKey: 'Descreva a dúvida...' }],
    action: (d) => api.agentAction('rfi-creation', 'create-rfi', { question: d.question }),
  },
  compliance: {
    key: 'compliance', fields: [{ key: 'project_data', type: 'textarea', placeholderKey: 'Descreva o projeto...' }],
    action: (d) => api.agentAction('compliance', 'check-compliance', { project_data: d.project_data }),
  },
  'onboarding-funcionarios': {
    key: 'onboarding_funcionarios', fields: [{ key: 'employee_data', type: 'textarea', placeholderKey: 'Dados do funcionario (nome, cargo, documento)...' }],
    action: (d) => api.agentAction('onboarding-funcionarios', 'run-onboarding', { employee_data: d.employee_data }),
  },
  'atendimento-cliente-ptbr': {
    key: 'atendimento_cliente_ptbr', fields: [{ key: 'ticket', type: 'textarea', placeholderKey: 'Descreva o ticket de atendimento...' }],
    action: (d) => api.agentAction('atendimento-cliente-ptbr', 'resolve-ticket', { ticket: d.ticket }),
  },
  'conciliacao-financeira': {
    key: 'conciliacao_financeira', fields: [{ key: 'financial_data', type: 'textarea', placeholderKey: 'Dados para conciliacao (NFs, extratos)...' }],
    action: (d) => api.agentAction('conciliacao-financeira', 'run-conciliation', { financial_data: d.financial_data }),
  },
};

const fieldLabels = {
  document: 'Documento', materials: 'Materiais (JSON)', items: 'Itens (JSON)',
  shipment: 'Dados do Envio (JSON)', specs: 'Especificações do Projeto',
  description: 'Descrição do Elemento', requirements: 'Requisitos',
  question: 'Pergunta', task_data: 'Dados da Tarefa',
  photo_description: 'Descrição da Foto', project_data: 'Dados do Projeto',
  employee_data: 'Dados do Funcionário', ticket: 'Ticket de Atendimento',
  financial_data: 'Dados Financeiros',
};

export default function AgentDetail() {
  const { agentId } = useParams();
  const { t } = useTranslation();
  const config = agentConfig[agentId];
  const [form, setForm] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendation, setRecommendation] = useState(null);

  const agentKey = agentId?.replace(/-/g, '_');

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_URL || '';
    fetch(`${apiBase}/api/cross-sell/recommend/default?completed_agent=${agentKey}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.recommendation) setRecommendation(data.recommendation);
      })
      .catch(() => {});
  }, [agentKey]);

  if (!config) {
    const agent = t(`agents.${agentKey}`, { returnObjects: true });
    if (!agent || !agent.name) return <div className="error-page">{t('agent_detail.not_found')}</div>;

    const fallbackConfig = {
      key: agentKey,
      fields: [{ key: 'input', type: 'textarea', placeholderKey: t('common.loading') }],
      action: async (d) => {
        const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/v1/agents/${agentId}/run`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(d),
        });
        return res.json();
      },
    };
    return renderDetail(fallbackConfig, form, setForm, result, setResult, loading, setLoading, error, setError, handleSubmit, t, recommendation);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await config.action(form);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return renderDetail(config, form, setForm, result, setResult, loading, setLoading, error, setError, handleSubmit, t, recommendation);
}

function renderDetail(config, form, setForm, result, setResult, loading, setLoading, error, setError, handleSubmit, t, recommendation) {
  const agent = t(`agents.${config.key}`, { returnObjects: true });
  return (
    <div className="agent-detail">
      <h1>{agent.icon} {agent.name}</h1>
      <p className="agent-description">{agent.description}</p>

      {recommendation && (
        <div className="cross-sell-banner" style={{
          background: 'linear-gradient(135deg, #1e40af, #3b82f6)',
          color: '#fff',
          borderRadius: 12,
          padding: '12px 16px',
          marginBottom: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}>
          <span style={{ fontSize: '1.3rem' }}>➡️</span>
          <div style={{ flex: 1 }}>
            <strong style={{ fontSize: '0.9rem' }}>Próximo passo recomendado:</strong>
            <p style={{ fontSize: '0.82rem', opacity: 0.9, marginTop: 2 }}>
              {recommendation.message}
            </p>
          </div>
          <Link
            to={`/agent/${recommendation.recommended_agent.replace(/_/g, '-')}`}
            className="btn-primary"
            style={{ background: '#fff', color: '#1e40af', border: 'none', padding: '6px 14px', borderRadius: 8, fontWeight: 600, fontSize: '0.82rem', textDecoration: 'none', whiteSpace: 'nowrap' }}
          >
            Conhecer {recommendation.recommended_agent_name}
          </Link>
        </div>
      )}

      <form onSubmit={handleSubmit} className="agent-form">
        {config.fields.map((f) => (
          <div key={f.key} className="form-group">
            <label>{fieldLabels[f.key] || f.key}</label>
            {f.type === 'textarea' ? (
              <textarea
                rows={6}
                placeholder={f.placeholderKey}
                value={form[f.key] || ''}
                onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
              />
            ) : (
              <input
                type="text"
                placeholder={f.placeholderKey}
                value={form[f.key] || ''}
                onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
              />
            )}
          </div>
        ))}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? t('agent_detail.processing') : t('agent_detail.execute')}
        </button>
      </form>

      {error && <div className="error-box">{t('agent_detail.error')}: {error}</div>}

      {result && (
        <div className="result-box">
          <h3>{t('agent_detail.result')}</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
