"""Generates a native LinkedIn carousel (Document post) from a topic — a
6-slide PDF built with reportlab (already a project dependency), uploaded via
the real LinkedIn Documents API and published as a Document post."""
import io
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

from integrations import LinkedInIntegration, LinkedInConfig
from workflows.content_bank import escolher_variacao, gerar_link_comentario


def _montar_slides(topico: dict) -> list[tuple[str, str]]:
    """6 slides: hook, problem, law, product, how-it-works, CTA."""
    return [
        (topico["produto"], f"{topico['fato'].capitalize()}."),
        ("O risco real", f"Base legal: {topico['lei']}. Ignorar isso custa mais caro do que resolver agora."),
        ("Como funciona", "1. Voce responde um questionario guiado\n2. IA extrai os fatos do seu caso\n3. Motor deterministico classifica o gap — nunca e opiniao de LLM"),
        ("Entrega", "Relatorio pronto para auditoria, plano de acao com prazos, e pontuacao de conformidade em 48h."),
        ("Preco", f"{topico['produto']}: {topico['preco']}. Sem implantacao, sem contrato longo."),
        ("Proximo passo", "Comente ou acesse o link no primeiro comentario deste post para comecar."),
    ]


def gerar_pdf_carrossel(topico: dict) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), topMargin=2.5 * cm, bottomMargin=2.5 * cm,
                             leftMargin=2 * cm, rightMargin=2 * cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("SlideTitle", parent=styles["Title"], fontSize=28, textColor=HexColor("#0d2c4c"))
    corpo_style = ParagraphStyle("SlideBody", parent=styles["Normal"], fontSize=16, leading=22, textColor=HexColor("#1e293b"))

    story = []
    for i, (titulo, corpo) in enumerate(_montar_slides(topico)):
        story.append(Paragraph(titulo, titulo_style))
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph(corpo.replace("\n", "<br/>"), corpo_style))
        if i < 5:
            story.append(PageBreak())

    doc.build(story)
    buf.seek(0)
    return buf


async def publicar_carrossel(pesos_topico: dict[str, float] | None = None) -> dict:
    variacao = await escolher_variacao(pesos_topico)
    topico = variacao["topico"]

    pdf_buf = gerar_pdf_carrossel(topico)
    filename = f"{topico['id']}_carousel.pdf"

    li_config = LinkedInConfig()
    linkedin = LinkedInIntegration(config=li_config)
    await linkedin.initialize()
    try:
        upload = await linkedin.tools.upload_document(pdf_buf.read(), filename)
        if "error" in upload:
            return {"published": False, "error": upload["error"], "combo_id": variacao["combo_id"]}

        legenda = f"{topico['fato'].capitalize()}.\n\n{topico['produto']} — {topico['lei']}.\n\nLink nos comentarios."
        result = await linkedin.tools.create_carousel_post(
            text=legenda, document_asset=upload["asset"], title=topico["produto"],
        )
        if "error" in result:
            return {"published": False, "error": result["error"], "combo_id": variacao["combo_id"]}

        await linkedin.tools.create_comment(result["post_id"], variacao["link_comentario"])
        return {
            "published": True, "post_id": result["post_id"], "url": result.get("url", ""),
            "combo_id": variacao["combo_id"], "topico": topico["id"],
        }
    finally:
        await linkedin.shutdown()
