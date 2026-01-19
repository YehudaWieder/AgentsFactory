"""
Registry of all available tools, combining built-in and custom tools.
"""

from typing import Dict, Callable
from agents_factory.user_data_loader import get_user_data
from agents_factory.built_in_tools.built_in_tools import (
    tool_uuid4,
    tool_now,
    tool_today,
    tool_random_choice,
    tool_random_int,
    tool_safe_get,
    tool_iso_timestamp,
)

def get_tools_registry() -> Dict[str, Callable]:
    """
    Dynamically combines built-in tools with the current custom tools from USER_DATA.
    """
    # Always fetch the current state of the singleton
    user_data = get_user_data()
    custom_tools = user_data.custom_tools_registry

    # Define built-in tools
    registry = {
        # ===== Core / Time =====
        "uuid4": tool_uuid4,
        "now": tool_now,
        "today": tool_today,
        "iso_timestamp": tool_iso_timestamp,

        # ===== Utils =====
        "random_choice": tool_random_choice,
        "random_int": tool_random_int,
        "safe_get": tool_safe_get,
    }

    # Merge with custom tools (User's tools will override built-ins if names match)
    registry.update(custom_tools)
    
    return registry

# For backward compatibility, you can keep a reference, 
# but it's better to call the function in your validation logic.
TOOLS_REGISTRY = get_tools_registry()