# AgentsFactory/agents_factory/config_errors.py
"""
Error types for configuration loading and validation.
"""
from enum import StrEnum

class ConfigErrorCode(StrEnum):
    FILE_TOO_LARGE = "CFG_001"
    NESTING_TOO_DEEP = "CFG_002"
    INVALID_FORMAT = "CFG_003"
    UNKNOWN_TOOL_REF = "CFG_004"
    UNKNOWN_AGENT_REF = "CFG_005"
    UNKNOWN_PROMPT = "CFG_006"
    CYCLE_DETECTED = "CFG_007"
    TEMPLATING_IN_PROMPT = "CFG_008"
    MISSING_VERSION = "CFG_009"
    UNSUPPORTED_VERSION = "CFG_010"

class ConfigError(Exception):
    def __init__(self, code: ConfigErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")