const relevantSites = ['gov.br', 'receita.fazenda', 'inss.gov', 'mte.gov'];
const currentUrl = window.location.hostname;

if (relevantSites.some(site => currentUrl.includes(site))) {
  const banner = document.createElement('div');
  banner.innerHTML = '<div style="position:fixed;bottom:20px;right:20px;background:#00C36B;color:#fff;padding:12px 16px;border-radius:8px;z-index:99999;font-family:sans-serif;font-size:13px;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.3)" id="sallesjam-banner">Precisa de ajuda com compliance aqui? Clique no icone do SallesJam</div>';
  document.body.appendChild(banner);
  setTimeout(() => banner.remove(), 8000);
}
