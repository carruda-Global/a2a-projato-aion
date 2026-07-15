import asyncio
import itertools
import logging
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.database.supabase_client import SupabaseClient

router = APIRouter(prefix="/pmoc", tags=["pmoc_seo"])
logger = logging.getLogger(__name__)


def _db() -> SupabaseClient:
    return SupabaseClient(Settings())


def _get_page(slug: str) -> str | None:
    r = _db().client.table("pmoc_pages").select("html").eq("slug", slug).execute()
    return r.data[0]["html"] if r.data else None


def _existing_slugs() -> set[str]:
    r = _db().client.table("pmoc_pages").select("slug").execute()
    return {row["slug"] for row in (r.data or [])}


def _save_page(slug: str, batch: str, html: str) -> None:
    _db().client.table("pmoc_pages").upsert({"slug": slug, "batch": batch, "html": html}).execute()

# 30 bairros/regiões SP com maior volume de buscas por PMOC
BAIRROS_SP = [
    "Itaim Bibi", "Vila Olímpia", "Brooklin", "Moema", "Pinheiros",
    "Jardins", "Paulista", "Faria Lima", "Berrini", "Santo André",
    "São Bernardo do Campo", "Guarulhos", "Osasco", "Alphaville", "Barueri",
    "Tatuapé", "Mooca", "Lapa", "Santana", "Perdizes",
    "Vila Mariana", "Saúde", "Ipiranga", "Jabaquara", "Santo Amaro",
    "Campo Belo", "Morumbi", "Butantã", "Jaguaré", "Penha",
]

# 20 tipos de empresa obrigados ao PMOC
TIPOS_EMPRESA = [
    "hospital", "clínica médica", "escola", "universidade", "shopping",
    "supermercado", "restaurante", "hotel", "academia de ginástica", "farmácia",
    "banco", "escritório corporativo", "condomínio comercial", "laboratório",
    "indústria", "data center", "clínica odontológica", "spa", "salão de beleza",
    "coworking",
]

# Keywords de problema/intenção — vindas do Relatório de palavras-chave da
# rede de pesquisa real (Google Ads, 16/mai-04/jul/2026), ordenadas por
# impressões reais (não estimativa).
PROBLEMAS = [
    "PMOC", "laudo PMOC", "orçamento laudo tecnico", "laudo ar condicionado",
    "PMOC ar condicionado", "laudo tecnico ar condicionado", "validade do PMOC",
    "laudo tecnico PMOC", "laudo de instalação de ar condicionado",
    "vistoria ar condicionado", "plano de manutenção operação e controle",
    "PMOC ANVISA", "engenheiro CREA SP", "PMOC empresa", "PMOC ART",
    "PMOC quanto custa", "fazer PMOC", "PMOC obrigatorio", "PMOC tem validade",
    "renovação PMOC",
]

# Top temas reais (mesma fonte) usados no batch keyword_bairro — cruza
# demanda comprovada (Ads) com localidade para long-tail hiperlocal.
KEYWORDS_TOP_REAIS = [
    "laudo PMOC", "PMOC ar condicionado", "vistoria ar condicionado",
    "laudo ar condicionado", "laudo tecnico ar condicionado",
    "validade do PMOC", "orçamento PMOC", "PMOC obrigatorio",
]

GTM_SCRIPT = """
<!-- Google Tag Manager + Ads -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-KHQR6DKH');</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18167532524"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','AW-18167532524');gtag('config','G-M26TGHRFK7');gtag('config','GT-PHRGNM2W');</script>
"""

GTM_NOSCRIPT = """<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KHQR6DKH" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>"""

WHATSAPP_NUMBER = "5511994798464"


