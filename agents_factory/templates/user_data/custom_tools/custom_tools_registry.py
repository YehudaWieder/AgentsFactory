# AgentsFactory/user_data/custom_tools/tools_registry.py
"""
Registry of all custom user-defined tools.
"""

from typing import Dict, Callable
from user_data.custom_tools.custom_tools import (
    my_tool
    )

CUSTOM_TOOLS_REGISTRY: Dict[str, Callable] = {
    "my_tool": my_tool,
}