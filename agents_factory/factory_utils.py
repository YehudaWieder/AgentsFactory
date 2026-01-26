# AgentsFactory/agents_factory/utils.py
"""
Utility functions: normalize agent output and wrap agents as tools.
"""

# --- Utility functions ---
import json
import logging
from typing import Any, Callable

from pydantic_ai import Agent, Tool


def normalize_result(result: Any, output_format: str, logger: logging.Logger) -> str:
    """Normalize agent output according to the expected output_format defined in the agent's config."""
    output = result.data if hasattr(result, "data") else result
    if output is None:
        output = ""

    if output_format == "raw":
        return output

    if output_format == "str":
        return str(output)

    if output_format == "json":
        if isinstance(output, (dict, list)):
            return output  # already structured – no need to parse
        try:
            return json.loads(str(output))
        except json.JSONDecodeError:
            logger.warning(
                f"Agent was configured to return JSON but output is invalid. "
                f"Falling back to string. Output preview: {str(output)[:200]}"
            )
            return str(output)

    # Fallback for unknown formats – treat as string
    logger.debug(f"Unknown output_format '{output_format}', treating as 'str'")
    return str(output)

def make_agent_tool(agent: Agent, agent_name: str, logger: logging.Logger) -> Callable[..., Any]:
    """Safe async wrapper factory for sub-agents."""
    async def agent_tool(input_data: str = "") -> str:
        if not input_data or input_data.strip() == "":
            input_data = "No specific instructions provided."

        logger.info(f"[Tool] Starting sub-agent: {agent_name} with input: {input_data[:30]}...")
        try:
            result = await agent.run(input_data)
            raw_output = result.data if hasattr(result, 'data') else str(result)
            
            normalized = normalize_result(
                    raw_output,
                    getattr(agent.output_format, "output_format", "str").lower(),
                    logger
                )
            
            if normalized is None or str(normalized).lower() in ["none", "null", ""]:
                logger.warning(f"[Tool] Sub-agent {agent_name} returned None after normalization.")
                return f"Agent {agent_name} completed but produced no readable output."
        
            logger.info(f"[Tool] Sub-agent {agent_name} completed with output: {normalized[:30]}...")
            return str(normalized)
        
        except Exception as e:
            logger.error(f"Sub-agent {agent_name} failed: {str(e)}")
            return f"[Error in {agent_name}: {str(e)}]"

    return Tool(
        agent_tool,
        name=f"call_{agent_name}",
        description=f"REQUIRED STEP: Call this tool to evaluate if the destination is suitable. You must pass the weather and flight data here."
    )

