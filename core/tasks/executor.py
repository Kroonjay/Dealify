from core.tasks.task_map import map_task, map_task_config
from pydantic import parse_raw_as
import logging


def validate_task_config(task):

    task_config_base = map_task_config(task.task_type)
    if not task_config_base:
        logging.error("NO task Config Base")
        return None
    if not task.task_config:
        logging.info("No Custom Task Config Specified, Using Default")
        return task_config_base()  # If no custom task_config specified with task, use Default
    try:
        task_config = parse_raw_as(task_config_base, task.task_config)
        logging.info(f"Task Config Validated Successfully")
        return task_config
    except ValidationError as ve:
        logging.error(f"Task Config Validation Failed - Data: {ve.json()}")
        # log_error(
        #     log_messages().search_worker.error_validate_task_config_ve, data=ve.json())
        return task_config_base()


async def run_dealify_task(task, conn):
    task_func = map_task(task.task_type)
    if not task_func:
        # log_error(
        #     log_messages().search_worker.error_execute_search_task_unfamiliar_task_type)
        logging.error(
            f"Failed to Run Dealify Task - No Task Func - Task: {task}")
        return None
    task_config = validate_task_config(task)
    if task_config:
        await task_func(conn, task_config)
    else:
        await task_func(conn)
    logging.info("Finished Task")
    # log(log_messages().search_worker.log_execute_search_task_finished)
    return True
