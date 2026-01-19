from pathlib import Path
import importlib.util
import sys

class UserData:
    def __init__(self, package_root: Path):
        """
        Initializes UserData pointing to the internal package structure.
        :param package_root: Should point to the 'agents_factory' directory.
        """
        self.package_root = package_root
        self._config = None
        self._custom_tools = None
        
        # Define the internal path to user_data templates
        self.internal_user_data_path = self.package_root / "templates" / "user_data"

    def _load_module(self, file_path: Path, module_name: str):
        """
        Dynamically loads a Python module from a specific file path.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Required module file not found at: {file_path}")
            
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for module {module_name}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    @property
    def config(self):
        if self._config is None:
            # Points to agents_factory/templates/user_data/config.py
            config_path = self.internal_user_data_path / "config.py"
            self._config = self._load_module(config_path, "user_data_config")
        return self._config

    @property
    def custom_tools_registry(self) -> dict:
        if self._custom_tools is None:
            # Points to agents_factory/templates/user_data/custom_tools/custom_tools_registry.py
            registry_path = self.internal_user_data_path / "custom_tools" / "custom_tools_registry.py"
            module = self._load_module(registry_path, "user_custom_tools_registry")
            self._custom_tools = getattr(module, "CUSTOM_TOOLS_REGISTRY", {})
        return self._custom_tools

# --- Singleton Logic ---

_USER_DATA_INSTANCE = None

def get_user_data() -> UserData:
    """
    Returns a singleton instance of UserData, 
    automatically locating the package root.
    """
    global _USER_DATA_INSTANCE
    if _USER_DATA_INSTANCE is None:
        # Path(__file__) is .../agents_factory/user_data_loader.py
        # .parent is .../agents_factory/
        package_root = Path(__file__).parent.resolve()
        _USER_DATA_INSTANCE = UserData(package_root)
    return _USER_DATA_INSTANCE