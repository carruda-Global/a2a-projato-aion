"""
Script único de setup para produção.
Cria produtos no Stripe, tabelas no Supabase e valida .env.

Uso:
    python scripts/setup_producao.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings, load_config
from src.monetization.plans import PLANS


def check_env():
    required = {
        "DEEPSEEK_API_KEY": "sk-... (DeepSeek)",
        "STRIPE_SECRET_KEY": "sk_live_... (Stripe)",
        "STRIPE_PUBLISHABLE_KEY": "pk_live_... (Stripe)",
        "STRIPE_WEBHOOK_SECRET": "whsec_... (Stripe)",
        "SUPABASE_URL": "https://... (Supabase)",
        "SUPABASE_API_KEY": "eyJ... (Supabase anon key)",
        "AZURE_TENANT_ID": "cb5ac0c5...",
        "AZURE_CLIENT_ID": "e5db2874...",
        "AZURE_CLIENT_SECRET": "jRp8Q~...",
    }
    missing = []
    for var, hint in required.items():
        val = os.getenv(var)
        if not val or val.startswith(("your-", "sk_test", "pk_test", "https://your")):
            missing.append(f"  {var} -> {hint}")
    return missing


def generate_supabase_sql():
    return """
-- EcoSystem AEC + Regulatory - Setup Supabase
-- Execute no SQL Editor do Supabase Dashboard

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    company TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    stripe_subscription_id TEXT,
    microsoft_subscription_id TEXT,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
"""


def generate_stripe_products_script():
    lines = ["# EcoSystem AEC + Regulatory - Criar Produtos no Stripe"]
    lines.append("# Execute: python scripts/create_stripe_products.py")
    lines.append("# Depois copie os price_id gerados para config.yaml\n")
    lines.append("import stripe")
    lines.append("stripe.api_key = 'sk_live_SEU_STRIPE_SECRET_KEY'\n")
    for plan in PLANS:
        name = plan["name"]
        price = plan["price"]
        lines.append(f"prod = stripe.Product.create(name='{name}')")
        lines.append(f"price = stripe.Price.create(")
        lines.append(f"    product=prod.id,")
        lines.append(f"    unit_amount={price},")
        lines.append(f"    currency='brl',")
        lines.append(f"    recurring={{'interval': 'month'}},")
        lines.append(f")")
        lines.append(f"print(f'{plan[\"id\"]}: {{price.id}}')")
        lines.append("")
    return "\n".join(lines)


def update_config_with_price_ids():
    config = load_config()
    plans = config.get("stripe", {}).get("plans", {})
    print("\nPreencha estes price_id no config.yaml:\n")
    for plan_id, plan_data in plans.items():
        pid = plan_data.get("price_id", "")
        if not pid:
            print(f"  stripe.plans.{plan_id}.price_id: \"\"")


def main():
    print("=" * 60)
    print("  EcoSystem AEC + Regulatory - Setup de Producao")
    print("=" * 60)

    print("\n1. Verificando .env...")
    missing = check_env()
    if missing:
        print("  VARIAVEIS PENDENTES:")
        for m in missing:
            print(f"    {m}")
    else:
        print("  Todas as variaveis configuradas!")

    print("\n2. SQL para Supabase (criar tabelas):")
    print("  Copie e cole no SQL Editor do Supabase Dashboard")
    print(generate_supabase_sql()[:200] + "...")

    print("\n3. Script para criar produtos no Stripe:")
    print("  scripts/create_stripe_products.py ja existe")
    print("  Execute: python scripts/create_stripe_products.py")

    print("\n4. Depois de criar os price_id no Stripe:")
    print("  Preencha em config.yaml > stripe.plans > cada plano > price_id")

    print("\n5. Deploy:")
    print("  Render.com: conecte o repo e configure as env vars")
    print("  Docker: docker-compose up -d")
    print("  URL: https://engenheiro-producao-ai.onrender.com")
    print("  Health: https://engenheiro-producao-ai.onrender.com/api/v1/health")


if __name__ == "__main__":
    main()
