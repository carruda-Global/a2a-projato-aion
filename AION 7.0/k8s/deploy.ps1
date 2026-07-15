# ============================================================
# AION 7.0 - Deploy para GKE com AppHub Agent Registry
# ============================================================
param(
    [string]$ImageTag = "7.0.0"
)

$ProjectId = "global-engenharia-498823"
$ClusterName = "aion-gke"
$ClusterRegion = "southamerica-east1"
$Namespace = "aion"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " AION 7.0 - Deploy para GKE" -ForegroundColor Cyan
Write-Host " Projeto: $ProjectId" -ForegroundColor Cyan
Write-Host " Cluster: $ClusterName" -ForegroundColor Cyan
Write-Host " Regiao:  $ClusterRegion" -ForegroundColor Cyan
Write-Host " Tag:     $ImageTag" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Step 1: Autenticar
Write-Host "[1/7] Autenticando no GCP..." -ForegroundColor Yellow
gcloud auth configure-docker "${ClusterRegion}-docker.pkg.dev" --quiet

# Step 2: Construir imagens
Write-Host "[2/7] Construindo imagens Docker..." -ForegroundColor Yellow
$services = @("orchestrator", "mcp-regulatory", "mcp-esg", "mcp-erp", "mcp-microsoft")
foreach ($svc in $services) {
    $img = "${ClusterRegion}-docker.pkg.dev/${ProjectId}/aion/${svc}:${ImageTag}"
    Write-Host "  -> Construindo ${img}"
    docker build -t "${img}" .
    docker push "${img}"
}

# Step 3: Kubeconfig
Write-Host "[3/7] Obtendo kubeconfig do GKE..." -ForegroundColor Yellow
gcloud container clusters get-credentials $ClusterName --region=$ClusterRegion --project=$ProjectId

# Step 4: Apply manifests
Write-Host "[4/7] Aplicando manifests K8s..." -ForegroundColor Yellow
kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\configmap.yaml
kubectl apply -f k8s\secrets.yaml -n $Namespace
kubectl apply -f k8s\agent-registry.yaml -n $Namespace

# Step 5: Service Account
Write-Host "[5/7] Criando Service Account..." -ForegroundColor Yellow
kubectl apply -f k8s\orchestrator\service-account.yaml -n $Namespace

# Step 6: Deployments
Write-Host "[6/7] Deploy dos servicos..." -ForegroundColor Yellow
kubectl apply -f k8s\orchestrator\deployment.yaml -n $Namespace
kubectl apply -f k8s\mcp\regulatory.yaml -n $Namespace
kubectl apply -f k8s\mcp\esg.yaml -n $Namespace
kubectl apply -f k8s\mcp\erp.yaml -n $Namespace
kubectl apply -f k8s\mcp\microsoft.yaml -n $Namespace

# Step 7: Ingress
Write-Host "[7/7] Configurando Ingress..." -ForegroundColor Yellow
kubectl apply -f k8s\ingress.yaml -n $Namespace

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " Deploy concluido!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Aguardando deployments..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s `
    deployment/aion-orchestrator `
    deployment/aion-mcp-regulatory `
    deployment/aion-mcp-esg `
    deployment/aion-mcp-erp `
    deployment/aion-mcp-microsoft `
    -n $Namespace

Write-Host ""
Write-Host "Pods ativos:" -ForegroundColor Cyan
kubectl get pods -n $Namespace

Write-Host ""
Write-Host "=== Agent Registry ===" -ForegroundColor Green
Write-Host "AppHub descobre automaticamente agentes via annotation:" -ForegroundColor Green
Write-Host "  apphub.cloud.google.com/functional-type: AGENT" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Green
Write-Host "  API:       https://aion.engenheiro-producao-ai.com"
Write-Host "  MCP Reg:   https://aion.engenheiro-producao-ai.com/mcp/regulatory/sse"
Write-Host "  MCP ESG:   https://aion.engenheiro-producao-ai.com/mcp/esg/sse"
Write-Host "  MCP ERP:   https://aion.engenheiro-producao-ai.com/mcp/erp/sse"
Write-Host "  MCP MS:    https://aion.engenheiro-producao-ai.com/mcp/microsoft/sse"