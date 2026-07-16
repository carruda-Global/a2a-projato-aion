from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/seo", tags=["seo_pages"])


@router.get("/page/{slug}")
async def get_seo_page(slug: str):
    import os, httpx
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not supa_url or not supa_key:
        return HTMLResponse(content="<h1>Service unavailable</h1>", status_code=503)
    try:
        headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}
        r = httpx.get(supa_url + "/rest/v1/seo_pages?slug=eq." + slug + "&select=*", headers=headers, timeout=10)
        if r.status_code != 200 or not r.json():
            return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)
        page = r.json()[0]
    except Exception as e:
        return HTMLResponse(content="<h1>Error loading page</h1>", status_code=500)
    title = page.get("title", slug)
    meta_desc = page.get("meta_description", "")
    body = page.get("body", "")
    link = page.get("stripe_link", "")
    market = (page.get("market") or "").upper()
    lang = "pt-BR" if market == "BR" else "en"
    cta_text = "🚀 Comece o teste gratuito" if lang == "pt-BR" else "🚀 Start free trial"
    html = (
        '<!DOCTYPE html><html lang="' + lang + '"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<title>' + title + ' | AION Voice Receptionist</title>'
        '<meta name="description" content="' + meta_desc + '">'
        '<meta name="robots" content="index,follow">'
        '<style>body{font-family:sans-serif;background:#0C1322;color:#e2e8f0;padding:40px 24px}'
        'h1{color:#00C36B}.cta{display:inline-block;background:#00C36B;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:700;margin-top:20px}</style>'
        '</head><body><h1>' + title + '</h1><div>' + body + '</div>'
        '<a href="' + link + '" class="cta">' + cta_text + '</a>'
        '</body></html>'
    )
    return HTMLResponse(content=html)


@router.get("/sitemap.xml")
async def sitemap():
    import os, httpx
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not supa_url or not supa_key:
        return HTMLResponse(content="", status_code=503)
    try:
        headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}
        r = httpx.get(supa_url + "/rest/v1/seo_pages?select=slug,market,topic_kind&published=eq.true", headers=headers, timeout=10)
        pages = r.json()
    except:
        return HTMLResponse(content="", status_code=500)
    # Static hand-written guide/comparison pages live under /ecosystem/callreception/
    # (see global-match-site/.htaccess); combinatorial capability/regulation pages
    # are served via the /artigos/{slug} reverse proxy. Both were emitted as
    # /artigos/ previously, which 404'd the 4 static pages in any real crawl.
    STATIC_KINDS = {"guide", "comparison"}
    items = []
    for p in pages or []:
        base = "/ecosystem/callreception/" if p.get("topic_kind") in STATIC_KINDS else "/artigos/"
        items.append('  <url><loc>https://global-engenharia.com' + base + p["slug"] + '</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(items) + "\n</urlset>"
    return HTMLResponse(content=xml, media_type="application/xml")


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
    count_r = httpx.get(
        supa_url + "/rest/v1/seo_pages?product=is.null&select=slug",
        headers=headers, timeout=15,
    )
    slugs = [row["slug"] for row in count_r.json()] if count_r.status_code == 200 else []
    if not slugs:
        return {"deleted": 0, "message": "No legacy rows found"}
    del_r = httpx.delete(
        supa_url + "/rest/v1/seo_pages?product=is.null",
        headers=headers, timeout=30,
    )
    return {"found": len(slugs), "delete_status_code": del_r.status_code, "sample_slugs": slugs[:5]}
