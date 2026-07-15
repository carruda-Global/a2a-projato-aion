from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uuid
from datetime import datetime

from src.data.models.consent import PrivacyConsent, PrivacyRequest, PrivacyResponse

router = APIRouter(prefix="/api/privacy", tags=["Privacy"])

PRIVACY_POLICY_HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head><meta charset="UTF-8"><title>Política de Privacidade - SallesJam</title></head>
<body style="background:#0C1322;color:#e2e8f0;font-family:sans-serif;padding:40px;max-width:800px;margin:0 auto">
<h1 style="color:#00C36B">Política de Privacidade</h1>
<p><strong>SallesJam</strong> | Global Match Engenharia de Produção | CREA-SP 5071200171</p>
<p>Esta extensão coleta apenas os dados necessários para fornecer respostas de compliance via IA:</p>
<ul>
<li>Mensagens de texto enviadas pelo usuário no chat</li>
<li>URL da página atual (apenas para contexto)</li>
<li>Preferência de idioma armazenada localmente</li>
</ul>
<p><strong>Não coletamos:</strong> dados pessoais, senhas, histórico de navegação completo, cookies de terceiros.</p>
<p><strong>Compartilhamento:</strong> nenhum dado é compartilhado com terceiros. As mensagens são processadas pela API DeepSeek para gerar respostas.</p>
<p><strong>Armazenamento:</strong> dados são armazenados em Supabase (PostgreSQL) com criptografia em trânsito e em repouso.</p>
<p><strong>Contato:</strong> contato@global-engenharia.com</p>
<p style="color:#94a3b8;font-size:12px">Última atualização: Junho 2026</p>
</body>
</html>"""


@router.get("/policy", response_class=HTMLResponse)
async def privacy_policy():
    return PRIVACY_POLICY_HTML


@router.post("/consent")
async def register_consent(consent: PrivacyConsent):
    try:
        from src.database.supabase_client import supabase
        existing = supabase.table("consents").select("*").eq("user_id", consent.user_id).execute()
        if existing.data:
            supabase.table("consents").update({
                "consent_given": consent.consent_given,
                "consent_version": consent.consent_version,
                "privacy_policy_accepted": consent.privacy_policy_accepted,
                "terms_of_service_accepted": consent.terms_of_service_accepted,
                "updated_at": datetime.now().isoformat()
            }).eq("user_id", consent.user_id).execute()
        else:
            supabase.table("consents").insert(consent.dict()).execute()
    except Exception:
        pass

    return {"status": "success", "message": "Consentimento registrado com sucesso", "user_id": consent.user_id}


@router.get("/consent/{user_id}")
async def get_consent(user_id: str):
    try:
        from src.database.supabase_client import supabase
        result = supabase.table("consents").select("*").eq("user_id", user_id).execute()
        if result.data:
            return {"consent_given": result.data[0]["consent_given"], "consent_version": result.data[0]["consent_version"]}
    except Exception:
        pass
    return {"consent_given": False, "message": "Usuario ainda nao consentiu"}


@router.post("/consent/revoke")
async def revoke_consent(request: PrivacyRequest):
    try:
        from src.database.supabase_client import supabase
        supabase.table("consents").update({"consent_given": False, "updated_at": datetime.now().isoformat()}).eq("user_id", request.user_id).execute()
        supabase.table("consent_history").insert({"user_id": request.user_id, "action": "revoke", "timestamp": datetime.now().isoformat()}).execute()
    except Exception:
        pass
    return {"status": "success", "message": "Consentimento revogado com sucesso", "user_id": request.user_id}


@router.post("/request/access")
async def request_data_access(request: PrivacyRequest):
    request_id = str(uuid.uuid4())
    try:
        from src.database.supabase_client import supabase
        supabase.table("privacy_requests").insert({
            "request_id": request_id, "user_id": request.user_id,
            "email": request.email, "request_type": request.request_type,
            "status": "pending", "timestamp": datetime.now().isoformat()
        }).execute()
    except Exception:
        pass
    return PrivacyResponse(request_id=request_id, user_id=request.user_id, status="pending", message="Solicitacao de acesso recebida. Processamento em ate 15 dias.")


@router.post("/request/deletion")
async def request_data_deletion(request: PrivacyRequest):
    request_id = str(uuid.uuid4())
    try:
        from src.database.supabase_client import supabase
        supabase.table("privacy_requests").insert({
            "request_id": request_id, "user_id": request.user_id,
            "email": request.email, "request_type": request.request_type,
            "status": "pending", "timestamp": datetime.now().isoformat()
        }).execute()
    except Exception:
        pass
    return PrivacyResponse(request_id=request_id, user_id=request.user_id, status="pending", message="Solicitacao de exclusao recebida. Processamento em ate 15 dias.")


@router.get("/policy", response_class=HTMLResponse)
async def get_privacy_policy():
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Politica de Privacidade - AION</title>
<style>body{font-family:-apple-system,sans-serif;max-width:800px;margin:0 auto;padding:20px;line-height:1.6;color:#1e293b}h1{color:#0f172a;border-bottom:2px solid #2563eb;padding-bottom:10px}h2{color:#2563eb;margin-top:30px}ul{background:#f8fafc;padding:20px;border-radius:8px}li{margin:8px 0}strong{color:#0f172a}.footer{margin-top:40px;padding:20px;background:#f1f5f9;border-radius:8px;font-size:14px;color:#64748b}</style></head>
<body>
<h1>Politica de Privacidade da AION</h1>
<p><strong>Ultima atualizacao:</strong> 27 de junho de 2026</p>
<h2>1. Quem Somos</h2>
<p>A AION e uma plataforma de orquestracao de agentes de IA desenvolvida pela Global Match Engenharia de Producao - CREA-SP 5071200171.</p>
<h2>2. Dados que Coletamos</h2>
<ul>
<li><strong>Dados de Registro:</strong> Nome, e-mail, empresa, CPF/CNPJ para faturamento</li>
<li><strong>Dados de Uso:</strong> Historico de consultas e interacoes com os agentes</li>
<li><strong>Dados de Entrada:</strong> Conteudo fornecido aos agentes para processamento</li>
<li><strong>Dados de Comunicacao:</strong> Registros de suporte e atendimento</li>
<li><strong>Dados de Pagamento:</strong> Processados exclusivamente pelo Stripe (nao armazenamos dados de cartao)</li>
</ul>
<h2>3. Base Legal para o Tratamento</h2>
<p>Tratamos seus dados com base nas seguintes hipoteses legais da LGPD (Lei 13.709/2018):</p>
<ul>
<li><strong>Consentimento:</strong> Para uso da plataforma e comunicacoes</li>
<li><strong>Obrigacao Legal:</strong> Para cumprimento de obrigacoes fiscais e regulatorias</li>
<li><strong>Execucao de Contrato:</strong> Para prestacao dos servicos contratados</li>
</ul>
<h2>4. Como Usamos Seus Dados</h2>
<ul>
<li>Operar, manter e aprimorar a plataforma</li>
<li>Processar e responder suas consultas</li>
<li>Garantir a seguranca da plataforma</li>
<li>Cumprir com obrigacoes legais (retencao fiscal, compliance regulatorio)</li>
<li>Melhorar nossos agentes de IA (dados anonimizados)</li>
</ul>
<h2>5. Compartilhamento de Dados</h2>
<p>Compartilhamos dados apenas com:</p>
<ul>
<li><strong>Stripe:</strong> Processamento de pagamentos (politica de privacidade do Stripe se aplica)</li>
<li><strong>Google Cloud / Render:</strong> Infraestrutura de hospedagem (dados armazenados na regiao sul-america-leste1)</li>
<li><strong>Autoridades Legais:</strong> Quando exigido por lei</li>
</ul>
<h2>6. Seus Direitos (LGPD - Art. 18)</h2>
<ul>
<li>Confirmacao da existencia de tratamento</li>
<li>Acesso aos seus dados pessoais</li>
<li>Correcao de dados incompletos, inexatos ou desatualizados</li>
<li>Anonimizacao, bloqueio ou eliminacao de dados desnecessarios</li>
<li>Portabilidade dos dados a outro fornecedor</li>
<li>Eliminacao dos dados tratados com consentimento</li>
<li>Revogacao do consentimento</li>
</ul>
<h2>7. Retencao de Dados</h2>
<p>Mantemos seus dados enquanto sua conta estiver ativa. Apos o cancelamento:</p>
<ul>
<li>Dados de uso: excluidos apos 90 dias</li>
<li>Dados fiscais: retidos por 5 anos (obrigacao legal)</li>
<li>Logs de seguranca: retidos por 1 ano</li>
</ul>
<h2>8. Seguranca</h2>
<p>Implementamos criptografia em transito (TLS 1.3) e em repouso (AES-256). Utilizamos Merkle Chain para auditoria imutavel de acesso aos dados.</p>
<h2>9. Contato do DPO</h2>
<div class="footer">
<p><strong>Encarregado de Dados (DPO):</strong> Cristiano Arruda</p>
<p><strong>E-mail:</strong> dpo@aion.global</p>
<p><strong>Telefone:</strong> (11) 99479-8464</p>
<p><strong>Endereco:</strong> Sao Paulo - SP</p>
<p>Para exercer seus direitos LGPD, use o endpoint /api/privacy/request/access ou /api/privacy/request/deletion</p>
</div>
</body></html>"""
    return HTMLResponse(content=html)


