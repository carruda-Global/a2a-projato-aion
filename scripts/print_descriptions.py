from PIL import Image
import os

folder = r"C:\Users\crist\Projetos\A2A - Projato Econosystens 2.0\mensagens e fotos debug"

descricoes = {
    "01_dashboard_principal.png": (
        "Dashboard principal do EcoSystem AEC + Regulatory exibindo todos os 27 agentes de IA online, "
        "incluindo nucleo AEC (Spec Analyst, Procurement, Inventory, Logistics, Field Execution), "
        "agentes especializados, conformidade AEC, regulatorios (NR-1, Tributario, LGPD, ESG, Carbono, "
        "Escopo 3, Canal de Denuncias, Igualdade Salarial, Anticorrupcao) e integracao Microsoft."
    ),
    "02_agente_nr1_psicossocial.png": (
        "Agente NR-1 Psicossocial realizando inventario de riscos ocupacionais com identificacao de "
        "fatores criticos como sobrecarga de trabalho (85%), assedio moral (92%), falta de autonomia, "
        "pressao por metas e jornada extensa. Plano de acao com 8 recomendacoes prioritarias. "
        "Conforme Portaria MTE 1.419/2024."
    ),
    "03_relatorio_esg.png": (
        "Relatorio ESG IFRS S1/S2 com diagnostico completo: Ambiental (emissoes Escopo 1: 45.2 tCO2e, "
        "Escopo 2: 120.8 tCO2e), Social (230 funcionarios, 34% diversidade, 1.200h treinamento) e "
        "Governanca (82% compliance, 12 politicas, 4 auditorias/ano). Pontuacao B+ (76/100). "
        "Resolucao CVM 193/2023."
    ),
    "04_canal_denuncias.png": (
        "Canal de Denuncias com painel de gestao completo: 15 denuncias recebidas, 11 resolvidas (73%), "
        "4 em andamento. Casos: assedio moral, conflito de interesses, vazamento de dados e favoritismo. "
        "Prazo medio de resposta de 48h. Canal anonimo conforme Lei 14.457/2022 e CIPA."
    ),
    "05_inventario_carbono.png": (
        "Inventario de Carbono completo conforme GHG Protocol e SBCE: Escopo 1 (45.2 tCO2e - combustiveis, "
        "veiculos), Escopo 2 (120.8 tCO2e - energia eletrica), Escopo 3 (385.6 tCO2e - fornecedores, "
        "residuos, transporte). Total: 551.6 tCO2e. Meta de reducao de 30% ate 2030. "
        "Lei 15.042/2024."
    ),
}

print("Descricoes para as 5 screenshots do Microsoft Marketplace:\n")
for fname, desc in descricoes.items():
    img_path = os.path.join(folder, fname)
    if os.path.exists(img_path):
        img = Image.open(img_path)
        print(f"[{fname}] ({img.size[0]}x{img.size[1]})")
    else:
        print(f"[{fname}] (arquivo nao encontrado)")
    print(desc)
    print()
