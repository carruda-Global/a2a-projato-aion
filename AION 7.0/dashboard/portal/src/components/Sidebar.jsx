import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const agents = [
  { id: 'spec-analyst', navKey: 'spec_analyst', icon: '🔍' },
  { id: 'procurement', navKey: 'procurement', icon: '🛒' },
  { id: 'inventory', navKey: 'inventory', icon: '📦' },
  { id: 'logistics', navKey: 'logistics', icon: '🚚' },
  { id: 'field-execution', navKey: 'field_execution', icon: '🏗️' },
  { id: 'bim-coordinator', navKey: 'bim_coordinator', icon: '📐' },
  { id: 'requirements-analyst', navKey: 'requirements_analyst', icon: '📋' },
  { id: 'engineering-assistant', navKey: 'engineering_assistant', icon: '💬' },
  { id: 'work-synopsis', navKey: 'work_synopsis', icon: '📝' },
  { id: 'photo-intelligence', navKey: 'photo_intelligence', icon: '📸' },
  { id: 'rfi-creation', navKey: 'rfi_creation', icon: '📄' },
  { id: 'compliance', navKey: 'compliance', icon: '⚖️' },
  { id: 'nr1-psicossocial', navKey: 'nr1_psicossocial', icon: '🧠' },
  { id: 'tributario-cbs-ibs', navKey: 'tributario_cbs_ibs', icon: '💰' },
  { id: 'lgpd-operacional', navKey: 'lgpd_operacional', icon: '🔒' },
  { id: 'esg-ifrs', navKey: 'esg_ifrs', icon: '🌱' },
  { id: 'inventario-carbono', navKey: 'inventario_carbono', icon: '🌍' },
  { id: 'escopo3-fornecedores', navKey: 'escopo3_fornecedores', icon: '🔗' },
  { id: 'canal-denuncias', navKey: 'canal_denuncias', icon: '🛡️' },
  { id: 'igualdade-salarial', navKey: 'igualdade_salarial', icon: '⚖️' },
  { id: 'compliance-anticorrupcao', navKey: 'compliance_anticorrupcao', icon: '🔐' },
  { id: 'onboarding-funcionarios', navKey: 'onboarding_funcionarios', icon: '👋' },
  { id: 'atendimento-cliente-ptbr', navKey: 'atendimento_cliente_ptbr', icon: '💬' },
  { id: 'conciliacao-financeira', navKey: 'conciliacao_financeira', icon: '💰' },
];

export default function Sidebar() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('i18nextLng', lng);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <strong>{t('app.title')}</strong>
        <span className="version">{t('app.version')}</span>
      </div>

      <div className="lang-switcher" style={{ padding: '8px 16px', display: 'flex', gap: 4 }}>
        {['pt', 'en', 'es'].map((lng) => (
          <button
            key={lng}
            onClick={() => changeLanguage(lng)}
            style={{
              flex: 1, padding: '4px 8px', fontSize: '0.75rem',
              background: i18n.language.startsWith(lng) ? '#0078d4' : '#e5e7eb',
              color: i18n.language.startsWith(lng) ? '#fff' : '#333',
              border: 'none', borderRadius: 6, cursor: 'pointer',
            }}
          >
            {lng === 'pt' ? 'PT' : lng === 'en' ? 'EN' : 'ES'}
          </button>
        ))}
      </div>

      <nav>
        <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          📊 {t('nav.dashboard')}
        </NavLink>
        <div className="nav-section">{t('nav.agents')}</div>
        {agents.map((a) => (
          <NavLink
            key={a.id}
            to={`/agent/${a.id}`}
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            {a.icon} {t(`nav.${a.navKey}`)}
          </NavLink>
        ))}
        <NavLink to="/journey" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          🗺️ Jornadas
        </NavLink>
        <NavLink to="/subscription" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          💳 {t('nav.plans')}
        </NavLink>
      </nav>
      <div className="sidebar-footer" style={{ padding: '16px', borderTop: '1px solid #e5e7eb', marginTop: 'auto' }}>
        <NavLink to="/support" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} style={{ fontSize: '0.8rem' }}>
          🆘 Suporte
        </NavLink>
        <NavLink to="/privacy" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} style={{ fontSize: '0.8rem' }}>
          🔒 Privacidade
        </NavLink>
        <NavLink to="/terms" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} style={{ fontSize: '0.8rem' }}>
          📜 Termos
        </NavLink>
      </div>
    </aside>
  );
}
