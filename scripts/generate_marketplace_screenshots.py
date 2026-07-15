from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"C:\Users\crist\Projetos\A2A - Projato Econosystens 2.0\marketplace-integration\microsoft\screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)
W, H = 1280, 720

def draw_card(draw, x, y, w, h, color, text_lines):
    draw.rounded_rectangle((x, y, x+w, y+h), radius=8, fill="#1e293b", outline=color)
    for i, (label, value) in enumerate(text_lines):
        draw.text((x+12, y+10+i*22), label, fill="#94a3b8")
        draw.text((x+12, y+28+i*22), value, fill="#e2e8f0")

def create_1_dashboard():
    img = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((20, 10, 1260, 50), 8, "#1e293b")
    draw.text((40, 22), "EcoSystem AEC + Regulatory - 27 Agentes de IA", fill="#38bdf8")
    agents = ["Spec Analyst", "Procurement", "Inventory", "Logistics", "Field Exec",
              "BIM Coord", "Requirements", "Engineering", "Synopsis", "Photo Intel",
              "RFI", "Compliance", "NR-1", "Tributario", "LGPD", "ESG", "Carbono",
              "Escopo 3", "Denuncias", "Igualdade", "Anticorrupcao", "Reg Analyst",
              "Compliance PM", "Channel", "Knowledge", "Facilitator", "Dev Exp"]
    for i, name in enumerate(agents):
        col = i % 6
        row = i // 6
        x = 25 + col * 205
        y = 70 + row * 95
        color = "#10b981" if i < 12 else "#6366f1"
        draw.rounded_rectangle((x, y, x+195, y+80), 6, "#1e293b", color)
        draw.text((x+10, y+12), name, fill="#e2e8f0")
        draw.text((x+10, y+50), "Online | 0 tasks", fill="#94a3b8")
    draw.text((30, 680), "27/27 agentes ativos | v3.0.0 | DeepSeek Flash", fill="#4ade80")
    img.save(os.path.join(OUTPUT_DIR, "01_dashboard.png"), "PNG")

def create_2_nr1():
    img = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((20, 10, 1260, 50), 8, "#1e293b")
    draw.text((40, 22), "NR-1 Psicossocial - Inventario de Riscos Ocupacionais", fill="#38bdf8")
    factors = [
        ("Sobrecarga de Trabalho", "Alto", "#ef4444", 85),
        ("Assedio Moral", "Critico", "#dc2626", 92),
        ("Falta de Autonomia", "Medio", "#f59e0b", 60),
        ("Pressao por Metas", "Alto", "#ef4444", 78),
        ("Relacionamento Interpessoal", "Baixo", "#22c55e", 35),
        ("Jornada Extensa", "Alto", "#ef4444", 82),
    ]
    for i, (factor, level, color, pct) in enumerate(factors):
        y = 70 + i * 65
        draw.rounded_rectangle((40, y, 1240, y+55), 6, "#1e293b", color)
        draw.text((60, y+8), factor, fill="#e2e8f0")
        draw.text((60, y+30), f"Nivel: {level} | Score: {pct}%", fill=color)
        draw.rounded_rectangle((400, y+10, 400+int(pct*8), y+45), 4, color)
    draw.text((40, 480), "Total de riscos identificados: 14 fatores criticos", fill="#f59e0b")
    draw.text((40, 510), "Plano de acao gerado com 8 recomendacoes prioritarias", fill="#4ade80")
    draw.text((40, 540), "Base normativa: Portaria MTE 1.419/2024", fill="#94a3b8")
    img.save(os.path.join(OUTPUT_DIR, "02_nr1_psicossocial.png"), "PNG")

def create_3_esg():
    img = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((20, 10, 1260, 50), 8, "#1e293b")
    draw.text((40, 22), "ESG IFRS S1/S2 - Relatorio de Sustentabilidade", fill="#38bdf8")
    sections = [
        ("E - Ambiental", "#22c55e", [
            ("Emissoes Escopo 1", "45.2 tCO2e"),
            ("Emissoes Escopo 2", "120.8 tCO2e"),
            ("Consumo Energetico", "850 MWh"),
            ("Residuos", "12.5 t"),
        ]),
        ("S - Social", "#3b82f6", [
            ("Funcionarios", "230"),
            ("Diversidade", "34%"),
            ("Treinamentos", "1.200h"),
            ("Acidentes", "0"),
        ]),
        ("G - Governanca", "#8b5cf6", [
            ("Score Compliance", "82%"),
            ("Politicas", "12"),
            ("Auditorias", "4/ano"),
            ("Canal Denuncias", "Ativo"),
        ]),
    ]
    for i, (title, color, items) in enumerate(sections):
        x = 40 + i * 410
        draw.rounded_rectangle((x, 70, x+390, 350), 8, "#1e293b", color)
        draw.text((x+15, 85), title, fill=color)
        for j, (label, value) in enumerate(items):
            draw.text((x+15, 125+j*50), label, fill="#94a3b8")
            draw.text((x+15, 145+j*50), value, fill="#e2e8f0")
    draw.text((40, 380), "Pontuacao ESG Geral: B+ (76/100) - Resolucao CVM 193/2023", fill="#4ade80")
    draw.text((40, 410), "Recomendacoes: 5 acoes de melhoria identificadas", fill="#f59e0b")
    img.save(os.path.join(OUTPUT_DIR, "03_esg_ifrs.png"), "PNG")

