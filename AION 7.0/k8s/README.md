# K8s - AION no Google Kubernetes Engine

## Pré-requisitos

```bash
gcloud auth login
gcloud config set project global-engenharia-498823
gcloud services enable container.googleapis.com cloudresourcemanager.googleapis.com
```

## Criar cluster GKE

```bash
gcloud container clusters create aion-gke \
  --region=southamerica-east1 \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --enable-autoscaling --min-nodes=3 --max-nodes=10 \
  --workload-pool=global-engenharia-498823.svc.id.goog
```

## Habilitar AppHub

```bash
gcloud services enable apphub.googleapis.com
gcloud app hub enable --project=global-engenharia-498823
```

A partir daqui, todo deployment com a annotation `apphub.cloud.google.com/functional-type: "AGENT"` é automaticamente registrado no Agent Registry do AppHub.

## Deploy

```bash
# Deploy completo
./k8s/deploy.sh

# Ou manualmente
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml -n aion
kubectl apply -f k8s/agent-registry.yaml -n aion
kubectl apply -f k8s/orchestrator/ -n aion
kubectl apply -f k8s/mcp/ -n aion
kubectl apply -f k8s/ingress.yaml -n aion
```

## Estrutura

```
k8s/
├── namespace.yaml           # Namespace aion
├── configmap.yaml           # ConfigMap compartilhado (config.yaml)
├── secrets.yaml             # Secrets (API keys)
├── agent-registry.yaml      # Agent Registry com 78 agentes
├── ingress.yaml             # Ingress + SSL ManagedCertificate
├── deploy.sh                # Script de deploy completo
├── orchestrator/
│   ├── deployment.yaml      # Orchestrator (FastAPI + AppHub annotation)
│   └── service-account.yaml # Workload Identity + RBAC
├── mcp/
│   ├── regulatory.yaml      # MCP Regulatory Server
│   ├── esg.yaml             # MCP ESG Server
│   ├── erp.yaml             # MCP ERP Server
│   └── microsoft.yaml       # MCP Microsoft Server
└── infra/
    ├── redis.yaml           # Redis (cache/streams)
    └── chromadb.yaml        # ChromaDB (vetorial)
```

## AppHub Agent Registry

Cada deployment com annotation `apphub.cloud.google.com/functional-type: "AGENT"` é descoberto automaticamente pelo AppHub.

O ConfigMap `aion-agent-registry` contém o registro completo de todos os 78 agentes com:
- ID, nome, cluster, descrição
- LLM model (deepseek-chat, gemini-pro, claude-api)
- Status (active, scheduled, co-sell)
- Service endpoint (service:port)
- Cluster/Channel mapping

## URLs

| Serviço | URL |
|---------|-----|
| API Principal | `https://aion.engenheiro-producao-ai.com` |
| MCP Regulatory | `https://aion.engenheiro-producao-ai.com/mcp/regulatory/sse` |
| MCP ESG | `https://aion.engenheiro-producao-ai.com/mcp/esg/sse` |
| MCP ERP | `https://aion.engenheiro-producao-ai.com/mcp/erp/sse` |
| MCP Microsoft | `https://aion.engenheiro-producao-ai.com/mcp/microsoft/sse` |
| Agent Registry | `https://aion.engenheiro-producao-ai.com/mcp/servers` |