# AgentsFactory/agents_factory/langfuse_client.py
"""
Langfuse client: load env vars and fetch prompts by name/version.
"""


import sys
from langfuse import Langfuse
import os
from dotenv import load_dotenv

import logging

logger = logging.getLogger("LANGFUSE_CLIENT")


from agents_factory.user_data_loader import get_user_data

USER_DATA = get_user_data()
ENV_PATH = USER_DATA.config.ENV_PATH

load_dotenv(ENV_PATH)

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

def get_prompt(name: str, version: str | None = None) -> str:
    try:
        if version:
            return langfuse.get_prompt(name, version=version)
        return langfuse.get_prompt(name)

    except Exception as e:
        msg = str(e).lower()

        if "401" in msg or "403" in msg:
            reason = "AUTH ERROR - Langfuse API keys invalid or no permission"
        elif "404" in msg or "not found" in msg:
            reason = f"PROMPT NOT FOUND - '{name}'"
        elif "connection" in msg or "timeout" in msg:
            reason = "CONNECTION ERROR - Langfuse host unreachable"
        else:
            reason = "UNKNOWN LANGFUSE ERROR"

        logger.critical("FATAL | %s", reason, exc_info=False)
        sys.exit(1)