# AgentsFactory/agents_factory/config_models.py
"""
Pydantic models and validation logic for AgentsFactory configuration.
"""

from typing import Dict, List, Set

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)

from pathlib import Path
from agents_factory.user_data_loader import UserData

USER_DATA = UserData(Path.cwd() / "user_data")
CUSTOM_TOOLS_REGISTRY = USER_DATA.custom_tools_registry

from agents_factory.built_in_tools.tools_registry import TOOLS_REGISTRY

from agents_factory.config_errors import ConfigError, ConfigErrorCode

import logging

logger = logging.getLogger("CONFIG_LOADER")


class ToolRefConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    ref: str


class AgentConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    model: str
    tools: List[str] = Field(default_factory=list)
    prompt: str
    description: str = ""
    output_format: str = "str"

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        allowed = {"str", "json", "raw"}
        normalized = v.lower()
        if normalized not in allowed:
            raise ValueError(f"output_format must be one of {allowed}, got '{v}'")
        return normalized


class ConfigModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)
    version: int = 1
    prompts: Dict[str, str] = Field(default_factory=dict)
    tools: Dict[str, ToolRefConfig] = Field(default_factory=dict)
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)
    pipeline: List[str] = Field(default_factory=list)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: int) -> int:
        if v != 1:
            logger.error(f"Unsupported config version: {v}")
            raise ConfigError(ConfigErrorCode.UNSUPPORTED_VERSION, f"Config version {v} not supported")
        return v

    @field_validator("prompts")
    @classmethod
    def validate_prompts(cls, v: Dict[str, str]) -> Dict[str, str]:
        forbidden = ["{{", "}}", "{%", "%}", "{#", "#}", "${"]
        for name, prompt in v.items():
            if any(marker in prompt for marker in forbidden):
                logger.error(f"Templating detected in prompt '{name}'")
                raise ConfigError(
                    ConfigErrorCode.TEMPLATING_IN_PROMPT,
                    f"Prompt '{name}' contains forbidden templating syntax"
                )
        return v

    @field_validator("tools")
    @classmethod
    def validate_tool_refs(cls, v: Dict[str, ToolRefConfig]):
        for name, cfg in v.items():
            if cfg.ref not in TOOLS_REGISTRY and cfg.ref not in CUSTOM_TOOLS_REGISTRY:
                logger.error(f"Unknown tool reference: {cfg.ref}")
                raise ConfigError(
                    ConfigErrorCode.UNKNOWN_TOOL_REF,
                    f"Tool '{name}' references unknown tool '{cfg.ref}'"
                )
        return v

    @model_validator(mode="after")
    def full_validation(self) -> "ConfigModel":
        logger.info("Running full cross-reference validation")
        agent_names = set(self.agents.keys())
        tool_names = set(self.tools.keys())
        prompt_names = set(self.prompts.keys())

        # Validate agent references
        for agent_name, cfg in self.agents.items():
            for tool_ref in cfg.tools:
                if tool_ref not in tool_names and tool_ref not in agent_names:
                    logger.error(f"Agent '{agent_name}' references unknown tool/agent '{tool_ref}'")
                    raise ConfigError(
                        ConfigErrorCode.UNKNOWN_AGENT_REF,
                        f"Agent '{agent_name}' references unknown '{tool_ref}'"
                    )
            if cfg.prompt not in prompt_names:
                logger.error(f"Agent '{agent_name}' uses unknown prompt '{cfg.prompt}'")
                raise ConfigError(
                    ConfigErrorCode.UNKNOWN_PROMPT,
                    f"Agent '{agent_name}' uses undefined prompt '{cfg.prompt}'"
                )

        # Validate pipeline
        for step in self.pipeline:
            if step not in agent_names:
                logger.error(f"Pipeline references unknown agent '{step}'")
                raise ConfigError(
                    ConfigErrorCode.UNKNOWN_AGENT_REF,
                    f"Pipeline step '{step}' not defined"
                )

        # Detect cycles
        if self._detect_agent_cycles():
            logger.error("Cycle detected in agent dependencies")
            raise ConfigError(ConfigErrorCode.CYCLE_DETECTED, "Circular dependency detected")

        logger.info("Config model validation completed successfully")
        return self

    def _detect_agent_cycles(self) -> bool:
        graph = {
            name: [t for t in cfg.tools if t in self.agents]
            for name, cfg in self.agents.items()
        }
        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited and dfs(neighbor):
                    return True
                if neighbor in stack:
                    return True
            stack.remove(node)
            return False

        return any(dfs(node) for node in graph if node not in visited)