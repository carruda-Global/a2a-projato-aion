document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  const url = tab.url || '';
  const govSites = ['gov.br', 'receita.fazenda', 'inss.gov', 'mte.gov'];
  if (govSites.some(site => url.includes(site))) {
    document.getElementById('chat-area').innerHTML =
      '<div style="background:#00C36B33;padding:8px;border-radius:8px;margin-bottom:8px">🌐 Site governamental detectado. Pergunte sobre compliance aqui!</div>';
  }
});

document.getElementById('send-btn').addEventListener('click', async () => {
  const input = document.getElementById('msg-input');
  const chatArea = document.getElementById('chat-area');
  const msg = input.value;
  if(!msg) return;

  chatArea.innerHTML += '<div class="msg-user">' + msg + '</div>';
  input.value = '';

  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

  const resp = await fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message: msg, page: tab.url, market: 'BR'})
  });
  const data = await resp.json();
  chatArea.innerHTML += '<div class="msg-bot">' + data.response + '</div>';
  chatArea.scrollTop = chatArea.scrollHeight;
});

document.getElementById('msg-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') document.getElementById('send-btn').click();
});
