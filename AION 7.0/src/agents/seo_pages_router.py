import html as _html
import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/seo", tags=["seo_pages"])

# Static hand-written guide/comparison pages live under /ecosystem/callreception/
# (see global-match-site/.htaccess); combinatorial capability/regulation pages
# are served via the /artigos/{slug} reverse proxy. Shared by sitemap() and
# get_seo_page()'s canonical tag so both agree on the "real" URL for a slug.
_STATIC_KINDS = {"guide", "comparison"}


def _esc(s: str) -> str:
    return _html.escape(s or "", quote=True)


# Small reusable inline-SVG icon set, applied per section by category. Real
# per-page photography for ~1000 pages isn't feasible; these give each
# section real visual structure (not a wall of text) without downloading
# external images (copyright/untrusted-source risk) or hosting thousands of
# near-duplicate stock photos search engines would flag as thin anyway.
_ICONS = {
    "phone": '<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#00C36B" stroke-width="1.5"><path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.4 21 3 13.6 3 4.5c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.6.1.4 0 .8-.2 1z"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#00C36B" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>',
    "check": '<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#00C36B" stroke-width="1.5"><path d="M20 6L9 17l-5-5"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#00C36B" stroke-width="1.5"><path d="M4 20V10M12 20V4M20 20v-7"/></svg>',
    "building": '<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#00C36B" stroke-width="1.5"><rect x="4" y="3" width="16" height="18"/><path d="M9 8h1M14 8h1M9 12h1M14 12h1M9 16h1M14 16h1"/></svg>',
}


def _render_structured(data: dict, title: str, cta_link: str, cta_text: str, lang: str, related: list[dict]) -> str:
    is_pt = lang == "pt-BR"
    toc_labels = (
        ["Visão geral", "Como funciona", "Benefícios", "Comparativo", "Caso real", "Setores", "Perguntas frequentes"]
        if is_pt else
        ["Overview", "How it works", "Benefits", "Comparison", "Real example", "Industries", "FAQ"]
    )
    sections_html = []

    sections_html.append(
        '<nav class="toc"><strong>' + ("Nesta página" if is_pt else "On this page") + '</strong><ul>' +
        "".join(f'<li><a href="#s{i}">{_esc(lbl)}</a></li>' for i, lbl in enumerate(toc_labels)) +
        '</ul></nav>'
    )

    sections_html.append(f'<section id="s0"><p class="intro">{_esc(data["intro"])}</p></section>')

    steps = "".join(f'<div class="step"><span class="n">{i+1}</span><p>{_esc(s)}</p></div>' for i, s in enumerate(data["how_it_works"]))
    sections_html.append(f'<section id="s1"><h2>{"Como funciona" if is_pt else "How it works"}</h2><div class="icon">{_ICONS["clock"]}</div><div class="steps">{steps}</div></section>')

    benefits = "".join(f'<div class="benefit">{_ICONS["check"]}<h3>{_esc(b["title"])}</h3><p>{_esc(b["desc"])}</p></div>' for b in data["benefits"])
    sections_html.append(f'<section id="s2"><h2>{"Benefícios" if is_pt else "Benefits"}</h2><div class="benefits-grid">{benefits}</div></section>')

    rows = "".join(f'<tr><td>{_esc(c["criterion"])}</td><td>{_esc(c["human"])}</td><td class="ai-col">{_esc(c["ai"])}</td></tr>' for c in data["comparison"])
    head = ("Critério", "Atendimento manual", "AION Voice Receptionist") if is_pt else ("Criterion", "Manual handling", "AION Voice Receptionist")
    sections_html.append(
        f'<section id="s3"><h2>{"Comparativo" if is_pt else "Comparison"}</h2>'
        f'<div class="icon">{_ICONS["chart"]}</div>'
        f'<table class="cmp"><thead><tr><th>{head[0]}</th><th>{head[1]}</th><th>{head[2]}</th></tr></thead><tbody>{rows}</tbody></table></section>'
    )

    ex = data["real_example"]
    sections_html.append(
        f'<section id="s4"><h2>{"Caso real" if is_pt else "Real example"}</h2>'
        f'<div class="example"><div class="before"><strong>{"Antes" if is_pt else "Before"}</strong><p>{_esc(ex["before"])}</p></div>'
        f'<div class="after"><strong>{"Depois" if is_pt else "After"}</strong><p>{_esc(ex["after"])}</p></div>'
        f'<div class="result">{_esc(ex["result"])}</div></div></section>'
    )

    industries = "".join(f'<div class="industry-card">{_ICONS["building"]}<span>{_esc(ind)}</span></div>' for ind in data["industries"])
    sections_html.append(f'<section id="s5"><h2>{"Setores atendidos" if is_pt else "Industries"}</h2><div class="industries-grid">{industries}</div></section>')

    faq_items = data["faq"]
    faq_html = "".join(f'<details><summary>{_esc(f["q"])}</summary><p>{_esc(f["a"])}</p></details>' for f in faq_items)
    sections_html.append(f'<section id="s6"><h2>{"Perguntas frequentes" if is_pt else "Frequently Asked Questions"}</h2><div class="faq">{faq_html}</div></section>')

    if related:
        rel_html = "".join(f'<a class="related-card" href="/artigos/{_esc(r["slug"])}">{_esc(r["title"])}</a>' for r in related)
        sections_html.append(f'<section id="related"><h2>{"Artigos relacionados" if is_pt else "Related Articles"}</h2><div class="related-grid">{rel_html}</div></section>')

    faq_schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faq_items
        ],
    }
    article_schema = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": data["intro"][:200],
        "publisher": {"@type": "Organization", "name": "AION Voice Receptionist"},
    }
    schema_html = (
        f'<script type="application/ld+json">{json.dumps(faq_schema, ensure_ascii=False)}</script>'
        f'<script type="application/ld+json">{json.dumps(article_schema, ensure_ascii=False)}</script>'
    )

    hero = (
        f'<header class="hero"><div class="icon-lg">{_ICONS["phone"]}</div>'
        f'<h1>{_esc(title)}</h1>'
        f'<a href="{_esc(cta_link)}" class="cta">{_esc(cta_text)}</a></header>'
    )

    footer_cta = (
        f'<section class="footer-cta"><h2>{"Pare de perder ligações hoje" if is_pt else "Stop losing calls today"}</h2>'
        f'<a href="{_esc(cta_link)}" class="cta">{_esc(cta_text)}</a></section>'
    )

    return hero + "".join(sections_html) + footer_cta + schema_html


