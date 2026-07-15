# AION — MASTER FINAL: Plugins Universais + Expansão Global
**Global Match Engenharia de Produção | Cristiano Arruda**
**Data:** 2026-06-24
**Este documento consolida:** tudo que ainda não foi implementado, incluindo os 3 plugins universais (Microsoft, Google, Chrome) e os 2 agentes novos de expansão global (Índia, Emirados Árabes)
**Pré-requisito:** o documento IMPLEMENTACAO_TOTAL_5_MERCADOS.md já cobre Brasil + EUA + México + Colômbia + Argentina — este documento é o complemento final

---

## ORDEM DE EXECUÇÃO — 14 DIAS (depois dos 21 dias anteriores)

```
DIA 1-4   → Office Add-in (Microsoft) — alcance 400M usuários globais
DIA 5-7   → Google Workspace Add-on — alcance 3B usuários Gmail
DIA 8-10  → Chrome Extension — alcance 3,4B instalações, funciona em qualquer site
DIA 11-12 → Índia Multilingual Support Agent
DIA 13-14 → UAE Government Process Agent
```

---

## PARTE 1 — OFFICE ADD-IN (Microsoft) — 400 milhões de usuários

### O que é
Painel que aparece dentro do Excel, Word, Outlook e Teams. Cliente nunca sai do programa — o EcoSystem abre como Task Pane lateral.

### 1.1 Manifest — manifest.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<OfficeApp
  xmlns="http://schemas.microsoft.com/office/appforoffice/1.1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:bt="http://schemas.microsoft.com/office/officeappbasictypes/1.0"
  xmlns:ov="http://schemas.microsoft.com/office/taskpaneappversionoverrides"
  xsi:type="TaskPaneApp">
  <Id>a1b2c3d4-e5f6-7890-abcd-ef1234567890</Id>
  <Version>1.0.0.0</Version>
  <ProviderName>Global Match Engenharia de Producao</ProviderName>
  <DefaultLocale>pt-BR</DefaultLocale>
  <DisplayName DefaultValue="EcoSystem Compliance"/>
  <Description DefaultValue="Agentes de IA para compliance regulatorio - NR-1, LGPD, CBS/IBS e mais"/>
  <IconUrl DefaultValue="https://global-engenharia.com/assets/icon-32.png"/>
  <HighResolutionIconUrl DefaultValue="https://global-engenharia.com/assets/icon-80.png"/>
  <SupportUrl DefaultValue="https://global-engenharia.com/suporte"/>

  <Hosts>
    <Host Name="Workbook"/>
    <Host Name="Document"/>
    <Host Name="Mailbox"/>
  </Hosts>

  <DefaultSettings>
    <SourceLocation DefaultValue="https://engenheiro-producao-ai.onrender.com/office-addin/taskpane.html"/>
  </DefaultSettings>

  <Permissions>ReadWriteDocument</Permissions>

  <VersionOverrides xmlns="http://schemas.microsoft.com/office/taskpaneappversionoverrides" xsi:type="VersionOverridesV1_0">
    <Hosts>
      <Host xsi:type="Workbook">
        <DesktopFormFactor>
          <GetStarted>
            <Title resid="GetStarted.Title"/>
            <Description resid="GetStarted.Description"/>
            <LearnMoreUrl resid="GetStarted.LearnMoreUrl"/>
          </GetStarted>
          <FunctionFile resid="Commands.Url"/>
          <ExtensionPoint xsi:type="PrimaryCommandSurface">
            <OfficeTab id="TabHome">
              <Group id="EcoSystemGroup">
                <Label resid="GroupLabel"/>
                <Icon>
                  <bt:Image size="16" resid="Icon.16x16"/>
                  <bt:Image size="32" resid="Icon.32x32"/>
                  <bt:Image size="80" resid="Icon.80x80"/>
                </Icon>
                <Control xsi:type="Button" id="TaskpaneButton">
                  <Label resid="TaskpaneButton.Label"/>
                  <Supertip>
                    <Title resid="TaskpaneButton.Label"/>
                    <Description resid="TaskpaneButton.Tooltip"/>
                  </Supertip>
                  <Icon>
                    <bt:Image size="16" resid="Icon.16x16"/>
                    <bt:Image size="32" resid="Icon.32x32"/>
                    <bt:Image size="80" resid="Icon.80x80"/>
                  </Icon>
                  <Action xsi:type="ShowTaskpane">
                    <TaskpaneId>ButtonId1</TaskpaneId>
                    <SourceLocation resid="Taskpane.Url"/>
                  </Action>
                </Control>
              </Group>
            </OfficeTab>
          </ExtensionPoint>
        </DesktopFormFactor>
      </Host>
    </Hosts>
    <Resources>
      <bt:Images>
        <bt:Image id="Icon.16x16" DefaultValue="https://global-engenharia.com/assets/icon-16.png"/>
        <bt:Image id="Icon.32x32" DefaultValue="https://global-engenharia.com/assets/icon-32.png"/>
        <bt:Image id="Icon.80x80" DefaultValue="https://global-engenharia.com/assets/icon-80.png"/>
      </bt:Images>
      <bt:Urls>
        <bt:Url id="Commands.Url" DefaultValue="https://engenheiro-producao-ai.onrender.com/office-addin/commands.html"/>
        <bt:Url id="Taskpane.Url" DefaultValue="https://engenheiro-producao-ai.onrender.com/office-addin/taskpane.html"/>
        <bt:Url id="GetStarted.LearnMoreUrl" DefaultValue="https://global-engenharia.com/ecosystem"/>
      </bt:Urls>
      <bt:ShortStrings>
        <bt:String id="GetStarted.Title" DefaultValue="EcoSystem Compliance ativado!"/>
        <bt:String id="GroupLabel" DefaultValue="EcoSystem"/>
        <bt:String id="TaskpaneButton.Label" DefaultValue="Compliance IA"/>
      </bt:ShortStrings>
      <bt:LongStrings>
        <bt:String id="GetStarted.Description" DefaultValue="Acesse seus agentes de compliance direto no Excel"/>
        <bt:String id="TaskpaneButton.Tooltip" DefaultValue="Abrir EcoSystem Compliance"/>
      </bt:LongStrings>
    </Resources>
  </VersionOverrides>
