import sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sales.database import init_db, SessionLocal
from sales import models
from sales.monitor import SalesMonitor


def get_leads_today(db) -> int:
    hoje = datetime.utcnow().date()
    return db.query(models.Lead).filter(
        models.Lead.created_at >= hoje
    ).count()


def get_leads_week(db) -> int:
    desde = datetime.utcnow() - timedelta(days=7)
    return db.query(models.Lead).filter(
        models.Lead.created_at >= desde
    ).count()


def get_conversion_rate(db) -> float:
    total = db.query(models.Lead).count()
    if total == 0:
        return 0.0
    won = db.query(models.Deal).filter(
        models.Deal.stage == models.DealStage.CLOSED_WON.value
    ).count()
    return round(won / total * 100, 1)


def get_mrr(db) -> float:
    won = db.query(models.Deal).filter(
        models.Deal.stage == models.DealStage.CLOSED_WON.value
    ).all()
    return sum(d.value for d in won)


def get_active_customers(db) -> int:
    return db.query(models.Deal).filter(
        models.Deal.stage == models.DealStage.CLOSED_WON.value
    ).count()


def get_churn_rate(db) -> float:
    total = db.query(models.Deal).count()
    if total == 0:
        return 0.0
    lost = db.query(models.Deal).filter(
        models.Deal.stage == models.DealStage.CLOSED_LOST.value
    ).count()
    return round(lost / total * 100, 1)


def get_active_agents(db) -> int:
    return db.query(models.Activity).filter(
        models.Activity.type == "activation",
        models.Activity.created_at >= datetime.utcnow() - timedelta(days=30),
    ).count()


def get_agent_utilization(db) -> float:
    total_agents = 71
    active = get_active_agents(db)
    return round(active / max(total_agents, 1) * 100, 1)


def get_metrics() -> dict:
    init_db()
    db = SessionLocal()
    monitor = SalesMonitor()
    try:
        resumo = monitor.pipeline_summary()
        funil = monitor.funil_conversao()
        gargalos = monitor.gargalos_detalhados()

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "prospecting": {
                "today": get_leads_today(db),
                "week": get_leads_week(db),
                "total": resumo["leads"]["total"],
                "from_site": resumo["leads"]["site"],
                "from_linkedin": resumo["leads"]["linkedin"],
                "conversion_rate": get_conversion_rate(db),
            },
            "sales": {
                "revenue_month": get_mrr(db),
                "pipeline_value": resumo["pipeline"]["valor_total"],
                "active_deals": resumo["pipeline"]["deals_ativos"],
                "won_deals": resumo["pipeline"]["deals_ganhos"],
                "lost_deals": resumo["pipeline"]["deals_perdidos"],
                "active_customers": get_active_customers(db),
                "churn_rate": get_churn_rate(db),
            },
            "agents": {
                "total": 71,
                "active_last_30d": get_active_agents(db),
                "utilization_pct": get_agent_utilization(db),
            },
            "funnel": funil.get("funil", {}),
            "bottlenecks": gargalos,
        }
        return metrics
    finally:
        db.close()
        monitor.close()


def print_dashboard():
    m = get_metrics()

    print("=" * 60)
    print("  PAINEL DE CONTROLE - MAQUINA DE VENDAS AION")
    print(f"  {m['timestamp']}")
    print("=" * 60)

    p = m["prospecting"]
    print(f"\nPROSPECCAO")
    print(f"  Leads hoje:     {p['today']:5d}  (target: 30-50/dia)")
    print(f"  Leads semana:   {p['week']:5d}")
    print(f"  Total leads:    {p['total']:5d}  ({p['from_site']} site | {p['from_linkedin']} linkedin)")
    print(f"  Conv. rate:     {p['conversion_rate']:5.1f}%  (target: >2%)")

    s = m["sales"]
    print(f"\nVENDAS")
    print(f"  Receita mes:    R${s['revenue_month']:>8,.2f}")
    print(f"  Pipeline:       R${s['pipeline_value']:>8,.2f}")
    print(f"  Deals ativos:   {s['active_deals']:5d}")
    print(f"  Ganhos/Perdidos: {s['won_deals']}/{s['lost_deals']}")
    print(f"  Churn:          {s['churn_rate']:5.1f}%")

    a = m["agents"]
    print(f"\nAGENTES")
    print(f"  Total:          {a['total']:5d}")
    print(f"  Ativos (30d):   {a['active_last_30d']:5d}")
    print(f"  Utilizacao:     {a['utilization_pct']:5.1f}%")

    if m["funnel"]:
        print(f"\nFUNIL")
        for etapa, dados in m["funnel"].items():
            print(f"  {etapa.replace('_',' ').title():30s} {dados['count']:4d} ({dados['porcentagem']:5.1f}%)")

    b = m["bottlenecks"].get("gargalos", [])
    if b:
        print(f"\nGARGALOS")
        for g in b:
            print(f"  [!] {g['estagio']} (taxa: {g['taxa']})")
            print(f"      Acao: {g['acao']}")

    print("\n" + "=" * 60)
    print("  Para atualizar: python scripts/dashboard.py")
    print("=" * 60)


if __name__ == "__main__":
    print_dashboard()
