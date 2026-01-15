# AgentsFactory/agents_factory/factory.py
"""
AgentsFactory core: initialize agents, resolve tools/prompts, run pipelines.
"""

import logging
from typing import Dict, List, Any, Callable, Optional

from pydantic_ai import Agent
from langfuse import get_client, observe

from agents_factory.factory_utils import make_agent_tool, normalize_result
from agents_factory.config_models import AgentConfig
from agents_factory.config_loader import EnhancedCompiledConfig

langfuse = get_client()

# --- Core factory class ---
class AgentsFactory:
    def __init__(
        self,
        enhanced_config: EnhancedCompiledConfig,
        logger: Optional[logging.Logger] = None,
    ):
        self.enhanced = enhanced_config
        self.logger = logger or logging.getLogger(__name__)

        self._models: Dict[str, Any] = {}
        self._agents: Dict[str, Agent] = {}

        # --- Build all agents ---
        self._build_agents()

    def _build_agents(self) -> None:
        """Build all agents from the configuration."""
        for agent_name, agent_cfg in self.enhanced.config.agents.items():
            if agent_name not in self._agents:
                self._create_agent(agent_name, agent_cfg)

    def _create_agent(self, agent_name: str, agent_cfg: AgentConfig) -> None:
        """Create a single agent with resolved tools and prompt."""
        model_name = agent_cfg.model
        self.logger.info(f"Creating agent '{agent_name}' with model '{model_name}'")

        # --- Resolve tools and sub-agents ---
        tools_callable: List[Callable] = []
        for tool_ref in agent_cfg.tools:
            if tool_ref in self.enhanced.resolved_tools:
                tools_callable.append(self.enhanced.resolved_tools[tool_ref])
            elif tool_ref in self.enhanced.config.agents:
                if tool_ref not in self._agents:
                    sub_cfg = self.enhanced.config.agents[tool_ref]
                    self._create_agent(tool_ref, sub_cfg)
                sub_agent = self._agents[tool_ref]
                wrapper = make_agent_tool(sub_agent, tool_ref, self.logger)
                tools_callable.append(wrapper)
            else:
                raise ValueError(f"Invalid tool reference '{tool_ref}' in agent '{agent_name}'")

        # --- Resolve system prompt ---
        system_prompt = self.enhanced.resolved_prompts.get(agent_cfg.prompt)
        if not system_prompt:
            raise KeyError(f"Missing resolved prompt '{agent_cfg.prompt}' for agent '{agent_name}'")

        # --- Instantiate and store agent ---
        agent_instance = Agent(
            model=model_name,
            tools=tools_callable,
            system_prompt=system_prompt,
            name=agent_name,
        )

        agent_instance.output_format = getattr(agent_cfg, "output_format", "str").lower()

        setattr(self, agent_name, agent_instance)
        self._agents[agent_name] = agent_instance

        self.logger.info(
        f"Agent '{agent_name}' initialized with model '{model_name}' "
        f"and output_format: '{agent_instance.output_format}'"
        )

    # --- Pipeline execution ---
    @observe(name="Travel Planning Pipeline")
    async def run_pipeline(self, user_input: str = "") -> str:
        if not self.enhanced.config.pipeline:
            raise RuntimeError("No pipeline defined in configuration")

        self.logger.info(f"Starting pipeline: {self.enhanced.config.pipeline}")
        current_input = user_input

        for agent_name in self.enhanced.config.pipeline:
            if agent_name not in self._agents:
                raise KeyError(f"Pipeline references undefined agent: {agent_name}")

            agent = self._agents[agent_name]
            self.logger.info(f"Running agent: {agent_name}")
            try:
                result = await agent.run(current_input)
                
                current_input = normalize_result(
                    result,
                    getattr(agent.output_format, "output_format", "str").lower(),
                    self.logger
                )
                self.logger.info(f"{agent_name} completed")
            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed in pipeline: {e}")
                raise
        
        return current_input

    def list_agents(self) -> List[str]:
        """Return available agent names."""
        return list(self._agents.keys())