# AgentsFactory/agents_factory/config_loader.py
"""
Load and validate configuration, resolve tools and prompts.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import json
import yaml
import logging

from pydantic import ValidationError

from pathlib import Path
from agents_factory.user_data_loader import get_user_data

USER_DATA = get_user_data(Path.cwd())

CUSTOM_TOOLS_REGISTRY = USER_DATA.custom_tools_registry
MAX_FILE_SIZE = USER_DATA.config.MAX_FILE_SIZE
MAX_NESTING_DEPTH = USER_DATA.config.MAX_NESTING_DEPTH

from agents_factory.config_models import ConfigModel
from agents_factory.config_errors import ConfigError, ConfigErrorCode
from agents_factory.built_in_tools.tools_registry import TOOLS_REGISTRY
from agents_factory.langfuse_client import get_prompt

logger = logging.getLogger("CONFIG_LOADER")


# --- Raw file loading helpers ---
def _load_raw(path: Path) -> Dict[str, Any]:
    logger.info(f"Reading config file: {path}")
    if path.stat().st_size > MAX_FILE_SIZE:
        logger.error("Config file too large")
        raise ConfigError(ConfigErrorCode.FILE_TOO_LARGE, "Config file exceeds size limit")

    content = path.read_text(encoding="utf-8")
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            raw = yaml.safe_load(content)
        elif path.suffix.lower() == ".json":
            raw = json.loads(content)
        else:
            raise ConfigError(ConfigErrorCode.INVALID_FORMAT, f"Unsupported extension: {path.suffix}")
    except Exception as e:
        logger.exception("Failed parsing config file")
        raise ConfigError(ConfigErrorCode.INVALID_FORMAT, "Parse error") from e

    if not isinstance(raw, dict):
        raise ConfigError(ConfigErrorCode.INVALID_FORMAT, "Config root must be an object")
    return raw


def _check_nesting_depth(obj: Any, depth: int = 0) -> None:
    if depth > MAX_NESTING_DEPTH:
        logger.error("Config nesting too deep")
        raise ConfigError(ConfigErrorCode.NESTING_TOO_DEEP, "Nesting exceeds allowed depth")
    if isinstance(obj, dict):
        for value in obj.values():
            _check_nesting_depth(value, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _check_nesting_depth(item, depth + 1)


# --- Resolved configuration ---
@dataclass(frozen=True)
class CompiledConfig:
    config: ConfigModel


@dataclass(frozen=True)
class EnhancedCompiledConfig:
    config: ConfigModel
    resolved_tools: Dict[str, Any] = field(default_factory=dict)
    resolved_prompts: Dict[str, str] = field(default_factory=dict)
    agent_graph: Dict[str, List[str]] = field(default_factory=dict)


# --- Public API ---
def load_config(config_path: str | Path) -> CompiledConfig:
    path = Path(config_path).expanduser().resolve()
    logger.info(f"Loading configuration from {path}")
    raw = _load_raw(path)
    _check_nesting_depth(raw)
    try:
        config_model = ConfigModel(**raw)
    except ValidationError as e:
        logger.exception("Pydantic validation failed")
        raise ConfigError(ConfigErrorCode.INVALID_FORMAT, "Validation failed") from e

    logger.info("Configuration loaded and validated successfully")
    return CompiledConfig(config=config_model)


def enhance_compiled_config(compiled: CompiledConfig) -> EnhancedCompiledConfig:
    logger.info("Enhancing compiled configuration")
    resolved_tools = {}
    for name, cfg in compiled.config.tools.items():
        tool = TOOLS_REGISTRY.get(cfg.ref) or CUSTOM_TOOLS_REGISTRY.get(cfg.ref)
        if tool is None:
            raise ConfigError(
                ConfigErrorCode.UNKNOWN_TOOL_REF,
                f"Tool '{name}' references undefined tool '{cfg.ref}'"
            )
        resolved_tools[name] = tool

    resolved_prompts = {}
    for name, prompt_ref in compiled.config.prompts.items():
        try:
            resolved_prompts[name] = get_prompt(prompt_ref)
        except RuntimeError as e:
            logger.warning(f"Could not fetch prompt '{prompt_ref}': {e}")
            resolved_prompts[name] = prompt_ref

    logger.debug(f"Resolved {len(resolved_prompts)} prompts from Langfuse")

    logger.debug(f"Resolved {len(resolved_tools)} tools")
    return EnhancedCompiledConfig(
        config=compiled.config,
        resolved_tools=resolved_tools,
        resolved_prompts=dict(compiled.config.prompts),
        agent_graph={},
    )


if __name__ == "__main__":
    # Minimal self-test (developer sanity check)
    from tempfile import TemporaryDirectory
    import json

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.json"
        path.write_text(json.dumps({
            "version": "1.0",
            "prompts": {},
            "tools": {},
            "agents": {},
            "pipeline": [],
        }), encoding="utf-8")

        compiled = load_config(path)
        enhanced = enhance_compiled_config(compiled)

        print("OK – config_loader basic self-test passed")
