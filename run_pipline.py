#AgentsFactory/run_pipline.py
"""
Interactive script to run the AgentsFactory pipeline with user input.
"""

from datetime import time
from pathlib import Path

from langfuse import get_client

# 1. Get the absolute path to your local test/user_data folder
# This ensures we point to YOUR local tools
current_dir = Path(__file__).parent.resolve()
local_user_data_path = current_dir / "user_data"

# 2. Force the singleton to initialize with YOUR path first
from agents_factory.user_data_loader import get_user_data
user_data = get_user_data(base_path=local_user_data_path)

# 3. NOW import the factory. It will use the already initialized singleton.
from agents_factory.main import create_pipeline

if __name__ == "__main__":
    import asyncio

    pipeline = create_pipeline()
    # factory = create_factory(config_path="user_data/software_feature_dev_config.yaml")

    while True:
        async def interactive_run():
            user_prompt = input("ask me..")
            res1 = await pipeline.run_pipeline(user_prompt)
            print("Pipeline result:", res1)

            langfuse = get_client()
            time.sleep(2)
            langfuse.flush()

            # res2 = await factory.supervisor_agent.run(user_prompt)
            # print("Supervisor result:", res2)

        asyncio.run(interactive_run())