</OfficeApp>
```

### 1.2 Task Pane — app/routers/office_addin.py

```python
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
    input{width:100%;padding:10px;border-radius:6px;border:none;background:#1A2540;color:#fff;margin-bottom:8px}
    button{width:100%;padding:10px;border-radius:6px;border:none;background:#00C36B;color:#fff;font-weight:600;cursor:pointer}
    .msg-bot{background:#1A2540;padding:8px;border-radius:8px;margin-bottom:6px}
    .msg-user{background:#00C36B33;padding:8px;border-radius:8px;margin-bottom:6px;text-align:right}
  </style>
</head>
<body>
  <h2>EcoSystem Compliance</h2>
  <p style="font-size:11px;color:#94A3B8">Analise sua planilha diretamente, sem sair do Excel</p>
  <div id="chat-area"></div>
  <input id="msg-input" placeholder="Pergunte sobre NR-1, LGPD..."/>
  <button onclick="sendMessage()">Enviar</button>
  <button onclick="analyzeSheet()" style="margin-top:8px;background:#1A2540">Analisar planilha atual</button>

  <script>
    Office.onReady(() => { console.log('EcoSystem Add-in pronto'); });

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
            message: 'Analise estes dados de planilha para compliance NR-1/LGPD: ' + JSON.stringify(range.values),
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
    with open("manifest.xml") as f:
        return f.read()
```

### 1.3 Publicar no AppSource
```
1. partner.microsoft.com/dashboard -> Office Store
2. Upload manifest.xml
3. Validacao automatica + revisao manual (3-7 dias)
4. Publicado -> visivel para todos os 400M usuarios Office globalmente
```

---

## PARTE 2 — GOOGLE WORKSPACE ADD-ON — 3 bilhões de usuários Gmail

### 2.1 Apps Script — Code.gs

```javascript
function onHomepage(e) {
  return buildCard();
}

function buildCard() {
  const card = CardService.newCardBuilder();

  const header = CardService.newCardHeader()
    .setTitle('EcoSystem Compliance')
    .setSubtitle('Agentes de IA para compliance regulatorio');

  const section = CardService.newCardSection();
  const textInput = CardService.newTextInput()
    .setFieldName('userMessage')
    .setTitle('Pergunte sobre NR-1, LGPD...');
  section.addWidget(textInput);

  const button = CardService.newTextButton()
    .setText('Enviar')
    .setOnClickAction(CardService.newAction().setFunctionName('sendToAgent'));
  section.addWidget(button);

  card.setHeader(header).addSection(section);
  return card.build();
}

function sendToAgent(e) {
  const message = e.formInput.userMessage;
  const response = UrlFetchApp.fetch(
    'https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat',
    {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({message: message, page: '/google-addon', market: 'BR'})
    }
  );
  const data = JSON.parse(response.getContentText());

  const card = CardService.newCardBuilder();
  card.addSection(
    CardService.newCardSection().addWidget(
      CardService.newTextParagraph().setText(data.response)
    )
  );
  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().pushCard(card.build()))
    .build();
}

function onGmailMessageOpen(e) {
  const messageId = e.gmail.messageId;
  const accessToken = e.gmail.accessToken;
  GmailApp.setCurrentMessageAccessToken(accessToken);
  const message = GmailApp.getMessageById(messageId);
  const body = message.getPlainBody();

  const card = CardService.newCardBuilder();
  card.setHeader(CardService.newCardHeader().setTitle('EcoSystem - Analise LGPD'));

  const button = CardService.newTextButton()
    .setText('Verificar conformidade LGPD deste email')
    .setOnClickAction(
      CardService.newAction()
        .setFunctionName('analyzeEmailLGPD')
        .setParameters({body: body.substring(0, 2000)})
    );

  card.addSection(CardService.newCardSection().addWidget(button));
  return card.build();
}

function analyzeEmailLGPD(e) {
  const body = e.parameters.body;
  const response = UrlFetchApp.fetch(
    'https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat',
    {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({
        message: 'Este email contem dados pessoais que violam LGPD? ' + body,
        page: '/gmail-addon', market: 'BR'
      })
    }
  );
  const data = JSON.parse(response.getContentText());
  const card = CardService.newCardBuilder();
  card.addSection(
    CardService.newCardSection().addWidget(
      CardService.newTextParagraph().setText(data.response)
    )
  );
  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().pushCard(card.build()))
    .build();
}
```

### 2.2 appsscript.json (manifest)
```json
{
  "timeZone": "America/Sao_Paulo",
  "addOns": {
    "common": {
      "name": "EcoSystem Compliance",
      "logoUrl": "https://global-engenharia.com/assets/icon-80.png",
      "homepageTrigger": {
        "runFunction": "onHomepage"
      }
    },
    "gmail": {
      "contextualTriggers": [{
        "unconditional": {},
        "onTriggerFunction": "onGmailMessageOpen"
      }]
    }
  },
  "oauthScopes": [
    "https://www.googleapis.com/auth/gmail.addons.execute",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/script.external_request"
  ]
}
```

### 2.3 Publicar
```
1. script.google.com -> New Project -> colar Code.gs e appsscript.json
2. Deploy -> Test deployments (testar primeiro)
3. Deploy -> New deployment -> Add-on
4. Google Workspace Marketplace -> Publish (revisao 1-3 semanas)
```

---

## PARTE 3 — CHROME EXTENSION — funciona em qualquer site do mundo

### Por que e o mais poderoso
Nao depende de estar dentro de Microsoft, Google ou Salesforce. Funciona em qualquer pagina, incluindo sites de governo (Receita Federal, INSS, Gov.br) onde nenhuma outra integracao chegaria.

### 3.1 manifest.json

```json
{
  "manifest_version": 3,
  "name": "EcoSystem Compliance - NR-1, LGPD e Compliance com IA",
  "version": "1.0.0",
  "description": "Agentes de IA para compliance regulatorio disponiveis em qualquer site",
  "icons": {
    "16": "icon16.png",
    "48": "icon48.png",
    "128": "icon128.png"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon48.png"
  },
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["https://engenheiro-producao-ai.onrender.com/*"],
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"]
  }]
}
```

### 3.2 popup.html + popup.js

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body{width:340px;height:480px;margin:0;background:#0C1322;font-family:sans-serif}
    #chat-area{height:340px;overflow-y:auto;padding:12px;color:#fff;font-size:13px}
    input{width:90%;margin:8px;padding:10px;border-radius:6px;border:none;background:#1A2540;color:#fff}
    button{width:90%;margin:0 8px 8px;padding:10px;border-radius:6px;border:none;background:#00C36B;color:#fff;font-weight:600;cursor:pointer}
    .header{background:#00C36B;padding:12px;color:#fff;font-weight:600}
  </style>
</head>
<body>
  <div class="header">EcoSystem Compliance</div>
  <div id="chat-area"></div>
  <input id="msg-input" placeholder="Pergunte sobre NR-1, LGPD..."/>
  <button id="send-btn">Enviar</button>
  <script src="popup.js"></script>
</body>
</html>
```

