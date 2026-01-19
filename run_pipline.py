#AgentsFactory/run_pipline.py
"""
Interactive script to run the AgentsFactory pipeline with user input.
"""

import time

from langfuse import get_client

from agents_factory.main import create_pipeline

if __name__ == "__main__":
    import asyncio

    factory = create_pipeline()
    # factory = create_factory(config_path="user_data/software_feature_dev_config.yaml")

    while True:
        async def interactive_run():
            user_prompt = input("ask me..")
            res1 = await factory.run_pipeline(user_prompt)
            print("Pipeline result:", res1)

            langfuse = get_client()
            time.sleep(2)
            langfuse.flush()

            # res2 = await factory.supervisor_agent.run(user_prompt)
            # print("Supervisor result:", res2)

        asyncio.run(interactive_run())
