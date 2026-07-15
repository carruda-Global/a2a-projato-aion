import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.memory.hybrid_memory import HybridMemory, SemanticMemory
from src.rag.text_retriever import TextRetriever
from src.rag.graph_retriever import GraphRetriever


def seed_semantic_knowledge():
    memory = HybridMemory("default")
    retriever = TextRetriever()
    graph = GraphRetriever()

    knowledge_base = {
        "oee": "Overall Equipment Effectiveness = Disponibilidade x Performance x Qualidade",
        "vrp": "Vehicle Routing Problem - Otimizacao de rotas com restricoes de janela de tempo",
        "eoq": "Economic Order Quantity = sqrt(2DS/H) onde D=demanda, S=custo pedido, H=custo armazenagem",
        "cep": "Controle Estatistico de Processo - Monitora variacao usando cartas de controle",
        "cpk": "Indice de capacidade do processo = min(USL-media, media-LSL)/(3*sigma)",
        "kaizen": "Melhoria continua baseada em pequenas mudancas incrementais",
        "5whys": "Tecnica de analise de causa raiz que pergunta 'por que' 5 vezes",
        "ishikawa": "Diagrama de causa-e-efeito (espinha de peixe) para analise de problemas",
        "pdm": "Plano de Manutencao Preventiva baseado em condicoes preditivas",
        "oee_target": "OEE de classe mundial: 85% (Disponibilidade 90% x Performance 95% x Qualidade 99.9%)",
    }

    for key, value in knowledge_base.items():
        memory.semantic.store_knowledge(key, value)
        retriever.add_document(key, value, {"type": "knowledge", "domain": "engineering"})

    graph.add_node("oee", "OEE", {"type": "metric", "category": "quality"})
    graph.add_node("vrp", "VRP", {"type": "algorithm", "category": "logistics"})
    graph.add_node("eoq", "EOQ", {"type": "formula", "category": "inventory"})
    graph.add_node("cep", "CEP", {"type": "method", "category": "quality"})
    graph.add_node("cpk", "CPK", {"type": "metric", "category": "quality"})
    graph.add_node("kaizen", "Kaizen", {"type": "methodology", "category": "continuous_improvement"})
    graph.add_edge("oee", "cep", "related_to")
    graph.add_edge("cpk", "cep", "part_of")
    graph.add_edge("kaizen", "5whys", "uses")
    graph.add_edge("ishikawa", "5whys", "complement")

    print(f"Knowledge seeded: {len(knowledge_base)} concepts")
    print(f"Documents: {retriever.size()}")
    print(f"Graph nodes: {graph.size()}")


if __name__ == "__main__":
    seed_semantic_knowledge()
