import importlib
import logging

logger = logging.getLogger(__name__)

_agent_cache: dict = {}


def load_agent(agent_id: str):
    if agent_id in _agent_cache:
        return _agent_cache[agent_id]

    try:
        module = importlib.import_module(f"src.agents.{agent_id}")
        agent = getattr(module, "agent", None)
        if agent is None:
            raise AttributeError(f"src/agents/{agent_id}.py nao tem variavel 'agent'")
        _agent_cache[agent_id] = agent
        logger.info("Agente carregado dinamicamente: %s", agent_id)
        return agent
    except ModuleNotFoundError:
        raise ValueError(f"Arquivo de agente nao encontrado: src/agents/{agent_id}.py")


def unload_agent(agent_id: str) -> None:
    _agent_cache.pop(agent_id, None)
