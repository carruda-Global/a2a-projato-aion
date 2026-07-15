DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'chat_logs') THEN
    CREATE TABLE chat_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        message TEXT, response TEXT, page TEXT, market TEXT DEFAULT 'BR',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX idx_chat_market ON chat_logs(market);
    CREATE INDEX idx_chat_created ON chat_logs(created_at DESC);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'identified_leads') THEN
    CREATE TABLE identified_leads (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_name TEXT, country TEXT, market TEXT,
        page_visited TEXT, ip TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX idx_leads_market ON identified_leads(market);
    CREATE INDEX idx_leads_created ON identified_leads(created_at DESC);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'seo_pages') THEN
    CREATE TABLE seo_pages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        slug TEXT UNIQUE NOT NULL,
        title TEXT, meta_description TEXT, body TEXT,
        stripe_link TEXT, market TEXT,
        published BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX idx_seo_slug ON seo_pages(slug);
    CREATE INDEX idx_seo_market ON seo_pages(market);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'usage_charges') THEN
    CREATE TABLE usage_charges (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        market TEXT NOT NULL, agent_id TEXT NOT NULL,
        email TEXT, stripe_session_id TEXT,
        amount_brl NUMERIC(10,2) DEFAULT 0,
        amount_usd NUMERIC(10,2) DEFAULT 0,
        currency TEXT DEFAULT 'brl',
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX idx_usage_market ON usage_charges(market);
  END IF;
END $$;
