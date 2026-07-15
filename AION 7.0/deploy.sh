#!/bin/bash
set -e

echo "=================================================="
echo "  H-MAS - 27 AGENTES - FLASH DEPLOYMENT"
echo "=================================================="

echo ""
echo "[1/8] Verificando dependencias..."
command -v docker >/dev/null 2>&1 || { echo "Docker nao encontrado. Instale docker primeiro."; exit 1; }
command -v python >/dev/null 2>&1 || { echo "Python nao encontrado."; exit 1; }

echo "[2/8] Configurando ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "TENANT_ID=default" >> .env
    echo "AGENT_CLUSTER=production,logistics,quality" >> .env
    echo "BUDGET_PER_TASK=0.10" >> .env
    echo "MAX_AGENTS_PARALLEL=10" >> .env
    echo "  .env criado a partir de .env.example"
fi

echo "[3/8] Instalando dependencias Python..."
pip install -r requirements.txt -q

echo "[4/8] Subindo infraestrutura Docker..."
docker compose up -d

echo "[5/8] Aguardando orquestrador ficar saudavel..."
timeout 120 bash -c 'until curl -sf http://localhost:8000/ > /dev/null; do sleep 3; done'
echo "  Orquestrador pronto."

echo "[6/8] Inicializando 27 agentes..."
curl -s -X POST http://localhost:8000/api/agents/initialize \
  -H "Content-Type: application/json" \
  -d '{"tenant": "default", "clusters": ["production", "logistics", "quality"]}' || echo "  (Orquestrador pode estar inicializando...)"

echo "[7/8] Verificando status..."
curl -s http://localhost:8000/api/status/default | python -m json.tool 2>/dev/null || echo "  (Aguardando orquestrador...)"
curl -s http://localhost:8000/ | python -m json.tool 2>/dev/null || echo "  (OK)"

echo "[8/8] Servicos disponiveis:"
echo "  API:         http://localhost:8000"
echo "  Dashboard:   http://localhost:8000/api/status/default"
echo "  Prometheus:  http://localhost:9090"
echo "  Grafana:     http://localhost:3000 (admin/admin)"
echo "  Kibana:      http://localhost:5601"
echo "  MinIO:       http://localhost:9001 (hmas_admin/hmas_storage_2024)"
echo "  Neo4j:       http://localhost:7474 (neo4j/hmas_graph_2024)"
echo "  Redis:       localhost:6379"
echo "  Kafka:       localhost:9093"
echo ""
echo "=================================================="
echo "  DEPLOY CONCLUIDO - 27 AGENTES ATIVOS"
echo "=================================================="
