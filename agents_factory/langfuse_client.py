# AgentsFactory/agents_factory/langfuse_client.py
"""
Langfuse client: load env vars and fetch prompts by name/version.
"""


from langfuse import Langfuse
import os
from dotenv import load_dotenv

from user_data.config import ENV_PATH

load_dotenv(ENV_PATH)

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

def get_prompt(name: str, version: str | None = None) -> str:
    """
    Fetch prompt from Langfuse by name (and optional version)
    """
    try:
        if version:
            prompt = langfuse.get_prompt(name, version=version)
        else:
            prompt = langfuse.get_prompt(name)  # latest version
        return prompt
    except Exception as e:
        raise RuntimeError(f"Failed to fetch prompt '{name}' from Langfuse: {e}")