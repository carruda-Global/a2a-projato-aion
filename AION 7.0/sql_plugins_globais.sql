DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'plugin_usage') THEN
    CREATE TABLE plugin_usage (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        plugin_source TEXT,
        page_context TEXT,
        message TEXT,
        response TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX idx_plugin_source ON plugin_usage(plugin_source);
    CREATE INDEX idx_plugin_created ON plugin_usage(created_at DESC);
  END IF;
END $$;
