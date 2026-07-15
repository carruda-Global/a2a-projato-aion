const { Client, LocalAuth } = require("whatsapp-web.js");
const QRCode = require("qrcode");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

const QUEUE_FILE = path.join(__dirname, "..", "data", "sdr", "whatsapp_queue.json");
const SENT_FILE = path.join(__dirname, "..", "data", "sdr", "whatsapp_enviados.json");
const QR_FILE = path.join(__dirname, "..", "data", "sdr", "whatsapp_qr.png");
const DELAY_MS = 15000;
const WPP_OWNER = "5511994798464";

// Limite diario de envios, para "aquecer" um numero novo aos poucos e
// reduzir risco de banimento. Aumente gradualmente ao longo das semanas
// (ex: 20-30 na 1a semana, 50-80 na 2a, etc).
const DAILY_LIMIT = parseInt(process.env.WHATSAPP_DAILY_LIMIT || "25", 10);

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: path.join(__dirname, ".wwebjs_auth") }),
  puppeteer: { headless: true, args: ["--no-sandbox"] },
});

client.on("qr", async (qr) => {
  console.log("Gerando QR Code...");
  await QRCode.toFile(QR_FILE, qr, { width: 500, margin: 2, color: { dark: "#25D366", light: "#FFF" } });
  console.log("QR salvo:", QR_FILE);
  console.log("Escaneie com WhatsApp > Dispositivos Conectados > Vincular");
  exec(`start "" "${QR_FILE}"`);
});

client.on("ready", async () => {
  console.log("\n=== WHATSAPP CONECTADO ===\n");

  if (!fs.existsSync(QUEUE_FILE)) {
    console.log("Nenhum prospect. Rode: python scripts/sdr_pipeline.py");
    process.exit(0);
  }

  let queue = JSON.parse(fs.readFileSync(QUEUE_FILE, "utf8"));
  let sent = fs.existsSync(SENT_FILE) ? JSON.parse(fs.readFileSync(SENT_FILE, "utf8")) : [];
  let pending = queue.filter(q => !sent.find(s => s.empresa === q.empresa));

  const today = new Date().toISOString().slice(0, 10);
  const sentToday = sent.filter(s => (s.enviado_em || "").slice(0, 10) === today).length;
  const remainingToday = Math.max(0, DAILY_LIMIT - sentToday);

  console.log(`Fila: ${queue.length} | Enviados: ${sent.length} | Pendentes: ${pending.length}`);
  console.log(`Limite diario: ${DAILY_LIMIT} | Enviados hoje: ${sentToday} | Restante hoje: ${remainingToday}\n`);

  if (pending.length === 0) {
    console.log("Tudo enviado!");
    process.exit(0);
  }

  if (remainingToday === 0) {
    console.log("Limite diario atingido. Rode de novo amanha (ou ajuste WHATSAPP_DAILY_LIMIT).");
    process.exit(0);
  }

  pending = pending.slice(0, remainingToday);

  for (let i = 0; i < pending.length; i++) {
    const lead = pending[i];
    const msg = `${lead.msg}\n\nglobal-engenharia.com/ecosystem`;

    console.log(`[${i + 1}/${pending.length}] ${lead.empresa} — ${lead.cargo}`);

    let targetNumber = lead.numero ? lead.numero.replace(/\D/g, "") : null;
    let sentToOwner = false;

    if (targetNumber && targetNumber.length >= 10) {
      try {
        const chatId = `${targetNumber}@c.us`;
        const isRegistered = await client.isRegisteredUser(chatId);
        
        if (isRegistered) {
          await client.sendMessage(chatId, msg);
          lead.status = "enviado_direto";
          lead.enviado_em = new Date().toISOString();
          console.log(`  [OK] Enviado direto pra ${targetNumber}`);
        } else {
          console.log(`  [AVISO] ${targetNumber} nao tem WhatsApp - salvando pra voce`);
          sentToOwner = true;
        }
      } catch (err) {
        console.log(`  [ERRO] ${targetNumber}: ${err.message}`);
        sentToOwner = true;
      }
    } else {
      sentToOwner = true;
    }

    if (sentToOwner) {
      const me = client.info.wid._serialized;
      await client.sendMessage(me, `[ENCAMINHAR PARA: ${lead.empresa} — ${lead.cargo}]\n\n${msg}`);
      lead.status = "enviado_para_voce";
      lead.enviado_em = new Date().toISOString();
      console.log(`  [OK] Salvo no seu WhatsApp pra encaminhar`);
    }

    sent.push(lead);
    queue = queue.map(q => {
      if (q.empresa === lead.empresa) {
        q.status = lead.status;
        q.enviado_em = lead.enviado_em;
      }
      return q;
    });
    fs.writeFileSync(QUEUE_FILE, JSON.stringify(queue, null, 2));
    fs.writeFileSync(SENT_FILE, JSON.stringify(sent, null, 2));

    console.log(`  Aguardando ${DELAY_MS / 1000}s...`);
    await new Promise(r => setTimeout(r, DELAY_MS));
  }

  console.log(`\n=== CONCLUIDO: ${pending.length} mensagens ===`);
  process.exit(0);
});

client.on("disconnected", () => { console.log("Desconectado"); process.exit(0); });

console.log("Conectando...");
client.initialize();
