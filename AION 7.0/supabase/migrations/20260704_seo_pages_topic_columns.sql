-- Extends seo_pages for the adaptive/multi-product SEO content engine.
-- Additive + nullable: safe to run against the 125 existing rows as-is.

ALTER TABLE seo_pages ADD COLUMN IF NOT EXISTS topic_kind TEXT;
ALTER TABLE seo_pages ADD COLUMN IF NOT EXISTS product TEXT;
ALTER TABLE seo_pages ADD COLUMN IF NOT EXISTS region TEXT;
ALTER TABLE seo_pages ADD COLUMN IF NOT EXISTS content_hash TEXT;

CREATE INDEX IF NOT EXISTS idx_seo_content_hash ON seo_pages(content_hash);
CREATE INDEX IF NOT EXISTS idx_seo_product ON seo_pages(product);

-- Phase 2 (GSC feedback loop) — created now so Phase 1 doesn't need a second
-- manual migration later.
CREATE TABLE IF NOT EXISTS seo_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    ctr NUMERIC,
    position NUMERIC,
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_seo_perf_slug ON seo_performance(slug);
CREATE INDEX IF NOT EXISTS idx_seo_perf_date ON seo_performance(snapshot_date DESC);