_PREMIUM_CSS = """
body{font-family:-apple-system,Segoe UI,sans-serif;background:#0C1322;color:#e2e8f0;margin:0;line-height:1.6}
.hero{text-align:center;padding:64px 24px 40px;background:linear-gradient(180deg,#111a2e,#0C1322)}
.hero h1{color:#fff;font-size:2rem;max-width:760px;margin:16px auto}
.icon-lg svg{width:64px;height:64px}
.cta{display:inline-block;background:#00C36B;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:700;margin-top:20px}
.toc{max-width:720px;margin:0 auto;padding:20px 24px;background:#111a2e;border-radius:12px}
.toc ul{display:flex;flex-wrap:wrap;gap:8px 16px;list-style:none;padding:8px 0 0;margin:0}
.toc a{color:#00C36B;text-decoration:none;font-size:.9rem}
section{max-width:760px;margin:40px auto;padding:0 24px}
h2{color:#00C36B;font-size:1.4rem}
.intro{font-size:1.05rem;color:#cbd5e1}
.steps{display:flex;flex-direction:column;gap:14px;margin-top:16px}
.step{display:flex;gap:14px;align-items:flex-start;background:#111a2e;padding:14px 18px;border-radius:10px}
.step .n{background:#00C36B;color:#0C1322;font-weight:700;border-radius:50%;width:28px;height:28px;flex:none;display:flex;align-items:center;justify-content:center}
.benefits-grid,.industries-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-top:16px}
.benefit,.industry-card{background:#111a2e;padding:18px;border-radius:10px}
.benefit svg,.industry-card svg{width:28px;height:28px}
.industry-card{display:flex;align-items:center;gap:10px;font-weight:600}
table.cmp{width:100%;border-collapse:collapse;margin-top:16px;background:#111a2e;border-radius:10px;overflow:hidden}
table.cmp th,table.cmp td{padding:12px 16px;text-align:left;border-bottom:1px solid #1e293b}
table.cmp .ai-col{color:#00C36B;font-weight:600}
.example{background:#111a2e;border-radius:12px;padding:20px;margin-top:16px;display:grid;gap:12px}
.example .result{background:#00C36B22;color:#00C36B;padding:10px 14px;border-radius:8px;font-weight:700}
.faq details{background:#111a2e;border-radius:10px;padding:14px 18px;margin-bottom:10px}
.faq summary{cursor:pointer;font-weight:600;color:#fff}
.faq p{color:#cbd5e1;margin-top:10px}
.related-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:16px}
.related-card{background:#111a2e;color:#e2e8f0;padding:14px 18px;border-radius:10px;text-decoration:none;font-size:.9rem}
.footer-cta{text-align:center;background:#111a2e;padding:48px 24px;margin-top:60px}
"""


