---
name: seo-voice-receptionist
description: Use for any SEO work on the AION Voice Receptionist product (global-engenharia.com) — adding topics/keywords, checking status, blog posts, backlinks, sitemap.
---

# SEO system — AION Voice Receptionist

## Architecture (AION 7.0 backend)
- `src/agents/seo_topics.py` — topic catalog (CAPABILITY_TOPICS × SECTORS_BY_REGION × SIZES_BY_REGION, markets US/UK/CA/AU). Add new real buyer-question topics here.
- `src/agents/seo_content_agent.py` — generates one real LLM page per topic×sector×size combo (dedup + length-floor gate). Trigger: `POST /api/seo/generate/{market}?limit=N` (batch — a single unbounded call 502s on Render's proxy timeout; batch at ~20-25/call). Cron: every 6h, all 4 markets, in `app/main.py`.
- `src/agents/seo_pages_router.py` — serves generated pages + `/sitemap.xml` (merges static hand-written page list + dynamic Supabase `seo_pages` rows).
- `src/agents/directory_submission_agent.py` — backlink/directory outreach emails. `DIRECTORIES` list = targets. Cron: daily, 10/run. Manual trigger: `POST /api/directories/run-now`. **Never add PBN/link-farm/mass-link-buying domains** — real self-serve directories only.
- `src/agents/seo_orchestrator_agent.py` — unified status: `GET /api/seo/agent/status` (page counts by market, recent directory sends, cron schedule).
- `src/agents/seo_feedback_agent.py` — GSC performance, weekly, no-ops without `GSC_*` env vars.

## Site (global-match-site, deployed via `python deploy_ftp.py`)
- `blog/` — hand-written posts (7 so far), footer links to all comparison/vertical pages, `sitemap.php` static list, `.htaccess` pretty-URL rules — all three must be updated together for a new page.
- Root domain (`index.html`) = Voice Receptionist (mirror of `vendas.html`). `/ecosystem` (bare) = PMOC (`pmoc.html`), `/ecosystem/callreception/*` = Voice Receptionist. Keep `vendas.html` filename stable — ~20 files link to it directly.
- FAQPage schema on `vendas.html` + each blog post with Q&A content.

## CRITICAL gotcha: two git remotes for the backend
`origin` (a2a-projato-aion.git) is NOT what Render deploys. Render's `render.yaml` points at `github.com/carruda-Global/engenheiro-producao-ai.git` (remote name `render-deploy` once added). **Every backend commit needs pushing to both** or changes silently never go live:
```
git push origin main
git checkout render-deploy-sync && git cherry-pick <sha> && git push render-deploy render-deploy-sync:main && git checkout main
```
Both branches share history but differ in root-path nesting for new-file adds (origin nests under `AION 7.0/`) — a cherry-pick conflict on a brand-new file is normal; resolve by `git add` the file at its render-deploy-relative path and `git cherry-pick --continue`.

## GEO/AEO (AI search, 2026-07-16 addition)
- `llms.txt` at site root — curated links for AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended; robots.txt already allows all, `Allow: /`).
- `Organization` + `Product`/`Offer` schema on `vendas.html`/`index.html` (alongside FAQPage).
- Pillar page `ai-receptionist-guide.html` — hub linking the full content cluster (must update when new blog/comparison pages are added).
- Keep `llms.txt` and the pillar page's link list in sync whenever a new page is added to the site.

## When asked to "expand SEO" / add keywords
1. Add topics to `seo_topics.py` (real search-validated questions only, not invented).
2. Push to both remotes (see above).
3. Batch-trigger `/api/seo/generate/{market}?limit=25` a few times per market, or just wait for the 6h cron.
4. Check `GET /api/seo/agent/status` for real counts before reporting progress.
