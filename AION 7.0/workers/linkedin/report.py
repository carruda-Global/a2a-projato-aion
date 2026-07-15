import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sales.database import init_db, SessionLocal
from sales import models
from sales.monitor import SalesMonitor
from datetime import datetime


def ver_relatorio():
    init_db()
    monitor = SalesMonitor()
    relatorio = monitor.relatorio_completo()
    gargalos = monitor.gargalos_detalhados()
    monitor.close()

    print("=" * 60)
    print("  RELATORIO AION - MAQUINA DE VENDAS")
    print(f"  Gerado em: {relatorio['gerado_em']}")
    print("=" * 60)

    resumo = relatorio["resumo"]
    print(f"\nRESUMO")
    print(f"  Leads: {resumo['leads']['total']} total | {resumo['leads']['site']} site | {resumo['leads']['linkedin']} linkedin")
    print(f"  Pipeline: R${resumo['pipeline']['valor_total']:,.2f}")
    print(f"  Deals ativos: {resumo['pipeline']['deals_ativos']}")
    print(f"  Ganhos: {resumo['pipeline']['deals_ganhos']} | Perdidos: {resumo['pipeline']['deals_perdidos']}")

    funil_data = relatorio.get("funil", {})
    if "funil" in funil_data:
        funil = funil_data["funil"]
        print(f"\nFUNIL DE CONVERSAO")
        for etapa, dados in funil.items():
            print(f"  {etapa.replace('_',' ').title():30s} {dados['count']:4d}  ({dados['porcentagem']:5.1f}%)")
    else:
        print(f"\nFUNIL: {funil_data.get('error', 'sem dados')}")

    garg = gargalos["gargalos"]
    if garg:
        print(f"\nGARGALOS IDENTIFICADOS")
        for g in garg:
            print(f"  [!] {g['estagio']} (taxa: {g['taxa']})")
            print(f"     Problema: {g['problema']}")
            print(f"     Acao: {g['acao']}")
    else:
        print(f"\nNenhum gargalo identificado")

    print(f"\nATIVIDADES RECENTES")
    for atv in relatorio["atividades_recentes"]:
        print(f"  [{atv['tipo']:12s}] {atv['assunto'][:60]}")

    print(f"\nTENDENCIA (7 dias)")
    for dia in relatorio["tendencia_7d"]:
        barra = "#" * min(dia["leads"], 20)
        print(f"  {dia['data']} {barra} {dia['leads']} leads")

    print("\n" + "=" * 60)
    print("  Para atualizar, execute: python workers/linkedin/report.py")
    print("=" * 60)


if __name__ == "__main__":
    ver_relatorio()
