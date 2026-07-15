from typing import Any
from src.clusters.all_agents import (
    PlannerAgent, DemandForecastAgent, SetupOptimizer, InventoryAgent,
    CapacityAnalyst, ResourceManager, EnergyOptimizer, OEEMonitor, MaintenanceAgent,
    RoutePlanner, FleetManager, DeliveryPredictor, LoadController, SupplierAnalyst,
    PurchaseManager, WarehouseController, ReturnsManager, CostAnalyst,
    VisualInspector, StatisticalAnalyst, NonConformanceManager, RootCauseAnalyst,
    CertificationManager, TestOptimizer, ComplaintAnalyst, TraceabilityManager, ImprovementAgent,
)
from src.agents.onboarding_funcionarios import OnboardingFuncionariosAgent
from src.agents.atendimento_cliente_ptbr import AtendimentoClientePTBRAgent
from src.agents.conciliacao_financeira import ConciliacaoFinanceiraAgent


CLUSTER_PRODUCTION = {
    "planner_master": PlannerAgent,
    "demand_forecaster": DemandForecastAgent,
    "setup_optimizer": SetupOptimizer,
    "inventory_controller": InventoryAgent,
    "capacity_analyst": CapacityAnalyst,
    "resource_manager": ResourceManager,
    "energy_optimizer": EnergyOptimizer,
    "oee_monitor": OEEMonitor,
    "maintenance_agent": MaintenanceAgent,
}

CLUSTER_LOGISTICS = {
    "route_planner": RoutePlanner,
    "fleet_manager": FleetManager,
    "delivery_predictor": DeliveryPredictor,
    "load_controller": LoadController,
    "supplier_analyst": SupplierAnalyst,
    "purchase_manager": PurchaseManager,
    "warehouse_controller": WarehouseController,
    "returns_manager": ReturnsManager,
    "cost_analyst": CostAnalyst,
}

CLUSTER_QUALITY = {
    "visual_inspector": VisualInspector,
    "statistical_analyst": StatisticalAnalyst,
    "nonconformance_manager": NonConformanceManager,
    "root_cause_analyst": RootCauseAnalyst,
    "certification_manager": CertificationManager,
    "test_optimizer": TestOptimizer,
    "complaint_analyst": ComplaintAnalyst,
    "traceability_manager": TraceabilityManager,
    "improvement_agent": ImprovementAgent,
}

CLUSTER_CROSS_SELL = {
    "onboarding_funcionarios": OnboardingFuncionariosAgent,
    "atendimento_cliente_ptbr": AtendimentoClientePTBRAgent,
    "conciliacao_financeira": ConciliacaoFinanceiraAgent,
}

CLUSTERS = {
    "production": CLUSTER_PRODUCTION,
    "logistics": CLUSTER_LOGISTICS,
    "quality": CLUSTER_QUALITY,
    "cross_sell": CLUSTER_CROSS_SELL,
}