```javascript
document.getElementById('send-btn').addEventListener('click', async () => {
  const input = document.getElementById('msg-input');
  const chatArea = document.getElementById('chat-area');
  const msg = input.value;
  if(!msg) return;

  chatArea.innerHTML += '<div style="text-align:right;margin-bottom:6px"><span style="background:#00C36B33;padding:6px 10px;border-radius:8px;display:inline-block">' + msg + '</span></div>';
  input.value = '';

  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

  const resp = await fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message: msg, page: tab.url, market: 'BR'})
  });
  const data = await resp.json();
  chatArea.innerHTML += '<div style="margin-bottom:6px"><span style="background:#1A2540;padding:6px 10px;border-radius:8px;display:inline-block">' + data.response + '</span></div>';
  chatArea.scrollTop = chatArea.scrollHeight;
});
```

### 3.3 content.js — detecta contexto da página automaticamente

```javascript
const relevantSites = ['gov.br', 'receita.fazenda', 'inss.gov', 'mte.gov'];
const currentUrl = window.location.hostname;

if (relevantSites.some(site => currentUrl.includes(site))) {
  const banner = document.createElement('div');
  banner.innerHTML = '<div style="position:fixed;bottom:20px;right:20px;background:#00C36B;color:#fff;padding:12px 16px;border-radius:8px;z-index:99999;font-family:sans-serif;font-size:13px;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.3)" id="ecosystem-banner">Precisa de ajuda com compliance aqui? Clique no icone do EcoSystem</div>';
  document.body.appendChild(banner);
  setTimeout(() => banner.remove(), 8000);
}
```

