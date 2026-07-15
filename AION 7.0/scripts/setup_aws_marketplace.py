"""
Script de setup para AWS Marketplace - Engenheiro de Producao AI

Este script guia o registro do produto no AWS Marketplace e gera
o template de configuracao necessario.

Requisitos:
  - Conta AWS com acesso ao AWS Marketplace Management Portal
  - IAM User com permissoes: aws-marketplace:*
  - AWS CLI configurado (aws configure) ou variaveis de ambiente

Uso:
  python scripts/setup_aws_marketplace.py
"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def print_step(step: int, title: str):
    print(f"\n{'='*60}")
    print(f" PASSO {step}: {title}")
    print(f"{'='*60}")


def check_aws_credentials():
    """Verifica se credenciais AWS estao configuradas."""
    keys = [
        ("AWS_ACCESS_KEY_ID", os.getenv("AWS_ACCESS_KEY_ID")),
        ("AWS_SECRET_ACCESS_KEY", os.getenv("AWS_SECRET_ACCESS_KEY")),
        ("AWS_DEFAULT_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1")),
    ]
    missing = [k for k, v in keys if not v]

    if missing:
        print(" Credenciais AWS nao encontradas:")
        for k in missing:
            print(f"   - {k} nao configurada")
        print("\n Configure via ~/.aws/credentials ou variaveis de ambiente.")
        return False

    print(" Credenciais AWS OK:")
    for k, v in keys:
        print(f"   {k}={v}")
    return True


def generate_product_template():
    """Gera template JSON para criacao do produto SaaS no AWS Marketplace."""
    AWS_ACCOUNT_ID = "819743217542"

    template = {
        "aws_account_id": AWS_ACCOUNT_ID,
        "product": {
            "title": "Engenheiro de Producao AI",
            "description": (
                "Sistema multiagente de IA para o setor de Arquitetura, "
                "Engenharia e Construcao (AEC). Automatiza analise de "
                "especificacoes tecnicas, processamento de ordens de compra, "
                "gestao de estoque de obra, rastreamento logistico e "
                "geracao de instrucoes de execucao em campo."
            ),
            "short_description": "IA multiagente para engenharia e construcao",
            "sku": "ENGPROAI-V1",
            "product_type": "SaaS",
            "categories": [
                "Artificial Intelligence",
                "Machine Learning",
                "Engineering",
                "Construction",
            ],
            "industries": [
                "Architecture & Construction",
                "Engineering",
                "Infrastructure",
            ],
            "pricing_model": "Monthly Subscription",
            "refund_policy": "14-day full refund",
            "eula_url": "https://engenheiro-producao-ai.onrender.com/eula",
            "support_url": "https://engenheiro-producao-ai.onrender.com/support",
            "support_email": "suporte@projatoengenharia.com",
        },
        "registration": {
            "url": "https://engenheiro-producao-ai.onrender.com/api/v1/aws-marketplace/subscribe",
            "verification_urls": [
                "https://engenheiro-producao-ai.onrender.com/api/v1/aws-marketplace/entitlement/{customer_id}",
                "https://engenheiro-producao-ai.onrender.com/api/v1/aws-marketplace/verify?customer_id={customer_id}",
            ],
            "sns_topic": "arn:aws:sns:us-east-1:819743217542:engproai-subscriptions",
        },
        "pricing": [
            {
                "plan": "Starter - Spec Analyst",
                "price": "$199/month",
                "dimension": "spec_analyst_seats",
                "description": "1 agente: Analisador de Especificacoes Tecnicas",
            },
            {
                "plan": "Professional",
                "price": "$299/month",
                "dimension": "professional_seats",
                "description": "2 agentes: Spec Analyst + Procurement",
            },
            {
                "plan": "Enterprise",
                "price": "$599/month",
                "dimension": "enterprise_seats",
                "description": "4 agentes: Spec Analyst, Procurement, Inventory, Logistics",
            },
            {
                "plan": "Full Suite",
                "price": "$699/month",
                "dimension": "full_suite_seats",
                "description": "Todos os 5 agentes + cross-selling automatico",
            },
        ],
        "endpoints": {
            "subscribe": "GET /api/v1/aws-marketplace/subscribe",
            "sns_webhook": "POST /api/v1/aws-marketplace/sns",
            "entitlement": "GET /api/v1/aws-marketplace/entitlement/{customer_id}",
            "verify": "GET /api/v1/aws-marketplace/verify",
            "list_plans": "GET /api/v1/aws-marketplace/plans",
        },
    }

    output_path = BASE_DIR / "config" / "aws_marketplace_offer.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, indent=2, ensure_ascii=False))

    print(f" Template salvo em: {output_path}")
    return template


def print_instructions():
    """Exibe instrucoes para registro no AWS Marketplace."""
    print_step(3, "REGISTRO NO AWS MARKETPLACE (MANUAL)")

    instructions = """
1. Acesse o AWS Marketplace Management Portal:
   https://aws.amazon.com/marketplace/management/

2. Faca login com sua conta AWS (recommendado: conta organizacional)

3. Va em "Products" -> "SaaS" -> "Create new SaaS product"

4. Preencha:
   - Product name: "Engenheiro de Producao AI"
   - Product description: Sistema multiagente de IA para AEC
   - Registration URL: Sua URL de registro (veja template gerado)
   - Pricing: Selecione "Subscription" (monthly)

5. Configure o SNS topic:
   - Crie um SNS Topic no console AWS
   - Assine a URL: POST /api/v1/aws-marketplace/sns
   - Configure a politica de acesso para permitir AWS Marketplace

6. Submeta para revisao da AWS (pode levar 2-5 dias uteis)

7. Apos aprovacao, ative em "Products" -> seu produto -> "Publish"

8. Atualize config.yaml:
     marketplace:
       aws:
         enabled: true
         product_code: SEU_PRODUCT_CODE
         sns_topic_arn: arn:aws:sns:...

9. Configure IAM permissions:
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": [
         "aws-marketplace:ResolveCustomer",
         "aws-marketplace:GetEntitlements",
         "aws-marketplace:MeterUsage"
       ],
       "Resource": "*"
     }]
   }

10. Teste o fluxo completo:
    python scripts/test_aws_marketplace.py
"""
    print(instructions)


def main():
    print("=" * 60)
    print("  SETUP AWS MARKETPLACE - Engenheiro de Producao AI")
    print("=" * 60)

    print_step(1, "VERIFICAR CREDENCIAIS AWS")
    creds_ok = check_aws_credentials()
    if not creds_ok:
        print(" Configure as credenciais AWS primeiro.")
        print("   aws configure")
        print("     ou")
        print("   export AWS_ACCESS_KEY_ID=...")
        print("   export AWS_SECRET_ACCESS_KEY=...")

    print_step(2, "GERAR TEMPLATE DO PRODUTO")
    template = generate_product_template()
    print(f" Produto: {template['product']['title']}")
    print(f" Planos: {len(template['pricing'])}")

    print_instructions()

    print("\n" + "=" * 60)
    print("  PROXIMOS PASSOS")
    print("=" * 60)
    print("""
1. Decida o modelo de precificacao (Subscription recomendado)
2. Crie o produto no AWS Marketplace Management Portal
3. Configure SNS e IAM
4. Teste o fluxo subscribe -> resolve -> entitlement
5. Publique e comeca a vender!

Tem alguma duvida sobre o processo?
""")


if __name__ == "__main__":
    main()
