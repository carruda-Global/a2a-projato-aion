-- PMOC SEO pages currently live only in an in-memory Python dict, which is
-- wiped on every Render restart/deploy (these pages are actively running
-- Google Ads traffic, so losing them intermittently is a real quality-score
-- and wasted-spend risk). This table gives them the same persistence the
-- main seo_pages table already has.

CREATE TABLE IF NOT EXISTS pmoc_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    batch TEXT NOT NULL,
    html TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pmoc_slug ON pmoc_pages(slug);