### 3.4 Publicar
```
1. chrome.google.com/webstore/devconsole
2. Taxa unica: USD 5 (registro de desenvolvedor)
3. Upload do .zip com manifest.json + popup.html + popup.js + content.js
4. Revisao: 1-3 dias
5. Publicado -> disponivel para 3,4B instalacoes de Chrome no mundo
```

---

## PARTE 4 — ÍNDIA: MULTILINGUAL SUPPORT AGENT

### Por que a Índia
93% dos lideres indianos pretendem usar agentes de IA em 12-18 meses, sinal de demanda mais forte do mundo. Mercado e-commerce e fintech em expansao rapida.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/india", tags=["india_agent"])

SYSTEM_PROMPT_IN = """You are the EcoSystem Multilingual Support Agent for India.
Respond in the language the user writes in - English, Hindi, or any regional language.
You help e-commerce and fintech companies automate customer support across
multiple Indian languages, reducing support team costs by 60-80%.
Always offer the activation link when interest is shown."""

@router.post("/chat")
async def chat_india(data: dict):
    from src.api.deepseek_client import DeepSeekClient
    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system=SYSTEM_PROMPT_IN,
        user=data.get("message", "")
    )
    return {"response": response, "checkout_url": "CRIAR_PRICE_USD_INDIA"}
