# AgentsFactory/agents_factory/templates/user_data/config.py
"""
User configuration and security constants for AgentsFactory.
"""


# --- Paths ---
ENV_PATH ="user_data/API_keys.env"

AGENT_CONFIG_DEFAULT_PATH = "user_data/agent_config.yaml"

CUSTOM_TOOLS_PATH ="user_data/custom_tools/custom_tools.py"

# --- Security constants ---
MAX_FILE_SIZE = 100 * 1024  # 100 KB
MAX_NESTING_DEPTH = 20