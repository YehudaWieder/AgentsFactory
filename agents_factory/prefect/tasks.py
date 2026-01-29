# AgentsFactory/agents_factory/prefect/tasks.py

from prefect import task, get_run_logger

from agents_factory.main import create_pipeline


@task
def create_factory_task(config_path):
    logger = get_run_logger()
    logger.info("Creating AgentsFactory")
    return create_pipeline(config_path)


@task(persist_result=False)
async def run_pipeline_task(factory, user_input: str):
    logger = get_run_logger()
    logger.info("Running AgentsFactory pipeline")
    return await factory.run_pipeline(user_input)