def _build_page(slug: str, title: str, h1: str, desc: str, body_html: str, keyword: str) -> str:
    wpp_msg = f"Olá! Preciso de PMOC para {keyword}. Podem me orçar?"
    wpp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={wpp_msg.replace(' ', '%20')}"
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://global-engenharia.com/pmoc/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://global-engenharia.com/pmoc/{slug}">
<meta property="og:image" content="https://global-engenharia.com/assets/pmoc-conforme.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
{GTM_SCRIPT}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,sans-serif;color:#1a1a2e;background:#fff;line-height:1.7}}
header{{background:#0f3460;color:#fff;padding:16px 24px;display:flex;justify-content:space-between;align-items:center}}
header a{{color:#fff;text-decoration:none;font-weight:600;font-size:14px}}
.hero{{background:#e8f4fd;padding:48px 24px;text-align:center}}
.hero h1{{font-size:clamp(22px,4vw,36px);font-weight:700;color:#0f3460;margin-bottom:12px}}
.hero p{{font-size:16px;color:#444;max-width:600px;margin:0 auto 24px}}
.cta-btn{{display:inline-block;background:#25d366;color:#fff;padding:14px 32px;border-radius:8px;font-size:16px;font-weight:700;text-decoration:none;margin:4px}}
.cta-btn.sec{{background:#0f3460}}
.badges{{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:16px;font-size:13px;color:#555}}
.badge{{background:#fff;border:1px solid #ddd;border-radius:20px;padding:4px 12px}}
.content{{max-width:800px;margin:0 auto;padding:40px 24px}}
.content h2{{font-size:22px;font-weight:700;color:#0f3460;margin:32px 0 12px}}
.content p{{margin-bottom:14px;color:#333}}
.content ul{{padding-left:20px;margin-bottom:14px}}
.content li{{margin-bottom:6px;color:#333}}
.planos{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:24px 0}}
.plano{{border:2px solid #e0e0e0;border-radius:10px;padding:20px;text-align:center}}
.plano.destaque{{border-color:#0f3460;background:#f0f7ff}}
.plano h3{{font-size:16px;font-weight:700;margin-bottom:8px}}
.plano .price{{font-size:28px;font-weight:800;color:#0f3460}}
.plano ul{{text-align:left;margin:12px 0;font-size:13px}}
.faq{{background:#f8f9fa;padding:24px;border-radius:10px;margin:24px 0}}
.faq h3{{font-size:18px;font-weight:700;margin-bottom:16px}}
.faq-item{{margin-bottom:16px}}
.faq-item strong{{display:block;margin-bottom:4px;color:#0f3460}}
footer{{background:#0f3460;color:#ccc;padding:24px;text-align:center;font-size:13px;margin-top:40px}}
footer a{{color:#fff}}
.wpp-float{{position:fixed;bottom:20px;right:20px;background:#25d366;color:#fff;border-radius:50px;padding:12px 20px;font-weight:700;text-decoration:none;font-size:14px;box-shadow:0 4px 12px rgba(0,0,0,.3);z-index:999}}
</style>
</head>
<body>
{GTM_NOSCRIPT}
<header>
  <a href="https://global-engenharia.com">Global Match Engenharia</a>
  <a href="{wpp_url}" target="_blank">📱 Orçamento WhatsApp</a>
</header>

<div class="hero">
  <h1>{h1}</h1>
  <p>{desc}</p>
  <a href="{wpp_url}" target="_blank" class="cta-btn">💬 Orçamento no WhatsApp</a>
  <a href="tel:+5511994798464" class="cta-btn sec">📞 Ligar Agora</a>
  <div class="badges">
    <span class="badge">✓ ART CREA-SP</span>
    <span class="badge">✓ Entrega em 15 dias</span>
    <span class="badge">✓ +500 empresas atendidas</span>
    <span class="badge">✓ CREA 5071200171</span>
  </div>
</div>

<div class="content">
{body_html}

<h2>Nossos Planos</h2>
<div class="planos">
  <div class="plano">
    <h3>Essencial</h3>
    <div class="price">R$ 890</div>
    <ul><li>1 a 4 equipamentos</li><li>PMOC completo</li><li>ART CREA-SP</li><li>Livro Técnico digital</li></ul>
    <a href="{wpp_url}" target="_blank" class="cta-btn" style="font-size:13px;padding:10px 16px">Solicitar</a>
  </div>
  <div class="plano destaque">
    <h3>⭐ Completo</h3>
    <div class="price">R$ 1.490</div>
    <ul><li>5 a 8 equipamentos</li><li>PMOC + ART</li><li>Laudo de Conformidade</li><li>Relatório fotográfico</li><li>Certificado</li></ul>
    <a href="{wpp_url}" target="_blank" class="cta-btn" style="font-size:13px;padding:10px 16px">Solicitar</a>
  </div>
  <div class="plano">
    <h3>Premium</h3>
    <div class="price">R$ 3.490</div>
    <ul><li>Acima de 9 equipamentos</li><li>Tudo do Completo</li><li>Suporte 12 meses</li><li>Renovação ART inclusa</li></ul>
    <a href="{wpp_url}" target="_blank" class="cta-btn" style="font-size:13px;padding:10px 16px">Solicitar</a>
  </div>
</div>

<div class="faq">
  <h3>Perguntas Frequentes</h3>
  <div class="faq-item"><strong>O PMOC é obrigatório para minha empresa?</strong>Sim, pela Portaria MS 3.523/98, qualquer ambiente com sistema de ar condicionado central ou unitário acima de 5 TR precisa de PMOC com ART.</div>
  <div class="faq-item"><strong>Qual a multa por não ter PMOC?</strong>A Vigilância Sanitária pode aplicar multas de R$ 2.000 a R$ 1,5 milhão pela Lei 6.437/77, além de interdição do estabelecimento.</div>
  <div class="faq-item"><strong>Em quanto tempo recebo o PMOC?</strong>Entregamos em até 15 dias úteis após vistoria técnica. Em casos urgentes, temos atendimento prioritário em 7 dias.</div>
  <div class="faq-item"><strong>Vocês emitem ART CREA-SP?</strong>Sim. Todos os serviços incluem ART assinada pelo Eng. Cristiano Arruda, CREA-SP 5071200171.</div>
</div>

<p style="text-align:center;margin-top:32px">
  <strong>Dúvidas? Fale conosco agora:</strong><br>
  <a href="{wpp_url}" target="_blank" class="cta-btn" style="margin-top:12px;display:inline-block">💬 WhatsApp: (11) 99479-8464</a>
</p>
</div>

<footer>
  <p>Global Match Engenharia de Produção — CREA-SP 5071200171</p>
  <p>Rua Monteiro Soares Filho, 552 — São Paulo/SP — CEP 03141-010</p>
  <p><a href="https://global-engenharia.com">global-engenharia.com</a> | contato@global-engenharia.com | (11) 99479-8464</p>
</footer>

<a href="{wpp_url}" target="_blank" class="wpp-float">💬 WhatsApp</a>

<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Service","name":"{h1}","provider":{{"@type":"ProfessionalService","name":"Global Match Engenharia","telephone":"+5511994798464","url":"https://global-engenharia.com","address":{{"@type":"PostalAddress","addressLocality":"São Paulo","addressRegion":"SP","addressCountry":"BR"}}}},"areaServed":{{"@type":"City","name":"São Paulo"}},"description":"{desc}"}}
</script>
</body>
</html>"""


async def _generate_body(keyword: str, context: str) -> str:
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    system = "Você é um especialista em PMOC (Plano de Manutenção, Operação e Controle de ar condicionado) conforme Portaria MS 3.523/98. Escreva conteúdo técnico e persuasivo em português para página de serviço."
    prompt = f"""Escreva 4 parágrafos HTML (usando <h2> e <p>) sobre PMOC para: {keyword}
Contexto adicional: {context}
Inclua: obrigatoriedade legal, riscos de não ter, processo de elaboração, diferenciais da Global Match Engenharia.
Use termos técnicos: Portaria 3.523/98, ART CREA-SP, ANVISA, Vigilância Sanitária.
Retorne apenas o HTML, sem explicação."""
    return await asyncio.to_thread(deepseek.chat, system, prompt)


async def generate_pmoc_pages(batch: str = "bairros", count: int = 10) -> dict:
    """Gera paginas SEO para PMOC. batch = bairros | empresas | problemas.
    Persiste no Supabase (pmoc_pages) e pula slugs ja existentes — sobrevive
    a restart do servico e para de reescrever o mesmo conteudo a cada ciclo."""
    existing = _existing_slugs()
    generated = []
    skipped = 0

    if batch == "bairros":
        items = BAIRROS_SP[:count]
        for bairro in items:
            slug = f"pmoc-{bairro.lower().replace(' ', '-').replace('/', '-')}-sp"
            if slug in existing:
                skipped += 1
                continue
            keyword = f"{bairro} SP"
            title = f"PMOC {bairro} SP — ART CREA-SP + Laudo | Global Match Engenharia"
            h1 = f"PMOC Executivo em {bairro} — São Paulo"
            desc = f"PMOC em {bairro} com ART CREA-SP, laudo fotográfico e relatório técnico. A partir de R$890. Entrega em 15 dias. Eng. responsável CREA 5071200171."
            body = await _generate_body(keyword, f"empresa localizada em {bairro}, São Paulo")
            page = _build_page(slug, title, h1, desc, body, keyword)
            _save_page(slug, batch, page)
            generated.append({"slug": slug, "title": title})
            logger.info("[PMOC-SEO] Gerado: %s", slug)
            await asyncio.sleep(2)

    elif batch == "empresas":
        items = TIPOS_EMPRESA[:count]
        for tipo in items:
            slug = f"pmoc-{tipo.lower().replace(' ', '-').replace('/', '-')}"
            if slug in existing:
                skipped += 1
                continue
            keyword = tipo
            title = f"PMOC para {tipo.title()} em SP — Obrigatório pela Portaria 3.523/98"
            h1 = f"PMOC para {tipo.title()} — São Paulo"
            desc = f"PMOC executivo para {tipo} em SP. Obrigatório pela Portaria 3.523/98. ART CREA-SP, laudo e certificado. Orçamento em 24h."
            body = await _generate_body(keyword, f"estabelecimento do tipo {tipo}")
            page = _build_page(slug, title, h1, desc, body, keyword)
            _save_page(slug, batch, page)
            generated.append({"slug": slug, "title": title})
            logger.info("[PMOC-SEO] Gerado: %s", slug)
            await asyncio.sleep(2)

    elif batch == "problemas":
        items = PROBLEMAS[:count]
        for prob in items:
            slug = prob.lower().replace(' ', '-').replace('/', '-').replace(',', '')
            if slug in existing:
                skipped += 1
                continue
            keyword = prob
            title = f"{prob.title()} em SP — Regularize com Global Match Engenharia"
            h1 = f"{prob.title()} — Solução Rápida em São Paulo"
            desc = f"Resolva {prob.lower()} em SP com a Global Match Engenharia. ART CREA-SP, entrega em 15 dias. +500 empresas atendidas. Orçamento gratuito."
            body = await _generate_body(keyword, f"cliente com problema: {prob}")
            page = _build_page(slug, title, h1, desc, body, keyword)
            _save_page(slug, batch, page)
            generated.append({"slug": slug, "title": title})
            logger.info("[PMOC-SEO] Gerado: %s", slug)
            await asyncio.sleep(2)

    elif batch == "keyword_bairro":
        # Cruza os temas de maior busca real (Ads) com bairro — long-tail
        # hiperlocal apoiado em demanda comprovada, não em keyword inventada.
        pairs = list(itertools.product(KEYWORDS_TOP_REAIS, BAIRROS_SP))[:count]
        for kw, bairro in pairs:
            kw_slug = kw.lower().replace(' ', '-').replace('/', '-')
            bairro_slug = bairro.lower().replace(' ', '-').replace('/', '-')
            slug = f"{kw_slug}-{bairro_slug}-sp"
            if slug in existing:
                skipped += 1
                continue
            keyword = f"{kw} em {bairro}"
            title = f"{kw.title()} em {bairro} SP — Global Match Engenharia"
            h1 = f"{kw.title()} — {bairro}, São Paulo"
            desc = f"{kw.title()} em {bairro}/SP com ART CREA-SP. Entrega em 15 dias. Eng. responsável CREA 5071200171."
            body = await _generate_body(keyword, f"empresa em {bairro}, São Paulo, buscando \"{kw}\"")
            page = _build_page(slug, title, h1, desc, body, keyword)
            _save_page(slug, batch, page)
            generated.append({"slug": slug, "title": title})
            logger.info("[PMOC-SEO] Gerado: %s", slug)
            await asyncio.sleep(2)

    return {"batch": batch, "generated": len(generated), "skipped": skipped, "slugs": [p["slug"] for p in generated]}


# ── Routes ────────────────────────────────────────────────────────────────────

def _find_batch_for_slug(slug: str) -> tuple[str, int] | None:
    """Locates which batch+index a slug belongs to, for on-demand generation
    of exactly that page (not just whatever is first in the batch)."""
    for batch, items, prefix, suffix in [
        ("bairros", BAIRROS_SP, "pmoc-", "-sp"),
        ("empresas", TIPOS_EMPRESA, "pmoc-", ""),
        ("problemas", PROBLEMAS, "", ""),
    ]:
        for i, item in enumerate(items):
            s = item.lower().replace(" ", "-").replace("/", "-").replace(",", "")
            if f"{prefix}{s}{suffix}" == slug:
                return batch, i

    pairs = list(itertools.product(KEYWORDS_TOP_REAIS, BAIRROS_SP))
    for i, (kw, bairro) in enumerate(pairs):
        kw_slug = kw.lower().replace(" ", "-").replace("/", "-")
        bairro_slug = bairro.lower().replace(" ", "-").replace("/", "-")
        if f"{kw_slug}-{bairro_slug}-sp" == slug:
            return "keyword_bairro", i
    return None


_BATCH_TOTAL_LEN = {
    "bairros": len(BAIRROS_SP),
    "empresas": len(TIPOS_EMPRESA),
    "problemas": len(PROBLEMAS),
    "keyword_bairro": len(KEYWORDS_TOP_REAIS) * len(BAIRROS_SP),
}


@router.get("/{slug}", response_class=HTMLResponse)
async def serve_page(slug: str):
    """Serve página PMOC — busca no banco (persistente), gera sob demanda
    se ainda não existir."""
    from fastapi import HTTPException
    html = await asyncio.to_thread(_get_page, slug)
    if html:
        return HTMLResponse(content=html)

    location = _find_batch_for_slug(slug)
    if location:
        batch, index = location
        # Gera só o item pedido: fatia ate index+1 e usa existing_slugs pra
        # pular os anteriores que ja estao no banco.
        original_len = _BATCH_TOTAL_LEN[batch]
        await generate_pmoc_pages(batch, min(index + 1, original_len))
        html = await asyncio.to_thread(_get_page, slug)
        if html:
            return HTMLResponse(content=html)
    raise HTTPException(status_code=404, detail="Página não encontrada")


@router.get("/sitemap.xml")
async def sitemap():
    from fastapi.responses import Response
    r = await asyncio.to_thread(lambda: _db().client.table("pmoc_pages").select("slug").execute())
    urls = [row["slug"] for row in (r.data or [])]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '  <url><loc>https://global-engenharia.com</loc><priority>1.0</priority></url>\n'
    for slug in urls:
        xml += f'  <url><loc>https://global-engenharia.com/pmoc/{slug}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
    xml += '</urlset>'
    return Response(content=xml, media_type="application/xml")

@router.get("/api/bairros")
async def list_bairros():
    return {"bairros": BAIRROS_SP, "total": len(BAIRROS_SP)}

@router.get("/api/empresas")
async def list_empresas():
    return {"tipos": TIPOS_EMPRESA, "total": len(TIPOS_EMPRESA)}

@router.get("/api/problemas")
async def list_problemas():
    return {"problemas": PROBLEMAS, "total": len(PROBLEMAS)}

@router.get("/api/cache-status")
async def cache_status():
    r = await asyncio.to_thread(lambda: _db().client.table("pmoc_pages").select("slug").execute())
    slugs = [row["slug"] for row in (r.data or [])]
    return {"pages_cached": len(slugs), "slugs": slugs}
