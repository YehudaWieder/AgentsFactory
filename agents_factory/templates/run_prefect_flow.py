# AgentsFactory/templates/flow.py

from pathlib import Path
from dotenv import load_dotenv

# 1. Get the absolute path to your local test/user_data folder
# This ensures we point to YOUR local tools
current_dir = Path(__file__).parent.resolve()
local_user_data_path = current_dir / "user_data"

# 2. Force the singleton to initialize with YOUR path first
from agents_factory.user_data_loader import get_user_data
user_data = get_user_data(base_path=local_user_data_path)

from user_data.config import AGENT_CONFIG_DEFAULT_PATH

from prefect import flow
from agents_factory.prefect.tasks import (
    create_factory_task,
    run_pipeline_task,
)

ENV_PATH = user_data.config.ENV_PATH

load_dotenv(ENV_PATH)

user_input = ""  # Placeholder for user input

@flow(name="AgentsFactory Pipeline")
async def agents_flow(
    config_path: str | Path = AGENT_CONFIG_DEFAULT_PATH,
    user_input: str = user_input,
):
    factory = create_factory_task(config_path)
    result = await run_pipeline_task(factory, user_input)
    return result


if __name__ == "__main__":
    agents_flow.serve(name="agents-factory-deployment")