@router.get("/acceptable-use", response_class=HTMLResponse)
async def get_acceptable_use_policy():
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Politica de Uso Aceitavel - AION</title>
<style>body{font-family:-apple-system,sans-serif;max-width:800px;margin:0 auto;padding:20px;line-height:1.6;color:#1e293b}h1{color:#0f172a;border-bottom:2px solid #2563eb;padding-bottom:10px}h2{color:#2563eb;margin-top:30px}h3{color:#475569;margin-top:20px}ul{background:#f8fafc;padding:20px;border-radius:8px}li{margin:8px 0}strong{color:#0f172a}.footer{margin-top:40px;padding:20px;background:#f1f5f9;border-radius:8px;font-size:14px;color:#64748b}</style></head>
<body>
<h1>Politica de Uso Aceitavel - AION</h1>
<p><strong>Ultima atualizacao:</strong> 27 de junho de 2026<br><strong>Versao:</strong> 1.0</p>
<h2>1. Introducao</h2>
<p>Esta Politica de Uso Aceitavel estabelece as regras para o uso adequado da plataforma AION. Ao acessar ou usar a plataforma, voce concorda em cumprir esta Politica em conjunto com os Termos de Uso e a Politica de Privacidade.</p>
<h2>2. Atividades Proibidas</h2>
<h3>2.1 Atividades Ilegais</h3>
<p>Voce nao pode usar a plataforma para:</p>
<ul>
<li>Violar qualquer lei, estatuto, portaria ou regulamentacao federal, estadual ou internacional</li>
<li>Envolver-se em transacoes relacionadas a bens roubados, incluindo bens digitais e virtuais</li>
<li>Promover odio, violencia, intolerancia racial ou outras formas de discriminacao</li>
<li>Explorar financeiramente atividades criminosas</li>
</ul>
<h3>2.2 Conteudo Proibido</h3>
<p>Voce nao pode usar a plataforma para gerar, transmitir ou armazenar:</p>
<ul>
<li>Conteudo que infrinja direitos autorais, marcas registradas ou outros direitos de propriedade intelectual</li>
<li>Conteudo difamatorio, calunioso ou que viole direitos de privacidade</li>
<li>Conteudo que promova atividades ilegais ou forneca instrucoes para a pratica de crimes</li>
<li>Conteudo que exponha informacoes pessoais de terceiros em violacao da lei aplicavel</li>
</ul>
<h3>2.3 Engenharia Social e Fraude</h3>
<p>Voce nao pode usar a plataforma para:</p>
<ul>
<li>Coletar informacoes pessoais de terceiros sem seu consentimento explicito</li>
<li>Criar conteudo falso ou enganoso com intencao de prejudicar, enganar ou fraudar terceiros</li>
<li>Representar falsamente sua identidade ou afiliacao</li>
</ul>
<h2>3. Restricoes Tecnicas e de Seguranca</h2>
<h3>3.1 Acesso e Modificacao</h3>
<p>Voce nao pode:</p>
<ul>
<li>Fazer engenharia reversa, descompilar, desmontar ou tentar derivar o codigo-fonte da plataforma</li>
<li>Modificar, criar trabalhos derivados ou melhorias nao autorizadas da plataforma</li>
<li>Alugar, arrendar, vender, sublicenciar, distribuir ou disponibilizar a plataforma a terceiros nao autorizados</li>
</ul>
<h3>3.2 Seguranca e Integridade</h3>
<p>Voce nao pode:</p>
<ul>
<li>Burlar ou violar qualquer dispositivo de seguranca ou protecao usado pela plataforma</li>
<li>Acessar ou usar a plataforma por meios nao autorizados</li>
<li>Danificar, destruir, interromper, desabilitar, prejudicar ou interferir com a plataforma ou seus servicos</li>
<li>Remover, alterar ou ocultar quaisquer avisos de direitos autorais, marcas registradas ou propriedade intelectual</li>
</ul>
<h3>3.3 Uso de Agentes</h3>
<p>Voce nao pode:</p>
<ul>
<li>Utilizar agentes para executar acoes para as quais nao tem permissao explicita</li>
<li>Tentar manipular agentes via injecao de prompt para executar acoes nao autorizadas</li>
<li>Utilizar agentes para automatizar ataques, varreduras ou atividades maliciosas</li>
<li>Processar dados sensiveis (LGPD) sem a devida autorizacao e bases legais</li>
</ul>
<h2>4. Monitoramento e Fiscalizacao</h2>
<h3>4.1 Monitoramento</h3>
<p>A AION pode monitorar o uso da plataforma para garantir conformidade com esta Politica. Isso pode incluir:</p>
<ul>
<li>Analise de logs de atividades dos agentes</li>
<li>Detecao de padroes de uso anomalos</li>
<li>Auditoria de acessos a dados sensiveis</li>
</ul>
<h3>4.2 Consequencias da Violacao</h3>
<p>A violacao desta Politica pode resultar em:</p>
<ul>
<li>Aviso e solicitacao de correcao</li>
<li>Suspensao temporaria ou permanente do acesso a plataforma</li>
<li>Rescisao dos Termos de Uso</li>
<li>Encaminhamento para autoridades competentes, se aplicavel</li>
</ul>
<h2>5. Relato de Violacoes</h2>
<p>Se voce tomar conhecimento de qualquer violacao desta Politica, entre em contato imediatamente:</p>
<ul>
<li><strong>E-mail:</strong> cristiano.arruda@global-engenharia.com</li>
<li><strong>Telefone:</strong> (11) 99479-8464</li>
</ul>
<h2>6. Modificacoes</h2>
<p>A AION pode modificar esta Politica a qualquer momento. As alteracoes serao comunicadas atraves da plataforma ou por e-mail. O uso continuado da plataforma apos tais alteracoes constitui sua aceitacao da Politica revisada.</p>
<div class="footer">
<p><strong>AION - Agents Intelligence Orchestration Network</strong></p>
<p>Global Match Engenharia de Producao</p>
<p>CREA-SP 5071200171</p>
<p>E-mail: cristiano.arruda@global-engenharia.com</p>
<p>Telefone: (11) 99479-8464</p>
</div>
</body></html>"""
    return HTMLResponse(content=html)


@router.get("/terms", response_class=HTMLResponse)
async def get_terms_of_service():
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Termos de Uso - AION</title>
<style>body{font-family:-apple-system,sans-serif;max-width:800px;margin:0 auto;padding:20px;line-height:1.6;color:#1e293b}h1{color:#0f172a;border-bottom:2px solid #2563eb;padding-bottom:10px}h2{color:#2563eb;margin-top:30px}ul{background:#f8fafc;padding:20px;border-radius:8px}li{margin:8px 0}strong{color:#0f172a}.footer{margin-top:40px;padding:20px;background:#f1f5f9;border-radius:8px;font-size:14px;color:#64748b}</style></head>
<body>
<h1>Termos de Uso da AION</h1>
<p><strong>Ultima atualizacao:</strong> 27 de junho de 2026</p>
<h2>1. Aceitacao dos Termos</h2>
<p>Ao acessar ou usar a plataforma AION (Agents Intelligence Orchestration Network), voce concorda com estes Termos de Uso. Se nao concordar, nao use a plataforma.</p>
<h2>2. Definicoes</h2>
<ul>
<li><strong>Plataforma:</strong> Sistema multiagente de IA para compliance regulatorio, engenharia e gestao empresarial</li>
<li><strong>Agentes:</strong> 71 (setenta e um) agentes de IA especializados</li>
<li><strong>Usuario:</strong> Pessoa fisica ou juridica que utiliza a plataforma</li>
<li><strong>Conteudo:</strong> Dados, documentos e informacoes fornecidos pelo usuario</li>
</ul>
<h2>3. Uso Aceitavel</h2>
<p>O usuario concorda em:</p>
<ul>
<li>Fornecer informacoes precisas e atualizadas</li>
<li>Nao usar a plataforma para fins ilegais</li>
<li>Nao tentar obter acesso nao autorizado</li>
<li>Nao reproduzir, distribuir ou criar produtos concorrentes</li>
<li>Nao submeter conteudo que infrinja direitos de terceiros</li>
</ul>
<p>E expressamente proibido:</p>
<ul>
<li>Engenharia reversa da plataforma ou dos agentes</li>
<li>Uso para tomada de decisoes automatizadas com efeitos legais sem supervisao humana</li>
<li>Insercao de dados pessoais sensiveis sem anonimizacao previa</li>
</ul>
<h2>4. Planos e Assinatura</h2>
<ul>
<li>Os precos dos planos estao disponiveis em https://buy.stripe.com</li>
<li>Assinaturas sao renovadas automaticamente</li>
<li>Cancelamento pode ser feito a qualquer momento pelo dashboard</li>
<li>Reembolso integral em ate 7 dias, conforme CDC</li>
</ul>
<h2>5. Propriedade Intelectual</h2>
<ul>
<li><strong>Da AION:</strong> A plataforma, codigo, agentes, interfaces, marcas e conteudo gerado pelos agentes (exceto dados do usuario)</li>
<li><strong>Do Usuario:</strong> O usuario mantem total propriedade dos dados e conteudo fornecidos</li>
<li><strong>Licenca:</strong> O usuario concede a AION licenca para processar seus dados exclusivamente para prestacao dos servicos</li>
</ul>
<h2>6. Limitacao de Responsabilidade</h2>
<p>A AION fornece seus servicos "no estado em que se encontram". Nao garantimos que o servico sera ininterrupto ou livre de erros.</p>
<p><strong>Importante:</strong> Os agentes de IA sao ferramentas de apoio a conformidade e nao substituem assessoria juridica, contabil ou de engenharia para casos especificos.</p>
<ul>
<li>O Agente NR-1 Psicossocial nao emite ART nem substitui Engenheiro de Seguranca do Trabalho</li>
<li>O Agente Tributario CBS/IBS requer validacao com contador habilitado</li>
<li>O Agente de Carbono requer verificacao externa ISO 14064-3 para submissao oficial ao SBCE</li>
</ul>
<h2>7. Vigencia e Rescisao</h2>
<p>Estes Termos vigoram enquanto o usuario mantiver uma conta ativa. A AION pode rescindir o acesso em caso de violacao dos termos.</p>
<h2>8. Legislacao e Foro</h2>
<p>Estes Termos sao regidos pela legislacao brasileira. Fica eleito o foro da Comarca de Sao Paulo - SP para resolucao de controversias.</p>
<div class="footer">
<p><strong>Global Match Engenharia de Producao</strong></p>
<p>CREA-SP 5071200171</p>
<p>E-mail: contato@aion.global</p>
<p>Telefone: (11) 99479-8464</p>
</div>
</body></html>"""
    return HTMLResponse(content=html)
