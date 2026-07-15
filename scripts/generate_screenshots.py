from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"C:\Users\crist\Projetos\A2A - Projato Econosystens 2.0\mensagens e fotos debug"

def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)

def create_dashboard():
    img = Image.new("RGB", (1200, 800), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (30, 20, 1170, 70), 10, "#1e293b")
    draw.text((50, 35), "EcoSystem AEC + Regulatory - Dashboard", fill="#38bdf8")
    draw.text((900, 35), "27/27 Agentes Online", fill="#4ade80")
    agents = ["Spec Analyst", "Procurement", "Inventory", "Logistics", "Field Exec",
              "BIM Coord", "Requirements", "Engineering", "Synopsis", "Photo Intel",
              "RFI", "Compliance", "NR-1", "Tributario", "LGPD", "ESG", "Carbono",
              "Escopo 3", "Denuncias", "Igualdade", "Anticorrupcao", "Reg Analyst",
              "Compliance PM", "Channel", "Knowledge", "Facilitator", "Dev Exp"]
    for i, name in enumerate(agents):
        col = i % 5
        row = i // 5
        x = 40 + col * 230
        y = 100 + row * 130
        color = "#10b981" if i < 12 else "#6366f1"
        draw_rounded_rect(draw, (x, y, x + 210, y + 110), 8, "#1e293b", color)
        draw.text((x + 15, y + 15), name, fill="#e2e8f0")
        draw.text((x + 15, y + 75), "Idle | 0 tasks", fill="#94a3b8")
    img.save(os.path.join(OUTPUT_DIR, "01_dashboard_principal.png"), "PNG")

def create_nr1():
    img = Image.new("RGB", (800, 600), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (20, 15, 780, 55), 8, "#1e293b")
    draw.text((35, 30), "NR-1 Psicossocial - Inventario de Riscos", fill="#38bdf8")
    factors = [("Sobrecarga de Trabalho", "Alto", "#ef4444"),
               ("Assedio Moral", "Critico", "#dc2626"),
               ("Falta de Autonomia", "Medio", "#f59e0b"),
               ("Pressao por Metas", "Alto", "#ef4444"),
               ("Relacionamento Interpessoal", "Baixo", "#22c55e")]
    for i, (factor, level, color) in enumerate(factors):
        y = 80 + i * 80
        draw_rounded_rect(draw, (40, y, 760, y + 65), 6, "#1e293b", color)
        draw.text((60, y + 12), factor, fill="#e2e8f0")
        draw.text((60, y + 35), f"Nivel: {level}", fill=color)
    draw.text((40, 500), "Plano de Acao: 5 recomendacoes geradas", fill="#94a3b8")
    draw.text((40, 530), "Total de riscos identificados: 12", fill="#4ade80")
    img.save(os.path.join(OUTPUT_DIR, "02_agente_nr1_psicossocial.png"), "PNG")

def create_esg():
    img = Image.new("RGB", (800, 600), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (20, 15, 780, 55), 8, "#1e293b")
    draw.text((35, 30), "ESG IFRS S1/S2 - Relatorio de Diagnostico", fill="#38bdf8")
    draw_rounded_rect(draw, (40, 80, 380, 200), 8, "#1e293b", "#22c55e")
    draw.text((60, 100), "E - Ambiental", fill="#22c55e")
    draw.text((60, 130), "Emissoes Escopo 1: 45.2 tCO2e", fill="#cbd5e1")
    draw.text((60, 160), "Emissoes Escopo 2: 120.8 tCO2e", fill="#cbd5e1")
    draw_rounded_rect(draw, (420, 80, 760, 200), 8, "#1e293b", "#3b82f6")
    draw.text((440, 100), "S - Social", fill="#3b82f6")
    draw.text((440, 130), "Funcionarios: 230", fill="#cbd5e1")
    draw.text((440, 160), "Indice de Diversidade: 34%", fill="#cbd5e1")
    draw_rounded_rect(draw, (40, 220, 380, 340), 8, "#1e293b", "#8b5cf6")
    draw.text((60, 240), "G - Governanca", fill="#8b5cf6")
    draw.text((60, 270), "Score Compliance: 82%", fill="#cbd5e1")
    draw_rounded_rect(draw, (420, 220, 760, 340), 8, "#1e293b", "#f59e0b")
    draw.text((440, 240), "Materialidade", fill="#f59e0b")
    draw.text((440, 270), "Riscos identificados: 7", fill="#cbd5e1")
    draw.text((40, 400), "Pontuacao ESG Geral: B+ (76/100)", fill="#4ade80")
    img.save(os.path.join(OUTPUT_DIR, "03_relatorio_esg.png"), "PNG")

