#!/usr/bin/env bash
# ============================================================
# AION 7.0 - Deploy para GKE com AppHub Agent Registry
# ============================================================
set -euo pipefail

PROJECT_ID="global-engenharia-498823"
CLUSTER_NAME="aion-gke"
CLUSTER_REGION="southamerica-east1"
IMAGE_TAG="${1:-7.0.0}"
NAMESPACE="aion"

echo "============================================"
echo " AION 7.0 - Deploy para GKE"
echo " Projeto: ${PROJECT_ID}"
echo " Cluster: ${CLUSTER_NAME}"
echo " Regiao:  ${CLUSTER_REGION}"
echo " Tag:     ${IMAGE_TAG}"
echo "============================================"

# Step 1: Autenticar no GCP
echo "[1/8] Autenticando no GCP..."
gcloud auth configure-docker ${CLUSTER_REGION}-docker.pkg.dev --quiet

# Step 2: Construir imagens Docker
echo "[2/8] Construindo imagens Docker..."
SERVICES=("orchestrator" "mcp-regulatory" "mcp-esg" "mcp-erp" "mcp-microsoft")
for svc in "${SERVICES[@]}"; do
    IMG="${CLUSTER_REGION}-docker.pkg.dev/${PROJECT_ID}/aion/${svc}:${IMAGE_TAG}"
    echo "  -> Construindo ${IMG}"
    docker build -t "${IMG}" .
    docker push "${IMG}"
done

# Step 3: Obter credentials do cluster
echo "[3/8] Obtendo kubeconfig do GKE..."
gcloud container clusters get-credentials "${CLUSTER_NAME}" --region="${CLUSTER_REGION}" --project="${PROJECT_ID}"

# Step 4: Criar namespace
echo "[4/8] Criando namespace ${NAMESPACE}..."
kubectl apply -f k8s/namespace.yaml

# Step 5: Aplicar ConfigMaps e Secrets
echo "[5/8] Aplicando ConfigMaps e Secrets..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml -n "${NAMESPACE}"
kubectl apply -f k8s/agent-registry.yaml -n "${NAMESPACE}"

# Step 6: Criar service account
echo "[6/8] Criando Service Account..."
kubectl apply -f k8s/orchestrator/service-account.yaml -n "${NAMESPACE}"

# Step 7: Deploy dos serviços
echo "[7/8] Deploy dos serviços no GKE..."
kubectl apply -f k8s/orchestrator/deployment.yaml -n "${NAMESPACE}"
kubectl apply -f k8s/mcp/regulatory.yaml -n "${NAMESPACE}"
kubectl apply -f k8s/mcp/esg.yaml -n "${NAMESPACE}"
kubectl apply -f k8s/mcp/erp.yaml -n "${NAMESPACE}"
kubectl apply -f k8s/mcp/microsoft.yaml -n "${NAMESPACE}"

# Step 8: Configurar Ingress
echo "[8/8] Configurando Ingress + SSL..."
kubectl apply -f k8s/ingress.yaml -n "${NAMESPACE}"

echo ""
echo "============================================"
echo " Deploy concluido!"
echo "============================================"
echo ""
echo "Aguardando deployments ficarem prontos..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/aion-orchestrator \
    deployment/aion-mcp-regulatory \
    deployment/aion-mcp-esg \
    deployment/aion-mcp-erp \
    deployment/aion-mcp-microsoft \
    -n "${NAMESPACE}"

echo ""
echo "Pods ativos:"
kubectl get pods -n "${NAMESPACE}"

echo ""
echo "Services:"
kubectl get svc -n "${NAMESPACE}"

echo ""
echo "Ingress:"
kubectl get ingress -n "${NAMESPACE}"

echo ""
echo "=== Agent Registry ==="
echo "AppHub ja esta descobrindo os agentes via annotation:"
echo "  apphub.cloud.google.com/functional-type: AGENT"
echo ""
echo "URLs de acesso:"
echo "  API:       https://aion.engenheiro-producao-ai.com"
echo "  MCP Reg:   https://aion.engenheiro-producao-ai.com/mcp/regulatory/sse"
echo "  MCP ESG:   https://aion.engenheiro-producao-ai.com/mcp/esg/sse"
echo "  MCP ERP:   https://aion.engenheiro-producao-ai.com/mcp/erp/sse"
echo "  MCP MS:    https://aion.engenheiro-producao-ai.com/mcp/microsoft/sse"
echo "  Registry:  https://aion.engenheiro-producao-ai.com/mcp/servers"