```

Preço: USD 29-149/mês (volume compensa ticket baixo).
SEO: páginas em inglês e hindi para "AI customer support India", "multilingual chatbot ecommerce".

---

## PARTE 5 — EMIRADOS ÁRABES: GOVERNMENT PROCESS AGENT

### Por que os Emirados
Dubai já treinou mais de 1.500 funcionários públicos em agentes com Microsoft e OpenAI — governo ativamente investindo em IA para serviços públicos.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/uae", tags=["uae_agent"])

SYSTEM_PROMPT_UAE = """You are the EcoSystem Government Process Agent for UAE.
Help businesses navigate visa processes, permits, fines, and banking
compliance in the UAE. Focus on efficiency and clarity for expat-run
businesses and financial services companies expanding into the Gulf.
Always offer the activation link when interest is shown."""

@router.post("/chat")
async def chat_uae(data: dict):
    from src.api.deepseek_client import DeepSeekClient
    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system=SYSTEM_PROMPT_UAE,
        user=data.get("message", "")
    )
    return {"response": response, "checkout_url": "CRIAR_PRICE_USD_UAE"}
```

Preço: USD 990-9.900/mês (contratos governamentais e bancários têm ticket alto).
SEO: páginas em inglês e árabe para "UAE business setup compliance", "Dubai banking compliance AI".

---

## PARTE 6 — SQL — TABELAS DESTE DOCUMENTO

```sql
CREATE TABLE plugin_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_source TEXT,
    page_context TEXT,
    message TEXT,
    response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_plugin_source ON plugin_usage(plugin_source);
```

---

## CHECKLIST FINAL — 14 DIAS

### Dia 1-4 — Microsoft Office Add-in
- [ ] Criar manifest.xml
- [ ] Criar app/routers/office_addin.py com taskpane.html
- [ ] Registrar router em app/main.py
- [ ] Criar icones 16x16, 32x32, 80x80
- [ ] Testar localmente via sideload no Excel
- [ ] Submeter para AppSource (partner.microsoft.com)

### Dia 5-7 — Google Workspace Add-on
- [ ] Criar projeto em script.google.com
- [ ] Colar Code.gs e appsscript.json
- [ ] Testar deployment de teste
- [ ] Submeter para Google Workspace Marketplace

### Dia 8-10 — Chrome Extension
- [ ] Criar manifest.json, popup.html, popup.js, content.js
- [ ] Criar icones 16, 48, 128px
- [ ] Testar localmente (chrome://extensions -> modo desenvolvedor)
- [ ] Pagar taxa de registro USD 5
- [ ] Submeter para Chrome Web Store

### Dia 11-12 — Índia
- [ ] Criar src/agents/india_multilingual_agent.py
- [ ] Criar price_id Stripe USD
- [ ] Gerar paginas SEO em ingles/hindi

### Dia 13-14 — Emirados Árabes
- [ ] Criar src/agents/uae_government_agent.py
- [ ] Criar price_id Stripe USD
- [ ] Gerar paginas SEO em ingles/arabe

---

## RESUMO — ALCANCE TOTAL APÓS ESTE DOCUMENTO

| Canal | Alcance global |
|-------|----------------|
| Office Add-in | 400 milhões de usuários |
| Google Workspace Add-on | 3 bilhões de usuários Gmail |
| Chrome Extension | 3,4 bilhões de instalações |
| Índia (agente novo) | Mercado de maior crescimento do mundo |
| UAE (agente novo) | Hub financeiro e governamental do Golfo |

Combinado com os documentos anteriores (Brasil + EUA + México + Colômbia + Argentina + Alemanha via Hermes + Japão via Physical AI + Reino Unido via EU AI Act), o AION cobre 11 mercados com 3 canais de distribuição universal que não dependem de aprovação país por país.

---

Documento final consolidado, gerado em 2026-06-24.
Passar integralmente para o DeepSeek Flash, seguindo a ordem exata de 14 dias.
Este documento complementa, não substitui, o IMPLEMENTACAO_TOTAL_5_MERCADOS.md anterior.
