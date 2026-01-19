# AgentsFactory/agents_factory/built_in_tools/tools_registry.py
"""
Registry of all available tools, combining built-in and custom tools.
"""

from pathlib import Path
from agents_factory.user_data_loader import get_user_data

USER_DATA = get_user_data()

CUSTOM_TOOLS_REGISTRY = USER_DATA.custom_tools_registry

from typing import Dict, Callable
from agents_factory.built_in_tools.built_in_tools import (
    tool_uuid4,
    tool_now,
    tool_today,
    tool_random_choice,
    tool_random_int,
    tool_safe_get,
    tool_iso_timestamp,
)


TOOLS_REGISTRY: Dict[str, Callable] = {
    # ===== Core / Time =====
    "uuid4": tool_uuid4,
    "now": tool_now,
    "today": tool_today,
    "iso_timestamp": tool_iso_timestamp,

    # ===== Utils =====
    "random_choice": tool_random_choice,
    "random_int": tool_random_int,
    "safe_get": tool_safe_get,

    # ===== Custom tools =====
    **CUSTOM_TOOLS_REGISTRY
}