@router.get("/page/{slug}")
async def get_seo_page(slug: str):
    import os, httpx
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not supa_url or not supa_key:
        return HTMLResponse(content="<h1>Service unavailable</h1>", status_code=503)
    try:
        headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}
        r = httpx.get(
            supa_url + "/rest/v1/seo_pages?slug=eq." + slug + "&published=eq.true&select=*",
            headers=headers, timeout=10,
        )
        if r.status_code != 200 or not r.json():
            return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)
        page = r.json()[0]
    except Exception:
        return HTMLResponse(content="<h1>Error loading page</h1>", status_code=500)

    title = page.get("title", slug)
    meta_desc = page.get("meta_description", "")
    body_raw = page.get("body", "")
    link = page.get("stripe_link", "") or "https://global-engenharia.com/vendas.html"
    market = (page.get("market") or "").upper()
    # Static hand-written guide/comparison pages (aion-vs-retell-ai.html etc.)
    # are the real canonical URL under /ecosystem/callreception/ (see
    # sitemap() below, which already routes these there). This dynamic
    # /api/seo/page/{slug} render of the same slug is a secondary/duplicate
    # copy -- self-canonicalizing it to /artigos/{slug} told crawlers it was
    # the authoritative version, producing a canonical that pointed away from
    # the actual indexed URL (Semrush "broken canonical links" finding,
    # confirmed 2026-07-19 for vs-retell-ai, vs-synthflow, etc).
    canonical_path = "/ecosystem/callreception/" if page.get("topic_kind") in _STATIC_KINDS else "/artigos/"
    lang = "pt-BR" if market == "BR" else "en"
    cta_text = "🚀 Comece o teste gratuito" if lang == "pt-BR" else "🚀 Start free trial"

    related: list[dict] = []
    try:
        rr = httpx.get(
            supa_url + f"/rest/v1/seo_pages?market=eq.{market}&slug=neq.{slug}&published=eq.true"
            f"&select=slug,title&limit=4",
            headers=headers, timeout=8,
        )
        if rr.status_code == 200:
            related = rr.json() or []
    except Exception:
        related = []

    try:
        structured = json.loads(body_raw)
        if not isinstance(structured, dict) or "faq" not in structured:
            raise ValueError("not structured")
        content_html = _render_structured(structured, title, link, cta_text, lang, related)
    except (json.JSONDecodeError, ValueError, TypeError, KeyError):
        # Legacy plain-text page (pre 2026-07-19 template) -- render as-is
        # until the next generation batch upgrades it.
        content_html = (
            f'<header class="hero"><h1>{_esc(title)}</h1></header>'
            f'<section><div>{body_raw}</div>'
            f'<a href="{_esc(link)}" class="cta">{_esc(cta_text)}</a></section>'
        )

    html = (
        '<!DOCTYPE html><html lang="' + lang + '"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<title>' + _esc(title) + ' | AION</title>'
        '<meta name="description" content="' + _esc(meta_desc) + '">'
        '<meta name="robots" content="index,follow">'
        '<link rel="canonical" href="https://global-engenharia.com' + canonical_path + _esc(slug) + '">'
        '<style>' + _PREMIUM_CSS + '</style>'
        '</head><body>' + content_html + '</body></html>'
    )
    return HTMLResponse(content=html)


# Real ISO hreflang codes for the 4 validated markets -- used to tell Google
# "these N URLs are equivalent content for different countries" without
# moving a single existing URL (the slugs/paths never change).
_HREFLANG_BY_MARKET = {"US": "en-us", "UK": "en-gb", "CA": "en-ca", "AU": "en-au"}


def _cluster_key(slug: str, market: str) -> str | None:
    """Strip the leading market prefix from a combinatorial slug (format
    '{market}-{topic}-{sector}-{size}') so pages sharing the same
    topic+sector+size across markets can be grouped for hreflang. Returns
    None for slugs that don't start with their own market prefix (static
    guide/comparison pages, legacy rows) -- those get no hreflang cluster."""
    prefix = market.lower() + "-"
    if not slug.startswith(prefix):
        return None
    return slug[len(prefix):]


