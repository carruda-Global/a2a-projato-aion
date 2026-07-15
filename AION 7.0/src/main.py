import argparse
import logging
import sys
from pathlib import Path

from src.config import Settings
from src.orchestrator import Orchestrator


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Engenheiro de Producao AI - Sistema Multiagente para AEC"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Caminho para o arquivo de configuracao YAML",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ativa modo debug",
    )
    args = parser.parse_args()

    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    logger.info("Iniciando Engenheiro de Producao AI v1.0.0")

    settings = Settings(config_path=args.config)
    if args.debug:
        settings.debug = True

    errors = settings.validate()
    if errors:
        for err in errors:
            logger.warning("Configuracao pendente: %s", err)

    orchestrator = Orchestrator(settings)
    health = orchestrator.health_check()
    logger.info("Health check: %s", health)

    if health["status"] == "healthy":
        logger.info(
            "Sistema pronto. Agentes disponiveis: %s",
            ", ".join(health["agents"]),
        )
    else:
        logger.error("Sistema com problemas de saude")
        sys.exit(1)


if __name__ == "__main__":
    main()
