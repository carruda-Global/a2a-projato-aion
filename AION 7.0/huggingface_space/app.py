import os
import gradio as gr
import httpx

API_BASE = os.getenv("ECOSYSTEM_API", "https://engenheiro-producao-ai.onrender.com")


async def _call_agent(endpoint: str, payload: dict) -> str:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{API_BASE}{endpoint}", json=payload)
            data = resp.json()
            if isinstance(data, dict):
                lines = []
                for k, v in data.items():
                    if isinstance(v, list):
                        lines.append(f"**{k}:**")
                        for item in v:
                            lines.append(f"  • {item}" if isinstance(item, str) else f"  • {item}")
                    else:
                        lines.append(f"**{k}:** {v}")
                return "\n".join(lines)
            return str(data)
    except Exception as e:
        return f"❌ Erro: {e}\n\nTente novamente ou acesse global-engenharia.com/ecosystem"


async def diagnostico_nr1(empresa: str, num_funcionarios: int, setor: str) -> str:
    if not empresa:
        return "Por favor, informe o nome da empresa."
    return await _call_agent(
        "/mcp/regulatory/tools/nr1_psicossocial",
        {"empresa": empresa, "num_funcionarios": num_funcionarios, "setor": setor},
    )


async def check_eu_ai_act(company: str, ai_systems: str, sector: str) -> str:
    if not company:
        return "Please provide company name."
    systems = [s.strip() for s in ai_systems.split(",") if s.strip()]
    return await _call_agent(
        "/mcp/regulatory/tools/eu_ai_act",
        {"company": company, "ai_systems": systems, "sector": sector},
    )


async def csrd_assessment(company: str, sector: str, employees: int, revenue: float) -> str:
    if not company:
        return "Please provide company name."
    return await _call_agent(
        "/mcp/regulatory/tools/csrd_assessment",
        {"company": company, "sector": sector, "employees": employees, "revenue_eur_million": revenue},
    )


with gr.Blocks(
    title="EcoSystem AEC — 86 AI Compliance Agents",
    theme=gr.themes.Soft(primary_hue="green"),
    css=".footer { text-align:center; color:#666; font-size:12px; margin-top:24px }",
) as demo:
    gr.Markdown(
        """
        # 🌐 EcoSystem AEC — 86 AI Compliance Agents
        **Diagnósticos de conformidade regulatória em segundos.**
        NR-1 Psicossocial • EU AI Act • CSRD • DORA • NIS2

        > Plano completo com relatório detalhado: **[global-engenharia.com/ecosystem](https://global-engenharia.com/ecosystem)**
        """
    )

    with gr.Tab("🇧🇷 NR-1 Psicossocial"):
        gr.Markdown("Diagnóstico de riscos psicossociais conforme Portaria MTE 1.419/2024")
        with gr.Row():
            nr1_empresa = gr.Textbox(label="Nome da Empresa", placeholder="Global Match Engenharia")
            nr1_funcionarios = gr.Number(label="Nº de Funcionários", value=50, minimum=1)
        nr1_setor = gr.Textbox(label="Setor", placeholder="Indústria, Serviços, Tecnologia...")
        nr1_btn = gr.Button("🔍 Gerar Diagnóstico NR-1", variant="primary")
        nr1_output = gr.Markdown()
        nr1_btn.click(diagnostico_nr1, [nr1_empresa, nr1_funcionarios, nr1_setor], nr1_output)

    with gr.Tab("🇪🇺 EU AI Act"):
        gr.Markdown("EU AI Act readiness check — deadline agosto 2026")
        with gr.Row():
            ai_company = gr.Textbox(label="Company Name")
            ai_sector = gr.Textbox(label="Sector", placeholder="financial, healthcare, HR, retail...")
        ai_systems = gr.Textbox(
            label="AI Systems / Use Cases (comma-separated)",
            placeholder="credit scoring model, HR recruitment AI, customer chatbot...",
            lines=3,
        )
        ai_btn = gr.Button("🔍 Check EU AI Act Readiness", variant="primary")
        ai_output = gr.Markdown()
        ai_btn.click(check_eu_ai_act, [ai_company, ai_systems, ai_sector], ai_output)

    with gr.Tab("🌱 CSRD Assessment"):
        gr.Markdown("CSRD double materiality assessment — ESRS standards")
        with gr.Row():
            csrd_company = gr.Textbox(label="Company Name")
            csrd_sector = gr.Textbox(label="Sector", placeholder="manufacturing, finance, retail...")
        with gr.Row():
            csrd_employees = gr.Number(label="Employees", value=500, minimum=1)
            csrd_revenue = gr.Number(label="Revenue (€M)", value=50, minimum=0)
        csrd_btn = gr.Button("🔍 Run CSRD Assessment", variant="primary")
        csrd_output = gr.Markdown()
        csrd_btn.click(csrd_assessment, [csrd_company, csrd_sector, csrd_employees, csrd_revenue], csrd_output)

    gr.Markdown(
        """
        <div class="footer">
        EcoSystem AEC v7.0 • Global Match Engenharia de Produção •
        <a href="https://global-engenharia.com/ecosystem" target="_blank">Plano completo com 86 agentes →</a>
        </div>
        """,
        elem_classes=["footer"],
    )

if __name__ == "__main__":
    demo.launch()