def _sitemap_xml(pages: list[dict], market_filter: str | None = None) -> str:
    # Build hreflang clusters first: cluster_key -> {market: slug}
    clusters: dict[str, dict[str, str]] = {}
    for p in pages or []:
        if p.get("topic_kind") in _STATIC_KINDS:
            continue
        m = (p.get("market") or "").upper()
        key = _cluster_key(p["slug"], m)
        if key is None or m not in _HREFLANG_BY_MARKET:
            continue
        clusters.setdefault(key, {})[m] = p["slug"]

    items = []
    for p in pages or []:
        m = (p.get("market") or "").upper()
        if market_filter and m != market_filter:
            continue
        base = "/ecosystem/callreception/" if p.get("topic_kind") in _STATIC_KINDS else "/artigos/"
        loc = "https://global-engenharia.com" + base + p["slug"]
        alt_links = ""
        key = _cluster_key(p["slug"], m) if p.get("topic_kind") not in _STATIC_KINDS else None
        variants = clusters.get(key) if key else None
        if variants and len(variants) > 1:
            alt_links = "".join(
                f'<xhtml:link rel="alternate" hreflang="{hl}" href="https://global-engenharia.com/artigos/{v_slug}" />'
                for v_market, v_slug in variants.items()
                if (hl := _HREFLANG_BY_MARKET.get(v_market))
            )
        items.append(f'  <url><loc>{loc}</loc>{alt_links}<changefreq>monthly</changefreq><priority>0.7</priority></url>')
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(items) + "\n</urlset>"
    )


async def _fetch_seo_pages():
    import os, httpx
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not supa_url or not supa_key:
        return None
    headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}
    # PostgREST caps a response at 1000 rows by default. With 1141+ published
    # pages, an unpaginated fetch here silently dropped ~140 pages from every
    # sitemap (main + all 4 per-country) -- confirmed 2026-07-21 via direct
    # Supabase count (US/UK/CA/AU sum to 1134, but the site's sitemaps only
    # showed 993-1058). Page through with Range until a partial page confirms
    # the end.
    all_rows: list[dict] = []
    page_size = 1000
    offset = 0
    while True:
        r = httpx.get(
            supa_url + "/rest/v1/seo_pages?select=slug,market,topic_kind&published=eq.true",
            headers={**headers, "Range-Unit": "items", "Range": f"{offset}-{offset + page_size - 1}"},
            timeout=15,
        )
        batch = r.json()
        if not isinstance(batch, list) or not batch:
            break
        all_rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    return all_rows


@router.get("/sitemap.xml")
async def sitemap():
    try:
        pages = await _fetch_seo_pages()
    except Exception:
        return HTMLResponse(content="", status_code=500)
    if pages is None:
        return HTMLResponse(content="", status_code=503)
    return HTMLResponse(content=_sitemap_xml(pages), media_type="application/xml")


@router.get("/sitemap-{market}.xml")
async def sitemap_by_market(market: str):
    """Per-country sitemap (sitemap-us.xml, sitemap-uk.xml, sitemap-ca.xml,
    sitemap-au.xml) -- same page set as sitemap.xml, filtered to one market,
    for separate GSC/Ads-per-country submission without any URL migration."""
    market = market.upper()
    if market not in _HREFLANG_BY_MARKET:
        return HTMLResponse(content="Unknown market", status_code=404)
    try:
        pages = await _fetch_seo_pages()
    except Exception:
        return HTMLResponse(content="", status_code=500)
    if pages is None:
        return HTMLResponse(content="", status_code=503)
    return HTMLResponse(content=_sitemap_xml(pages, market_filter=market), media_type="application/xml")


@router.delete("/legacy-pages")
async def cleanup_legacy_pages():
    """One-time cleanup: removes seo_pages rows from the retired 19-Copilot
    compliance catalog (product IS NULL) that pre-date the 2026-07 Voice
    Receptionist pivot — never deleted, still polluting the sitemap with
    irrelevant BR compliance slugs. Counts before deleting; safe to retry
    (matches 0 rows once cleaned)."""
    import os, httpx
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not supa_url or not supa_key:
        return {"error": "Supabase not configured"}
    headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}
    # product IS NULL (never tagged) OR product != voice_receptionist (tagged
    # with a now-retired product) -- the first attempt only matched IS NULL
    # and found 0 rows, meaning these legacy rows carry a stale non-null
    # product value instead.
    filter_q = "or=(product.is.null,product.neq.voice_receptionist)"
    count_r = httpx.get(
        supa_url + f"/rest/v1/seo_pages?{filter_q}&select=slug",
        headers=headers, timeout=15,
    )
    slugs = [row["slug"] for row in count_r.json()] if count_r.status_code == 200 else []
    if not slugs:
        return {"deleted": 0, "message": "No legacy rows found"}
    del_r = httpx.delete(
        supa_url + f"/rest/v1/seo_pages?{filter_q}",
        headers=headers, timeout=30,
    )
    return {"found": len(slugs), "delete_status_code": del_r.status_code, "sample_slugs": slugs[:5]}