def create_canal():
    img = Image.new("RGB", (800, 600), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (20, 15, 780, 55), 8, "#1e293b")
    draw.text((35, 30), "Canal de Denuncias - Painel de Gestao", fill="#38bdf8")
    draw_rounded_rect(draw, (40, 80, 380, 180), 8, "#1e293b", "#ef4444")
    draw.text((60, 100), "Total de Denuncias", fill="#ef4444")
    draw.text((150, 130), "15", fill="#fff", font=ImageFont.load_default())
    draw_rounded_rect(draw, (420, 80, 760, 180), 8, "#1e293b", "#22c55e")
    draw.text((440, 100), "Resolvidas", fill="#22c55e")
    draw.text((550, 130), "11", fill="#fff")
    items = [("Assedio Moral", "Em investigacao", "#f59e0b"),
             ("Conflito de interesses", "Concluido", "#22c55e"),
             ("Vazamento de dados", "Concluido", "#22c55e"),
             ("Favoritismo", "Em andamento", "#3b82f6")]
    for i, (item, status, color) in enumerate(items):
        y = 210 + i * 55
        draw_rounded_rect(draw, (40, y, 760, y + 45), 6, "#1e293b")
        draw.text((60, y + 12), item, fill="#e2e8f0")
        draw.text((580, y + 12), status, fill=color)
    draw.text((40, 460), "Ultima denuncia recebida: 24/06/2026", fill="#94a3b8")
    draw.text((40, 490), "Prazo medio de resposta: 48h", fill="#4ade80")
    img.save(os.path.join(OUTPUT_DIR, "04_canal_denuncias.png"), "PNG")

def create_carbono():
    img = Image.new("RGB", (800, 600), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (20, 15, 780, 55), 8, "#1e293b")
    draw.text((35, 30), "Inventario de Carbono - GHG Protocol", fill="#38bdf8")
    draw_rounded_rect(draw, (40, 80, 380, 200), 8, "#1e293b", "#22c55e")
    draw.text((60, 100), "Escopo 1 - Emissoes Diretas", fill="#22c55e")
    draw.text((60, 140), "45.2 tCO2e", fill="#4ade80")
    draw.text((60, 170), "Combustiveis, veiculos, refrigerantes", fill="#64748b")
    draw_rounded_rect(draw, (420, 80, 760, 200), 8, "#1e293b", "#3b82f6")
    draw.text((440, 100), "Escopo 2 - Energia", fill="#3b82f6")
    draw.text((440, 140), "120.8 tCO2e", fill="#60a5fa")
    draw.text((440, 170), "Eletricidade, aquecimento", fill="#64748b")
    draw_rounded_rect(draw, (40, 220, 760, 340), 8, "#1e293b", "#8b5cf6")
    draw.text((60, 240), "Escopo 3 - Outras Emissoes", fill="#8b5cf6")
    draw.text((60, 280), "385.6 tCO2e", fill="#a78bfa")
    draw.text((60, 310), "Fornecedores, residuos, transporte de funcionarios", fill="#64748b")
    draw.text((40, 380), "Total: 551.6 tCO2e", fill="#4ade80")
    draw.text((40, 410), "Intensidade de Carbono: 2.4 tCO2e/funcionario", fill="#94a3b8")
    draw.text((40, 440), "Meta de reducao: 30% ate 2030 (SBCE)", fill="#f59e0b")
    img.save(os.path.join(OUTPUT_DIR, "05_inventario_carbono.png"), "PNG")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    create_dashboard()
    print("01_dashboard_principal.png criado")
    create_nr1()
    print("02_agente_nr1_psicossocial.png criado")
    create_esg()
    print("03_relatorio_esg.png criado")
    create_canal()
    print("04_canal_denuncias.png criado")
    create_carbono()
    print("05_inventario_carbono.png criado")
    print("Todos os screenshots recriados!")
