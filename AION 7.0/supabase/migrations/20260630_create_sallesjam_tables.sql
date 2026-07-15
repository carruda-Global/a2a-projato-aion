-- SallesJam: 5 mercados (Brasil, EUA, México, Colômbia, Argentina)
-- Chat logs, leads identificados, páginas SEO e cobrança pay-per-use

CREATE TABLE IF NOT EXISTS chat_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message TEXT, response TEXT, page TEXT, market TEXT DEFAULT 'BR',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chat_market ON chat_logs(market);
CREATE INDEX IF NOT EXISTS idx_chat_created ON chat_logs(created_at DESC);

CREATE TABLE IF NOT EXISTS identified_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT, country TEXT, market TEXT,
    page_visited TEXT, ip TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_leads_market ON identified_leads(market);
CREATE INDEX IF NOT EXISTS idx_leads_created ON identified_leads(created_at DESC);

CREATE TABLE IF NOT EXISTS seo_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT, meta_description TEXT, body TEXT,
    stripe_link TEXT, market TEXT,
    published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_seo_slug ON seo_pages(slug);
CREATE INDEX IF NOT EXISTS idx_seo_market ON seo_pages(market);

CREATE TABLE IF NOT EXISTS usage_charges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market TEXT NOT NULL, agent_id TEXT NOT NULL,
    email TEXT, stripe_session_id TEXT,
    amount_brl NUMERIC(10,2) DEFAULT 0,
    amount_usd NUMERIC(10,2) DEFAULT 0,
    currency TEXT DEFAULT 'brl',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_usage_market ON usage_charges(market);
