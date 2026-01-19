from pathlib import Path
import importlib.util
import sys

class UserData:
    def __init__(self, base_path: Path):
        """
        Initializes UserData pointing to the directory containing user files.
        :param base_path: Path to the directory containing config.py and custom_tools/
        """
        self.base_path = Path(base_path).resolve()
        self._config = None
        self._custom_tools = None

    def _load_module(self, file_path: Path, module_name: str):
        """
        Dynamically loads a Python module from a specific file path.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Required module file not found at: {file_path}")
            
        if module_name in sys.modules:
            del sys.modules[module_name]

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
            # Look directly in the base_path for config.py
            config_path = self.base_path / "config.py"
            self._config = self._load_module(config_path, "user_data_config")
        return self._config

    @property
    def custom_tools_registry(self) -> dict:
        if self._custom_tools is None:
            # Look for custom_tools_registry.py inside the custom_tools subfolder
            registry_path = self.base_path / "custom_tools" / "custom_tools_registry.py"
            module = self._load_module(registry_path, "user_custom_tools_registry")
            self._custom_tools = getattr(module, "CUSTOM_TOOLS_REGISTRY", {})
        return self._custom_tools

# --- Singleton Logic ---

_USER_DATA_INSTANCE = None

def get_user_data(base_path: Path = None) -> UserData:
    """
    Returns a singleton instance of UserData.
    If base_path is provided, it initializes or overrides the instance with that path.
    """
    global _USER_DATA_INSTANCE
    
    if _USER_DATA_INSTANCE is None or base_path is not None:
        if base_path is None:
            # Default internal path inside the package
            target_path = Path(__file__).parent.resolve() / "templates" / "user_data"
        else:
            # Use the provided path (e.g., from your local test folder)
            target_path = Path(base_path).resolve()
        
        _USER_DATA_INSTANCE = UserData(target_path)
        
    return _USER_DATA_INSTANCE