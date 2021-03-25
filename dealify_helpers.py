from pydantic import ValidationError
import logging
from models import DealifySearch, CraigslistOverdueSearchTaskConfig, SearchConfig, CraigslistConfig, LocationRestrictionConfig, PriceRestrictionConfig, DealifySearchTaskTypes
from config import WORKER_LOG_FORMAT, DEV_MODE, BASE_LOGGER_NAME, WORKER_LOG_LEVEL, WORKER_LOG_FILE, SEARCH_CONFIG_CL_CONFIG_KEY_NAME, SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME, SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME
from dealify_utils import log, log_debug, log_error, log_messages
import json
from craigslist_helpers import work_overdue_craigslist_queries


def get_default_search_task_config(task):
    if not task.task_type:
        log_error(
            log_messages().search_worker.error_default_task_config_none_task_type)
        return None
    if task.task_type not in [task_type.value for task_type in DealifySearchTaskTypes]:
        log_data = f"Task Type: {task.task_type}"
        log_error(log_messages().search_worker.error_default_task_config_unfamiliar_task_type, data=log_data
                  )
        return None
    if task.task_type == DealifySearchTaskTypes.OverdueCraigslistQueries.value:
        return CraigslistOverdueSearchTaskConfig()


def validate_search_task_config(task):
    if not task.task_config:
        get_default_search_task_config(task)
    if task.task_type == DealifySearchTaskTypes.OverdueCraigslistQueries.value:
        try:
            task_config = CraigslistOverdueSearchTaskConfig(
                **json.loads(task.task_config))
            return task_config
        except ValidationError as ve:
            log_error(
                log_messages().search_worker.error_validate_task_config_ve, ve.json())
            return None


async def execute_dealify_search_task(task, conn):
    if task.task_type not in [task_type.value for task_type in DealifySearchTaskTypes]:
        log_data = f"Task Type: {task.task_type}"
        log_error(log_messages(
        ).search_worker.error_execute_search_task_unfamiliar_task_type, log_data)
        return None
    if task.task_type == DealifySearchTaskTypes.OverdueCraigslistQueries.value:
        task_config = validate_search_task_config(task)
        if not task_config:
            log_error(
                log_messages().search_worker.error_validate_task_config_no_task_config)
            return None
        log_data = f"Task ID: {task.task_id}"
        log(log_messages().search_worker.log_execute_search_task_started, log_data)
        await work_overdue_craigslist_queries(conn, **task_config.dict(exclude_unset=True))
        log(log_messages().search_worker.log_execute_search_task_finished, log_data)
        return True


def start_logger(log_level=WORKER_LOG_LEVEL, dev=DEV_MODE):
    logging.basicConfig(level=log_level,
                        filename=WORKER_LOG_FILE,
                        filemode='w')
    root_logger = logging.getLogger()
    fh = logging.FileHandler(WORKER_LOG_FILE)
    root_logger.addHandler(fh)
    if dev:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter(WORKER_LOG_FORMAT)
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)
    base_logger = logging.getLogger(BASE_LOGGER_NAME)
    return base_logger
