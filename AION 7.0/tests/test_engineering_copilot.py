"""Testes do Engineering Copilot — cobre apenas Modulo 4/5 (deterministicos,
sem banco nem LLM). Modulos 1/2/3 dependem de rede/DB e ficam para testes de
integracao numa proxima iteracao."""
from app.core.engineering.compliance_engine import avaliar_compliance
from app.core.engineering.document_generator import gerar_documento, TITULOS


def test_avaliar_compliance_identifica_norma_por_tipo_equipamento():
    equipamentos = [{"tag": "AC-01", "tipo": "Ar condicionado split", "fabricante": "Daikin"}]
    resultado = avaliar_compliance(equipamentos, normas_identificadas=[])

    normas_exigidas = {p["norma"] for p in resultado["pendencias"]}
    assert "ABNT NBR 13971" in normas_exigidas
    assert "ANVISA RDC 09/2003" in normas_exigidas
    assert "ART/CREA" in normas_exigidas  # exigencia universal, mesmo sem equipamento especifico


def test_avaliar_compliance_marca_conforme_quando_norma_ja_identificada():
    equipamentos = [{"tag": "AC-01", "tipo": "Ar condicionado split"}]
    normas_identificadas = [{"norma": "ABNT NBR 13971", "descricao": "PMOC anexado"}]
    resultado = avaliar_compliance(equipamentos, normas_identificadas)

    conformes = {c["norma"] for c in resultado["conformidades"]}
    assert "ABNT NBR 13971" in conformes
    assert resultado["score_conformidade"] > 0


def test_avaliar_compliance_sem_equipamentos_so_exige_art_crea():
    resultado = avaliar_compliance(equipamentos=[], normas_identificadas=[])
    assert len(resultado["pendencias"]) == 1
    assert resultado["pendencias"][0]["norma"] == "ART/CREA"


def test_gerar_documento_cria_docx_para_todos_os_tipos():
    projeto = {"cliente": "Cliente Teste", "local": "Unidade 1", "escopo": "Manutencao de climatizacao"}
    equipamentos = [{"tag": "AC-01", "tipo": "Ar condicionado", "fabricante": "Daikin", "modelo": "X1", "localizacao": "Sala 2"}]
    normas = [{"norma": "ABNT NBR 13971", "descricao": "PMOC"}]
    compliance = avaliar_compliance(equipamentos, normas)

    for tipo in TITULOS:
        buf = gerar_documento(tipo, projeto, equipamentos, normas, documentos=[], fotos=[],
                               compliance=compliance, licenca_premium=False)
        assert buf.getbuffer().nbytes > 0


def test_gerar_documento_tipo_invalido_gera_erro():
    import pytest
    with pytest.raises(ValueError):
        gerar_documento("tipo_inexistente", {}, [], [], [], [], {})
