# user_data_loader.py
from pathlib import Path
import importlib.util
from shutil import copytree

class UserData:
    def __init__(self, base_path: Path, templates_path: Path = None):
        self.base_path = base_path
        self._config = None
        self._custom_tools = None

        # Copy templates first if base_path doesn't exist
        if templates_path and not self.base_path.exists():
            copytree(templates_path, self.base_path)

        # Now check if user_data exists
        if not self.base_path.exists():
            raise RuntimeError(
                f"user_data folder not found at {self.base_path}. "
                f"Run: agents-factory init"
            )

    def _load_module(self, file_path: Path, module_name: str):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @property
    def config(self):
        if self._config is None:
            config_path = self.base_path / "config.py"
            self._config = self._load_module(config_path, "user_data_config")
        return self._config

    @property
    def custom_tools_registry(self) -> dict:
        if self._custom_tools is None:
            registry_path = self.base_path / "custom_tools" / "custom_tools_registry.py"
            module = self._load_module(registry_path, "user_custom_tools_registry")
            self._custom_tools = getattr(module, "CUSTOM_TOOLS_REGISTRY", {})
        return self._custom_tools

# Singleton instance
_USER_DATA_INSTANCE = None

def get_user_data(base_path: Path = Path.cwd(), templates_path: Path = None) -> UserData:
    """
    Return the single instance of UserData for the project.
    Ensures templates are copied before accessing config.
    """
    global _USER_DATA_INSTANCE
    if _USER_DATA_INSTANCE is None:
        _USER_DATA_INSTANCE = UserData(base_path, templates_path)
    return _USER_DATA_INSTANCE
