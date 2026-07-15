from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/office-addin", tags=["office_addin"])

TASKPANE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <script src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"></script>
  <style>
    body{font-family:'Segoe UI',sans-serif;background:#0C1322;color:#fff;margin:0;padding:16px}
    h2{font-size:16px;color:#00C36B}
    #chat-area{height:300px;overflow-y:auto;background:#131D30;border-radius:8px;padding:12px;margin:12px 0;font-size:13px}
    input{width:100%;padding:10px;border-radius:6px;border:none;background:#1A2540;color:#fff;margin-bottom:8px;box-sizing:border-box}
    button{width:100%;padding:10px;border-radius:6px;border:none;background:#00C36B;color:#fff;font-weight:600;cursor:pointer}
    .msg-bot{background:#1A2540;padding:8px;border-radius:8px;margin-bottom:6px}
    .msg-user{background:#00C36B33;padding:8px;border-radius:8px;margin-bottom:6px;text-align:right}
  </style>
</head>
<body>
  <h2>SallesJam Compliance</h2>
  <p style="font-size:11px;color:#94A3B8">Analise sua planilha sem sair do Excel</p>
  <div id="chat-area"></div>
  <input id="msg-input" placeholder="Pergunte sobre NR-1, LGPD..."/>
  <button onclick="sendMessage()">Enviar</button>
  <button onclick="analyzeSheet()" style="margin-top:8px;background:#1A2540">Analisar planilha atual</button>
  <script>
    Office.onReady(() => { console.log('SallesJam Add-in pronto'); });
    async function sendMessage(){
      const input = document.getElementById('msg-input');
      const chatArea = document.getElementById('chat-area');
      const msg = input.value;
      if(!msg) return;
      chatArea.innerHTML += '<div class="msg-user">' + msg + '</div>';
      input.value = '';
      const resp = await fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({message: msg, page: '/office-addin', market: 'BR'})
      });
      const data = await resp.json();
      chatArea.innerHTML += '<div class="msg-bot">' + data.response + '</div>';
      chatArea.scrollTop = chatArea.scrollHeight;
    }
    async function analyzeSheet(){
      Excel.run(async (context) => {
        const range = context.workbook.getSelectedRange();
        range.load('values');
        await context.sync();
        const chatArea = document.getElementById('chat-area');
        chatArea.innerHTML += '<div class="msg-user">Analisar dados selecionados</div>';
        const resp = await fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({
            message: 'Analise estes dados para compliance NR-1/LGPD: ' + JSON.stringify(range.values),
            page: '/office-addin/excel', market: 'BR'
          })
        });
        const data = await resp.json();
        chatArea.innerHTML += '<div class="msg-bot">' + data.response + '</div>';
      });
    }
  </script>
</body>
</html>
"""


@router.get("/taskpane.html", response_class=HTMLResponse)
async def taskpane():
    return TASKPANE_HTML


@router.get("/manifest.xml")
async def get_manifest():
    from pathlib import Path
    manifest_path = Path(__file__).parent.parent.parent / "templates" / "office-addin" / "manifest.xml"
    return manifest_path.read_text(encoding="utf-8")
