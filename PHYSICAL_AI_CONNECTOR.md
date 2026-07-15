# EcoSystem — Physical AI Connector #63
## NVIDIA Omniverse + Azure Foundry + Google Cloud + ERP
**Global Match Engenharia de Produção | CREA-SP 5071200171**
**Data:** 2026-06-24
**Posicionamento:** A ponte que NVIDIA + Microsoft + Google não têm
**Canal:** Microsoft Marketplace + Google Cloud Marketplace + NVIDIA NGC Catalog
**Preço:** USD 3.990/mês enterprise

---

## O QUE A PESQUISA CONFIRMOU

**Microsoft + NVIDIA (março 2026):**
Microsoft Fabric + NVIDIA Omniverse conectam dados operacionais
com digital twins. Foundry Agent Service em GA para agentes de produção.
**Gap:** conectam simulação com dados — mas não com ERP, compliance e gestão.

**Google + NVIDIA (abril 2026):**
NVIDIA Isaac Sim + Cosmos Reason 2 disponíveis no Google Cloud Marketplace.
Digital twins e robótica em GKE.
**Gap:** robots e sensores veem e agem — mas não fecham o ciclo
de gestão (OS no SAP, atualização no Dynamics, relatório ESG).

**O gap real identificado:**
```
NVIDIA Omniverse simula a fábrica → dados ficam no Omniverse
Sensor IoT detecta falha → alerta fica no dashboard
Robot conclui tarefa → registro fica no sistema NVIDIA

Ninguém conecta com:
→ SAP (OS de manutenção)
→ Dynamics (estoque e suprimentos)
→ Oracle (financeiro e compliance)
→ Relatório ESG/Carbono (Escopo 1 — emissões da produção)
→ NR-12 (segurança em manutenção)
```

---

## O QUE O PHYSICAL AI CONNECTOR RESOLVE

```
┌─────────────────────────────────────────────────────────────────┐
│                  PHYSICAL AI CONNECTOR #63                      │
│                                                                 │
│  MUNDO FÍSICO                    MUNDO DIGITAL                  │
│  ┌────────────────┐              ┌─────────────────────────┐   │
│  │ NVIDIA         │              │ ERP + Compliance        │   │
│  │ Omniverse      │◄────────────►│ SAP S/4HANA             │   │
│  │ Isaac Sim      │              │ Dynamics 365            │   │
│  │ Cosmos Reason  │              │ Oracle Fusion           │   │
│  └────────────────┘              └─────────────────────────┘   │
│          ▲                                ▲                     │
│          │     PHYSICAL AI CONNECTOR      │                     │
│          │    ┌────────────────────────┐  │                     │
│          └───►│ Event Router           │◄─┘                     │
│               │ • Sensor → OS SAP      │                       │
│               │ • Robot → Dynamics     │                       │
│               │ • Falha → NR-12 Alert  │                       │
│               │ • Produção → Carbono   │                       │
│               │ • Digital Twin → BIM   │                       │
│               └────────────────────────┘                       │
│                          ▲                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Azure Foundry │ Google GKE │ Edge/On-premise           │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## CASOS DE USO REAIS

### Caso 1 — Manutenção preditiva → SAP automático
```
Sensor IoT detecta vibração anormal no motor
        ↓
NVIDIA Cosmos Reason analisa: "falha em 48h com 94% probabilidade"
        ↓
Physical AI Connector intercepta o evento
        ↓
Abre OS no SAP PM automaticamente
Aloca técnico via Dynamics HR
Pede peça de reposição via SAP MM
Notifica supervisor via Teams
Calcula custo de parada evitada
        ↓
Relatório NR-12 gerado automaticamente
        ↓
EcoSystem #47 (SAP Predictive Maintenance) atualiza histórico
```

### Caso 2 — Produção → Inventário de Carbono automático
```
Linha de produção opera por 8h
        ↓
NVIDIA Omniverse registra: 450 kWh consumidos, 200 unidades produzidas
        ↓
