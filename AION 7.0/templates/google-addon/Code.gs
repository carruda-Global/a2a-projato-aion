function onHomepage(e) {
  return buildCard();
}

function buildCard() {
  var card = CardService.newCardBuilder();
  var header = CardService.newCardHeader()
    .setTitle('SallesJam Compliance')
    .setSubtitle('Agentes de IA para compliance regulatorio');
  var section = CardService.newCardSection();
  var textInput = CardService.newTextInput()
    .setFieldName('userMessage')
    .setTitle('Pergunte sobre NR-1, LGPD...');
  section.addWidget(textInput);
  var button = CardService.newTextButton()
    .setText('Enviar')
    .setOnClickAction(CardService.newAction().setFunctionName('sendToAgent'));
  section.addWidget(button);
  card.setHeader(header).addSection(section);
  return card.build();
}

function sendToAgent(e) {
  var message = e.formInput.userMessage;
  var response = UrlFetchApp.fetch(
    'https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat',
    {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({message: message, page: '/google-addon', market: 'BR'})
    }
  );
  var data = JSON.parse(response.getContentText());
  var card = CardService.newCardBuilder();
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
  var messageId = e.gmail.messageId;
  var accessToken = e.gmail.accessToken;
  GmailApp.setCurrentMessageAccessToken(accessToken);
  var message = GmailApp.getMessageById(messageId);
  var body = message.getPlainBody();
  var card = CardService.newCardBuilder();
  card.setHeader(CardService.newCardHeader().setTitle('SallesJam - Analise LGPD'));
  var button = CardService.newTextButton()
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
  var body = e.parameters.body;
  var response = UrlFetchApp.fetch(
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
  var data = JSON.parse(response.getContentText());
  var card = CardService.newCardBuilder();
  card.addSection(
    CardService.newCardSection().addWidget(
      CardService.newTextParagraph().setText(data.response)
    )
  );
  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().pushCard(card.build()))
    .build();
}
