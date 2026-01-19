# AgentsFactory/agents_factory/main.py
"""
Entry point for AgentsFactory: setup logging, load config, and initialize the factory.
"""

import logging
import sys
from pathlib import Path

from pathlib import Path
from agents_factory.user_data_loader import get_user_data

USER_DATA = get_user_data(Path.cwd())

AGENT_CONFIG_DEFAULT_PATH = USER_DATA.config.AGENT_CONFIG_DEFAULT_PATH

from agents_factory.factory import AgentsFactory
from agents_factory.config_loader import load_config, enhance_compiled_config


# --- Logging setup ---
def setup_logging(level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("AGENTS_FACTORY")


# --- Pipeline creation ---
def create_pipeline(
    config_path: str | Path = AGENT_CONFIG_DEFAULT_PATH,
) -> AgentsFactory:
    logger = setup_logging()
    config_path = Path(config_path).expanduser().resolve()

    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    logger.info(f"Loading configuration from: {config_path}")

    try:
        compiled = load_config(config_path)
        enhanced = enhance_compiled_config(compiled)

        # --- Config summary ---
        logger.info("Configuration loaded and validated successfully")
        logger.info(f"Config version: {enhanced.config.version}")
        logger.info(f"Agents defined: {len(enhanced.config.agents)}")
        logger.info(f"Tools available: {len(enhanced.resolved_tools)}")
        logger.info(f"Pipeline: {enhanced.config.pipeline or 'Not defined'}")

        # --- Build factory ---
        factory = AgentsFactory(
            enhanced_config=enhanced,
            logger=logger,
        )

        logger.info("AgentsFactory system fully initialized and ready")
        logger.info(f"Available agents: {factory.list_agents()}")
        return factory

    except Exception as e:
        logger.exception(f"Failed to initialize AgentsFactory: {e}")
        sys.exit(1)