def create_4_canal():
    img = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((20, 10, 1260, 50), 8, "#1e293b")
    draw.text((40, 22), "Canal de Denuncias - Portal de Integridade", fill="#38bdf8")
    draw.rounded_rectangle((40, 70, 400, 220), 8, "#1e293b", "#ef4444")
    draw.text((60, 90), "Total de Denuncias", fill="#ef4444")
    draw.text((60, 130), "15", fill="#fff")
    draw.text((60, 170), "Recebidas este mes", fill="#94a3b8")
    draw.rounded_rectangle((440, 70, 800, 220), 8, "#1e293b", "#22c55e")
    draw.text((460, 90), "Resolvidas", fill="#22c55e")
    draw.text((460, 130), "11", fill="#fff")
    draw.text((460, 170), "73% de resolucao", fill="#94a3b8")
    draw.rounded_rectangle((840, 70, 1240, 220), 8, "#1e293b", "#3b82f6")
    draw.text((860, 90), "Em Andamento", fill="#3b82f6")
    draw.text((860, 130), "4", fill="#fff")
    draw.text((860, 170), "Prazo medio: 48h", fill="#94a3b8")
    items = [("Assedio Moral", "Em investigacao", "#f59e0b"),
             ("Conflito de interesses", "Concluido", "#22c55e"),
             ("Vazamento de dados", "Concluido", "#22c55e"),
             ("Favoritismo", "Em andamento", "#3b82f6")]
    for i, (item, status, color) in enumerate(items):
        y = 240 + i * 50
        draw.rounded_rectangle((40, y, 1240, y+40), 6, "#1e293b")
        draw.text((60, y+10), item, fill="#e2e8f0")
        draw.text((1000, y+10), status, fill=color)
    draw.text((40, 500), "Base legal: Lei 14.457/2022 | CIPA | Canal anonimo", fill="#94a3b8")
    img.save(os.path.join(OUTPUT_DIR, "04_canal_denuncias.png"), "PNG")

def create_5_carbono():
    img = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((20, 10, 1260, 50), 8, "#1e293b")
    draw.text((40, 22), "Inventario de Carbono - GHG Protocol + SBCE", fill="#38bdf8")
    scopes = [
        ("Escopo 1 - Diretas", "#22c55e", "45.2 tCO2e", "Combustiveis, veiculos, refrigerantes"),
        ("Escopo 2 - Energia", "#3b82f6", "120.8 tCO2e", "Eletricidade, aquecimento"),
        ("Escopo 3 - Indiretas", "#8b5cf6", "385.6 tCO2e", "Fornecedores, residuos, transporte"),
    ]
    for i, (title, color, value, desc) in enumerate(scopes):
        y = 70 + i * 100
        draw.rounded_rectangle((40, y, 1240, y+85), 8, "#1e293b", color)
        draw.text((60, y+10), title, fill=color)
        draw.text((500, y+10), value, fill="#fff")
        draw.text((60, y+45), desc, fill="#94a3b8")
    draw.text((40, 390), "Total de emissoes: 551.6 tCO2e", fill="#4ade80")
    draw.text((40, 420), "Intensidade: 2.4 tCO2e/funcionario/ano", fill="#94a3b8")
    draw.text((40, 450), "Meta SBCE: Reducao de 30% ate 2030", fill="#f59e0b")
    draw.text((40, 480), "Lei 15.042/2024 | Conforme GHG Protocol", fill="#64748b")
    img.save(os.path.join(OUTPUT_DIR, "05_inventario_carbono.png"), "PNG")

DESCRIPTIONS = {
    "01_dashboard.png": "Dashboard principal do EcoSystem AEC + Regulatory exibindo todos os 27 agentes de IA online, incluindo nucleo AEC, agentes especializados, conformidade, regulatorios e integracao Microsoft.",
    "02_nr1_psicossocial.png": "Agente NR-1 Psicossocial realizando inventario de riscos ocupacionais com identificacao de fatores criticos como sobrecarga de trabalho, assedio moral e pressao por metas, conforme Portaria MTE 1.419/2024.",
    "03_esg_ifrs.png": "Relatorio ESG IFRS S1/S2 com diagnostico ambiental (emissoes de carbono), social (diversidade e treinamentos) e governanca (compliance e auditorias) conforme Resolucao CVM 193/2023.",
    "04_canal_denuncias.png": "Canal de Denuncias com painel de gestao mostrando total de denuncias recebidas, resolvidas e em andamento, conforme Lei 14.457/2022, com anonimato garantido.",
    "05_inventario_carbono.png": "Inventario de Carbono completo com Escopos 1, 2 e 3 (GHG Protocol) e metas de reducao SBCE, em conformidade com a Lei 15.042/2024.",
}

if __name__ == "__main__":
    create_1_dashboard()
    print("01_dashboard.png (1280x720)")
    create_2_nr1()
    print("02_nr1_psicossocial.png (1280x720)")
    create_3_esg()
    print("03_esg_ifrs.png (1280x720)")
    create_4_canal()
    print("04_canal_denuncias.png (1280x720)")
    create_5_carbono()
    print("05_inventario_carbono.png (1280x720)")
    print("\n--- Descricoes para as screenshots ---")
    for filename, desc in DESCRIPTIONS.items():
        print(f"\n{filename}:")
        print(desc)
    print("\nTodas as 5 screenshots no formato 1280x720!")
