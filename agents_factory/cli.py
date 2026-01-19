from pathlib import Path
import shutil
from importlib.resources import files

def init():
    target = Path.cwd() / "user_data"

    if target.exists():
        print("user_data already exists")
        return

    src = files("agents_factory").joinpath("templates/user_data")
    shutil.copytree(src, target)

    print("user_data template created")
