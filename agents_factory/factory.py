# AgentsFactory/agents_factory/factory.py
"""
AgentsFactory core: initialize agents, resolve tools/prompts, run pipelines.
"""

import logging
from typing import Dict, List, Any, Callable, Optional
import time

from pydantic_ai import Agent, ModelSettings, UsageLimits
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
    async def run_pipeline(self, user_input: str = "") -> str:
        if not self.enhanced.config.pipeline:
            raise RuntimeError("No pipeline defined in configuration")

        langfuse = get_client()
        pipeline_name = getattr(self.enhanced.config, "pipeline_name", "AgentsFactory Pipeline")
        trace_name = f"Full {pipeline_name} Request"

        self.logger.info(f"Starting pipeline: {self.enhanced.config.pipeline}")
        current_input = user_input

        # --- Root Trace ---
        with langfuse.start_as_current_observation(
            as_type="span",
            name=trace_name,
            input={"user_input": user_input},
        ) as root_trace:

            for step_index, agent_name in enumerate(self.enhanced.config.pipeline):
                if agent_name not in self._agents:
                    raise KeyError(f"Pipeline references undefined agent: {agent_name}")

                agent = self._agents[agent_name]

                # instrumentation for all tools used by the agent
                agent.instrument_all()

                self.logger.info(f"Running agent: {agent_name}")
                start_time = time.perf_counter()
                limits = UsageLimits(request_limit=5)

                # --- Span for each Agent ---
                with langfuse.start_as_current_observation(
                    as_type="span",
                    name=f"agent:{agent_name}",
                    input={
                        "step": step_index,
                        "input": current_input,
                        "model": getattr(agent, "model", None),
                    },
                ) as agent_span:

                    try:
                        result = await agent.run(current_input, 
                            usage_limits=limits,
                            model_settings=ModelSettings(parallel_tool_calls=False)
                            )

                        output = normalize_result(
                            result,
                            getattr(agent.output_format, "output_format", "str").lower(),
                            self.logger
                        )

                        duration = time.perf_counter() - start_time
                        agent_span.update(output={"output": output, "duration_seconds": duration})

                        if output is None or (isinstance(output, str) and output.strip() == ""):
                            self.logger.warning(f"Agent '{agent.name}' returned empty output. Stopping execution.")
                            break
                        
                        current_input = output
                        self.logger.info(f"{agent_name} completed in {duration:.3f} seconds")

                    except Exception as e:
                        duration = time.perf_counter() - start_time
                        agent_span.update(error=str(e), output={"duration_seconds": duration})
                        self.logger.error(f"Agent {agent_name} failed after {duration:.3f} seconds: {e}")
                        raise

            # --- Update the final output of the root trace ---
            root_trace.update(output=current_input)

        output = current_input
        return output

    def list_agents(self) -> List[str]:
        """Return available agent names."""
        return list(self._agents.keys())