Physical AI Connector intercepta dados de produção
        ↓
Calcula emissões Escopo 1 (energia elétrica BR = 0,0817 tCO2/MWh)
Atualiza Inventário de Carbono no EcoSystem #17
Gera relatório SBCE do período
Alerta se meta de carbono mensal será excedida
        ↓
ESG IFRS (#16) atualiza dashboard de sustentabilidade automaticamente
```

### Caso 3 — Digital Twin → BIM + Dynamics
```
BMW usa Omniverse para planejar fábrica antes de construir
Foxconn usa Cadence para simulação térmica 150x mais rápida
        ↓
Physical AI Connector sincroniza digital twin com:
→ BIM Coordinator (#6) — arquivos IFC atualizados
→ Dynamics Supply Chain (#33) — materiais necessários
→ Field Execution (#5) — guia trabalhadores com RA
→ Compliance PGRS (#12) — mapa de riscos atualizado
```

---

## IMPLEMENTAÇÃO TÉCNICA

```python
# src/agents/physical_ai_connector.py
"""
Physical AI Connector — #63
Ponte entre NVIDIA Physical AI e sistemas enterprise.
Integra: NVIDIA Omniverse + Isaac + Cosmos → SAP + Dynamics + Oracle + EcoSystem
"""
from fastapi import APIRouter, Request, BackgroundTasks
from src.database.supabase_client import SupabaseClient
from src.api.sap_client import SAPClient
from src.api.dynamics_client import DynamicsClient
from src.api.oracle_client import OracleClient
from src.agents.inventario_carbono import InventarioCarbonAgent
from src.agents.sap_predictive_maintenance import SAPPredictiveAgent
import logging

router = APIRouter(prefix="/api/physical-ai", tags=["physical_ai"])
logger = logging.getLogger(__name__)

# Mapeamento de eventos físicos para ações enterprise
EVENT_HANDLERS = {
    # Manutenção
    "equipment_anomaly":        "create_sap_maintenance_order",
    "predictive_failure":       "create_sap_maintenance_order",
    "maintenance_completed":    "close_sap_order_update_history",

    # Produção
    "production_cycle_complete": "update_inventory_carbon",
    "energy_consumption":        "update_carbon_scope1",
    "production_output":         "update_dynamics_inventory",

    # Segurança
    "safety_violation":         "create_nr12_alert",
    "epi_not_detected":         "create_photo_intelligence_alert",
    "emergency_stop":           "create_emergency_protocol",

    # Digital Twin
    "digital_twin_updated":     "sync_bim_coordinator",
    "simulation_complete":      "update_supply_chain",
    "factory_layout_changed":   "update_field_execution",
}

class PhysicalAIConnector:

    async def process_event(
        self,
        event_type: str,
        event_data: dict,
        source: str,  # 'nvidia_omniverse' | 'isaac_sim' | 'cosmos' | 'iot'
        tenant_id: str
    ) -> dict:
        """
        Processa evento físico e executa ações enterprise correspondentes.
        """
        handler_name = EVENT_HANDLERS.get(event_type)
        if not handler_name:
            logger.warning(f"Evento sem handler: {event_type}")
            return {"status": "no_handler", "event": event_type}

        # Executar handler
        handler = getattr(self, f"_{handler_name}", None)
        if not handler:
            return {"status": "handler_not_implemented", "handler": handler_name}

        result = await handler(event_data, tenant_id)

        # Salvar no log de eventos
        await self._log_event(
            event_type, source, event_data, result, tenant_id
        )

        return result

    # ─── HANDLERS DE MANUTENÇÃO ───

    async def _create_sap_maintenance_order(
        self, data: dict, tenant_id: str
    ) -> dict:
        """
        Cria OS de manutenção no SAP PM automaticamente.
        Acionado por anomalia detectada pelo NVIDIA Cosmos.
        """
        sap = SAPClient()
        equipment_id = data.get("equipment_id")
        failure_probability = data.get("failure_probability", 0)
        estimated_failure_hours = data.get("estimated_failure_hours", 48)

        # Criar OS no SAP PM
        order = await sap.create_maintenance_order({
            "equipment": equipment_id,
            "description": f"Manutenção preditiva — IA detectou falha em {estimated_failure_hours}h (prob: {failure_probability:.0%})",
            "priority": "1" if failure_probability > 0.8 else "2",
            "work_center": data.get("work_center"),
            "planned_start": data.get("planned_start"),
        })

        # Notificar via Teams
        await self._notify_teams(
            tenant_id=tenant_id,
            message=f"⚠️ Manutenção preditiva criada — {equipment_id}\n"
                    f"Probabilidade de falha: {failure_probability:.0%}\n"
                    f"OS SAP: {order.get('order_number')}",
            channel="manutencao"
        )

        # Acionar NR-12 se necessário
        if data.get("involves_electrical") or data.get("involves_pressure"):
            await self._create_nr12_alert(data, tenant_id)

        return {
            "status": "success",
            "sap_order": order.get("order_number"),
            "nr12_created": data.get("involves_electrical", False)
        }

    # ─── HANDLERS DE CARBONO ───

    async def _update_inventory_carbon(
        self, data: dict, tenant_id: str
    ) -> dict:
        """
        Atualiza Inventário de Carbono com dados de produção.
        Acionado ao fim de cada ciclo de produção.
        """
        # Fator de emissão elétrica Brasil (MCTI 2024)
        FATOR_EMISSAO_BR = 0.0817  # tCO2/MWh

        energy_kwh = data.get("energy_kwh", 0)
        units_produced = data.get("units_produced", 0)

        # Calcular emissões Escopo 1 e 2
        emissoes_escopo2 = (energy_kwh / 1000) * FATOR_EMISSAO_BR

        # Combustíveis diretos (Escopo 1)
        gas_natural_m3 = data.get("gas_natural_m3", 0)
        emissoes_escopo1 = gas_natural_m3 * 0.00202  # tCO2/m3

        total_emissoes = emissoes_escopo1 + emissoes_escopo2

        # Atualizar agente #17 do EcoSystem
        carbon_agent = InventarioCarbonAgent(tenant_id=tenant_id)
        await carbon_agent.update_realtime({
            "periodo": data.get("periodo"),
            "escopo1_tco2": emissoes_escopo1,
            "escopo2_tco2": emissoes_escopo2,
            "total_tco2": total_emissoes,
            "unidades_produzidas": units_produced,
            "intensidade_carbono": total_emissoes / max(units_produced, 1)
        })

        return {
            "status": "success",
            "emissoes_escopo1": emissoes_escopo1,
            "emissoes_escopo2": emissoes_escopo2,
            "total_tco2": total_emissoes
        }

    # ─── HANDLERS DE SEGURANÇA ───

    async def _create_nr12_alert(
        self, data: dict, tenant_id: str
    ) -> dict:
        """
        Cria alerta NR-12 (segurança em manutenção elétrica/mecânica).
        """
        db = SupabaseClient()
        alert = await db.table("nr12_alerts").insert({
            "tenant_id": tenant_id,
            "equipment_id": data.get("equipment_id"),
            "alert_type": data.get("alert_type", "predictive_maintenance"),
            "severity": "high" if data.get("failure_probability", 0) > 0.7 else "medium",
            "involves_electrical": data.get("involves_electrical", False),
            "involves_pressure": data.get("involves_pressure", False),
            "lockout_tagout_required": data.get("involves_electrical", False),
            "ppe_required": ["luvas isolantes", "óculos", "capacete"]
        }).execute()

        await self._notify_teams(
            tenant_id=tenant_id,
            message=f"🔴 ALERTA NR-12 — {data.get('equipment_id')}\n"
                    f"LOTO obrigatório antes de qualquer intervenção",
            channel="seguranca",
            urgent=True
        )

        return {"status": "success", "alert_id": alert.data[0]["id"]}

    # ─── HANDLERS DIGITAL TWIN ───

    async def _sync_bim_coordinator(
        self, data: dict, tenant_id: str
    ) -> dict:
        """
        Sincroniza digital twin atualizado com BIM Coordinator (#6).
        Conecta Omniverse → BIM → Field Execution.
        """
        # Notificar BIM Coordinator que o modelo foi atualizado
        from src.agents.bim_coordinator import BIMCoordinatorAgent
        bim = BIMCoordinatorAgent(tenant_id=tenant_id)

        result = await bim.sync_from_digital_twin({
            "twin_id": data.get("twin_id"),
            "changes": data.get("changes", []),
            "timestamp": data.get("timestamp")
        })

        # Se layout de fábrica mudou, atualizar Field Execution (#5)
        if data.get("layout_changed"):
            from src.agents.field_execution import FieldExecutionAgent
            fe = FieldExecutionAgent(tenant_id=tenant_id)
            await fe.update_ar_guides(data.get("new_layout"))

        return {"status": "success", "bim_updated": True}

    # ─── UTILITÁRIOS ───

    async def _notify_teams(
        self, tenant_id: str, message: str,
        channel: str = "geral", urgent: bool = False
    ):
        """Envia notificação no Microsoft Teams."""
        from src.api.dynamics_client import DynamicsClient
        dynamics = DynamicsClient()
        await dynamics.send_teams_message(
            tenant_id=tenant_id,
            channel=channel,
            message=message,
            urgent=urgent
        )

    async def _log_event(
        self, event_type: str, source: str,
        data: dict, result: dict, tenant_id: str
    ):
        db = SupabaseClient()
        await db.table("physical_ai_events").insert({
            "event_type": event_type,
            "source": source,
            "tenant_id": tenant_id,
            "event_data": str(data),
            "result": str(result)
        }).execute()


# ─── ENDPOINTS ───

@router.post("/event")
async def receive_physical_event(
    request: Request,
    bg: BackgroundTasks
):
    """
    Recebe eventos do NVIDIA Omniverse, Isaac Sim, Cosmos ou IoT.

    Headers:
        X-Source: nvidia_omniverse | isaac_sim | cosmos | iot_sensor
        X-Tenant-ID: tenant_id

    Body:
    {
        "event_type": "equipment_anomaly",
        "equipment_id": "MOTOR-001",
        "failure_probability": 0.87,
        "estimated_failure_hours": 36,
        "involves_electrical": true
    }
    """
    data = await request.json()
    source = request.headers.get("X-Source", "unknown")
    tenant_id = request.headers.get("X-Tenant-ID", "default")

    connector = PhysicalAIConnector()

    bg.add_task(
        connector.process_event,
        event_type=data.get("event_type"),
        event_data=data,
        source=source,
        tenant_id=tenant_id
    )

    return {"status": "received", "event_type": data.get("event_type")}


@router.get("/events/{tenant_id}")
async def get_physical_events(
    tenant_id: str, limit: int = 50
):
    """Histórico de eventos físicos processados."""
    db = SupabaseClient()
    result = await db.table("physical_ai_events").select(
        "*"
    ).eq("tenant_id", tenant_id).order(
        "created_at", desc=True
    ).limit(limit).execute()
    return {"events": result.data}


@router.get("/carbon/realtime/{tenant_id}")
async def get_realtime_carbon(tenant_id: str):
    """
    Emissões de carbono em tempo real da produção.
    Alimentado pelos eventos de produção do NVIDIA Omniverse.
    """
    db = SupabaseClient()
    result = await db.table("carbon_realtime").select(
        "*"
    ).eq("tenant_id", tenant_id).order(
        "created_at", desc=True
    ).limit(1).execute()
    return result.data[0] if result.data else {"total_tco2": 0}
```

---

## SQL — Tabelas necessárias

```sql
-- Eventos do mundo físico
CREATE TABLE physical_ai_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    event_data TEXT,
    result TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alertas NR-12
CREATE TABLE nr12_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    equipment_id TEXT,
    alert_type TEXT,
    severity TEXT,
    involves_electrical BOOLEAN,
    involves_pressure BOOLEAN,
    lockout_tagout_required BOOLEAN,
    ppe_required JSONB,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Carbono em tempo real
CREATE TABLE carbon_realtime (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    periodo TEXT,
    escopo1_tco2 DECIMAL(10,4),
    escopo2_tco2 DECIMAL(10,4),
    total_tco2 DECIMAL(10,4),
    unidades_produzidas INTEGER,
    intensidade_carbono DECIMAL(10,6),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_physical_tenant ON physical_ai_events(tenant_id);
CREATE INDEX idx_nr12_tenant ON nr12_alerts(tenant_id);
CREATE INDEX idx_carbon_tenant ON carbon_realtime(tenant_id, created_at DESC);
```

---

## INTEGRAÇÃO COM NVIDIA OMNIVERSE

```python
# src/api/omniverse_client.py
"""
Cliente NVIDIA Omniverse — recebe eventos do digital twin.
Usa NVIDIA Omniverse Kit API e NVIDIA Nucleus.
"""
import httpx, os

class OmniverseClient:

    def __init__(self):
        self.nucleus_url = os.getenv("NVIDIA_NUCLEUS_URL")
        self.api_key = os.getenv("NVIDIA_API_KEY")

    async def subscribe_events(self, scene_id: str) -> dict:
        """
        Assina eventos de um digital twin específico.
        Omniverse envia webhook quando scene muda.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.nucleus_url}/api/v1/scenes/{scene_id}/webhooks",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "url": f"{os.getenv('RENDER_URL')}/api/physical-ai/event",
                    "events": [
                        "simulation_complete",
                        "anomaly_detected",
                        "equipment_state_changed",
                        "production_cycle_complete"
                    ]
                }
            )
        return resp.json()

    async def get_sensor_data(
        self, scene_id: str, sensor_ids: list
    ) -> dict:
        """Busca dados de sensores IoT do digital twin."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.nucleus_url}/api/v1/scenes/{scene_id}/sensors",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"ids": ",".join(sensor_ids)}
            )
        return resp.json()
```

---

## REGISTRO NO CONFIG.YAML E AGENTS.MD

```yaml
# config.yaml — adicionar

clusters:
  physical_ai:
    enabled: true
    max_parallel: 5
    agents:
      physical_ai_connector: { enabled: true, budget_per_task: 0.20 }

# Variáveis de ambiente necessárias — .env
NVIDIA_NUCLEUS_URL=https://nucleus.your-omniverse.nvidia.com
NVIDIA_API_KEY=your-nvidia-api-key
NVIDIA_COSMOS_ENDPOINT=https://integrate.api.nvidia.com/v1
```

```markdown
# AGENTS.md — adicionar ao GRUPO 15

| # | ID | Nome | Conecta | Preço | LLM |
|---|----|----|---------|-------|-----|
| 63 | `physical_ai_connector` | Physical AI Connector | NVIDIA Omniverse + Azure Foundry + Google GKE + SAP/Dynamics/Oracle | USD 1.990–3.990/mês | Claude API |
```

---

## CROSS-SELL COM PORTFÓLIO EXISTENTE

```
Physical AI Connector (#63)
        ↓ detecta falha em equipamento
SAP Predictive Maintenance (#47) — cria OS automaticamente
        ↓ manutenção realizada
NR-12 Alert — compliance de segurança automático
        ↓ produção retoma
Inventário Carbono (#17) — atualiza emissões em tempo real
        ↓ relatório mensal
ESG IFRS (#16) — dashboard de sustentabilidade atualizado
        ↓ dados de fornecedores
Escopo 3 (#18) — rastreabilidade completa da cadeia

LTV cliente industrial: R$ 1.990 (Physical AI) +
                        R$ 1.290 (SAP Maintenance) +
                        R$ 890 (Carbono) +
                        R$ 490 (ESG) = R$ 4.660/mês
```

---

## PLANOS E PREÇOS

```
Physical AI Starter:    USD 990/mês
  → Até 10 equipamentos monitorados
  → Integração SAP ou Dynamics (escolher 1)
  → Alertas Teams

Physical AI Pro:        USD 1.990/mês
  → Até 100 equipamentos
  → SAP + Dynamics + Oracle
  → Carbono em tempo real
  → NR-12 automático

Physical AI Enterprise: USD 3.990/mês
  → Ilimitado
  → NVIDIA Omniverse + Isaac Sim + Cosmos
  → Digital Twin sync com BIM
  → SLA 99.9% + suporte 24/7
  → Onboarding dedicado
```

---

## MERCADO-ALVO

| Setor | Caso de uso | Budget típico |
|-------|------------|---------------|
| Manufatura | Manutenção preditiva + carbono | USD 5k–50k/ano |
| Automotivo | Digital twin + BIM + supply chain | USD 20k–200k/ano |
| Energia | Monitoramento de plantas + Escopo 1 | USD 10k–100k/ano |
| Construção civil | BIM + AEC + NR-12 + PGRS | R$ 5k–50k/mês |
| Aeroespacial | Simulação + compliance + carbono | USD 50k–500k/ano |

**Clientes como BMW, Foxconn e McLaren** já usam Omniverse.
O Physical AI Connector é o que conecta o trabalho deles
com o ERP e compliance que já usam.

---

## CHECKLIST DE IMPLEMENTAÇÃO

### Semana 1 — Core do conector
- [ ] Criar `src/agents/physical_ai_connector.py`
- [ ] Criar `src/api/omniverse_client.py`
- [ ] Criar tabelas Supabase (physical_ai_events, nr12_alerts, carbon_realtime)
- [ ] Registrar router em `app/main.py`
- [ ] Adicionar variáveis NVIDIA ao `.env`
- [ ] Testar endpoint `/api/physical-ai/event` com payload simulado

### Semana 2 — Integrações ERP
- [ ] Conectar com SAP PM (criar OS de manutenção)
- [ ] Conectar com Inventário Carbono (#17)
- [ ] Conectar com BIM Coordinator (#6)
- [ ] Testar pipeline: evento NVIDIA → SAP → Teams → Carbono

### Semana 3 — Listings
- [ ] Publicar no Microsoft Marketplace (categoria Manufacturing)
- [ ] Publicar no Google Cloud Marketplace (categoria Industrial AI)
- [ ] Publicar no NVIDIA NGC Catalog (canal específico para Physical AI)
- [ ] Criar price_ids Stripe para os 3 tiers

### Semana 4 — Go-to-market
- [ ] Solicitar co-sell Microsoft com foco em industrial/manufatura
- [ ] Contactar NVIDIA Partner Network
- [ ] Case study: cliente AEC existente usando Physical AI + BIM

---

## PROJEÇÃO FINANCEIRA

| Período | Clientes | Ticket médio | MRR | ARR |
|---------|---------|-------------|-----|-----|
| 3 meses | 5 | USD 1.990 | USD 9.950 | — |
| 6 meses | 20 | USD 2.490 | USD 49.800 | USD 597k |
| 12 meses | 60 | USD 2.990 | USD 179.400 | USD 2,15M |
| Ano 2 | 150 | USD 3.490 | USD 523.500 | USD 6,28M |
| Ano 3 | 300 | USD 3.990 | USD 1,197M | USD 14,36M |

**Driver:** 1 cliente de manufatura médio porte
com 50 equipamentos + integração SAP + carbono realtime
= USD 1.990–3.990/mês garantido + upsell natural
para Carbono (#17), ESG (#16) e SAP Pack (#46–#48).

**Portfólio total após implementação: 63 agentes.**

---

*Documento gerado em 2026-06-24*
*Implementar com DeepSeek após Enterprise Connectors (#60–#62)*
*Canal adicional: NVIDIA NGC Catalog — programa de parceiros gratuito*
*Contato NVIDIA Partner: https://www.nvidia.com/en-us/about-nvidia/partners/*
