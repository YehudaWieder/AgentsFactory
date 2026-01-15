# AgentsFactory/agents_factory/built_in_tools/built_in_tools.py
"""
Common built-in tools for AgentsFactory, including UUID, date/time, random, and safe data access utilities.
"""

import logging
import random
from datetime import date, datetime, timezone
from uuid import uuid4

logger = logging.getLogger("COMMON TOOLS")

def tool_uuid4() -> str:
    value = str(uuid4())
    logger.debug(f"Generated UUID4: {value}")
    return value


def tool_now() -> datetime:
    now = datetime.now()
    logger.debug(f"Current datetime generated: {now}")
    return now


def tool_today() -> date:
    today = date.today()
    logger.debug(f"Current date generated: {today}")
    return today


def tool_random_choice(items: list):
    return random.choice(items)


def tool_random_int(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)


def tool_safe_get(data: dict, path: list, default=None):
    """
    Safely extract nested values from dict
    Example: tool_safe_get(obj, ["a", "b", "c"])
    """
    for key in path:
        if not isinstance(data, dict):
            return default
        data = data.get(key)
    return data if data is not None else default


def tool_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
