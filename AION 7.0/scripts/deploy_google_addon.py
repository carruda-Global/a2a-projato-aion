"""Deploy Google Workspace Add-on via Apps Script API."""
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/script.deployments",
    "https://www.googleapis.com/auth/script.projects",
    "https://www.googleapis.com/auth/script.external_request",
]

SCRIPT_ID = "1F1g1xx4gMU2u3U8hMBonuIZY5y2vHpj7b1rWIfC0k-74qUpkucDe98U2"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", ".google_token.json")
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "client_secret_757085749411-3gqmku41tvgih5gmk3c2kvkr5hukhfrc.apps.googleusercontent.com.json")


def main():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt="consent")
            print("\n" + "=" * 60)
            print("  ABRA ESTE LINK NO NAVEGADOR:")
            print("=" * 60)
            print(auth_url)
            print("=" * 60)
            code = input("\nCole o codigo de autorizacao aqui: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    service = build("script", "v1", credentials=creds)

    code_gs = """function onHomepage(e) { return buildCard(); }
function buildCard() {
  var card = CardService.newCardBuilder();
  var header = CardService.newCardHeader().setTitle('SallesJam Compliance').setSubtitle('Agentes de IA para compliance regulatorio');
  var section = CardService.newCardSection();
  var textInput = CardService.newTextInput().setFieldName('userMessage').setTitle('Pergunte sobre NR-1, LGPD...');
  section.addWidget(textInput);
  var button = CardService.newTextButton().setText('Enviar').setOnClickAction(CardService.newAction().setFunctionName('sendToAgent'));
  section.addWidget(button);
  card.setHeader(header).addSection(section);
  return card.build();
}
function sendToAgent(e) {
  var message = e.formInput.userMessage;
  var response = UrlFetchApp.fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {method: 'post', contentType: 'application/json', payload: JSON.stringify({message: message, page: '/google-addon', market: 'BR'})});
  var data = JSON.parse(response.getContentText());
  var card = CardService.newCardBuilder();
  card.addSection(CardService.newCardSection().addWidget(CardService.newTextParagraph().setText(data.response)));
  return CardService.newActionResponseBuilder().setNavigation(CardService.newNavigation().pushCard(card.build())).build();
}
function onGmailMessageOpen(e) {
  var messageId = e.gmail.messageId;
  var accessToken = e.gmail.accessToken;
  GmailApp.setCurrentMessageAccessToken(accessToken);
  var message = GmailApp.getMessageById(messageId);
  var body = message.getPlainBody();
  var card = CardService.newCardBuilder();
  card.setHeader(CardService.newCardHeader().setTitle('SallesJam - Analise LGPD'));
  var button = CardService.newTextButton().setText('Verificar conformidade LGPD deste email').setOnClickAction(CardService.newAction().setFunctionName('analyzeEmailLGPD').setParameters({body: body.substring(0, 2000)}));
  card.addSection(CardService.newCardSection().addWidget(button));
  return card.build();
}
function analyzeEmailLGPD(e) {
  var body = e.parameters.body;
  var response = UrlFetchApp.fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {method: 'post', contentType: 'application/json', payload: JSON.stringify({message: 'Este email contem dados pessoais que violam LGPD? ' + body, page: '/gmail-addon', market: 'BR'})});
  var data = JSON.parse(response.getContentText());
  var card = CardService.newCardBuilder();
  card.addSection(CardService.newCardSection().addWidget(CardService.newTextParagraph().setText(data.response)));
  return CardService.newActionResponseBuilder().setNavigation(CardService.newNavigation().pushCard(card.build())).build();
}
"""
    appsscript_json = json.dumps({
        "timeZone": "America/Sao_Paulo",
        "addOns": {
            "common": {
                "name": "SallesJam Compliance",
                "logoUrl": "https://engenheiro-producao-ai.onrender.com/static/icons/icon-80.png",
                "homepageTrigger": {"runFunction": "onHomepage"},
            },
            "gmail": {
                "contextualTriggers": [{"unconditional": {}, "onTriggerFunction": "onGmailMessageOpen"}],
            },
        },
        "oauthScopes": [
            "https://www.googleapis.com/auth/gmail.addons.execute",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/script.external_request",
        ],
    })

    body = {
        "files": [
            {"name": "Code", "type": "SERVER_JS", "source": code_gs},
            {"name": "appsscript", "type": "JSON", "source": appsscript_json},
        ]
    }
    result = service.projects().updateContent(body=body, scriptId=SCRIPT_ID).execute()
    print("Projeto atualizado:", result.get("scriptId"))

    deployment = {
        "versionNumber": 1,
        "description": "SallesJam Compliance Add-on",
        "manifestVersion": 1,
    }
    dep_result = service.projects().deployments().create(body=deployment, scriptId=SCRIPT_ID).execute()
    print("Deploy criado:", dep_result.get("deploymentConfig", {}).get("versionNumber"))
    print("URL:", dep_result.get("entryPoints", [{}])[0].get("webAppUrl", "N/A"))


if __name__ == "__main__":
    main()
