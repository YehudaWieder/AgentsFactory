# AgentsFactory/agents_factory/templates/init_templates.py
"""
Init script to copy template user_data and run_pipeline.py to the project directory.
"""

import shutil
from pathlib import Path

def copy_templates():
    base_path = Path.cwd()
    template_dir = Path(__file__).parent
    user_data_src = template_dir / "user_data"
    run_pipeline_src = template_dir / "run_pipeline.py"
    run_prefect_flow_src = template_dir / "run_prefect_flow.py"

    # copy user_data, skip __pycache__ directories
    user_data_dest = base_path / "user_data"
    if not user_data_dest.exists():
        def ignore_pycache(dir, files):
            return ["__pycache__"] if "__pycache__" in files else []
        
        shutil.copytree(user_data_src, user_data_dest, ignore=ignore_pycache)
        print(f"Copied user_data to {user_data_dest}")
    else:
        print(f"user_data already exists at {user_data_dest}")

    # copy run_pipeline.py
    run_pipeline_dest = base_path / "run_pipeline.py"
    if not run_pipeline_dest.exists():
        shutil.copy(run_pipeline_src, run_pipeline_dest)
        print(f"Copied run_pipeline.py to {run_pipeline_dest}")
    else:
        print(f"run_pipeline.py already exists at {run_pipeline_dest}")

    # copy run_prefect_flow.py
    run_prefect_flow_dest = base_path / "run_prefect_flow.py"
    if not run_prefect_flow_dest.exists():
        shutil.copy(run_prefect_flow_src, run_prefect_flow_dest)
        print(f"Copied run_prefect_flow.py to {run_prefect_flow_dest}")
    else:
        print(f"run_prefect_flow.py already exists at {run_prefect_flow_dest}")

if __name__ == "__main__":
    copy_templates()
