from pydantic import ValidationError
import logging
from models import DealifySearch, DealifyWorkerStatus, CraigslistOverdueSearchTaskConfig, SearchConfig, CraigslistConfig, LocationRestrictionConfig, PriceRestrictionConfig, DealifySearchTaskTypes, DealifySources
from config import WORKER_LOG_FORMAT, DEV_MODE, BASE_LOGGER_NAME, WORKER_LOG_LEVEL, WORKER_LOG_FILE, SEARCH_CONFIG_CL_CONFIG_KEY_NAME, SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME, SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME
from dealify_utils import log, log_debug, log_error, log_messages
from database_helpers import set_dormant_dealify_search, set_overdue_craigslist_queries, read_new_dealify_search_ids, read_dealify_search_by_search_id, update_dealify_worker_status
from task_map import map_task, map_task_config
import json
from craigslist_helpers import work_overdue_craigslist_queries, create_craigslist_queries


# Legacy, Gross. Functionality now built into validate_task_config
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
    if task.task_type == DealifySearchTaskTypes.SearchOverdueCraigslistQueries.value:
        return CraigslistOverdueSearchTaskConfig()


# Legacy, Gross.  Use validate_dealify_task instead w/ task_config_map
def validate_search_task_config(task):
    if not task.task_config:
        get_default_search_task_config(task)
    if task.task_type == DealifySearchTaskTypes.SearchOverdueCraigslistQueries.value:
        try:
            task_config = CraigslistOverdueSearchTaskConfig(
                **json.loads(task.task_config))
            return task_config
        except ValidationError as ve:
            log_error(
                log_messages().search_worker.error_validate_task_config_ve, ve.json())
            return None


# Legacy, Gross.  Use run_dealify_task w/ task_map
async def execute_dealify_search_task(task, conn):
    if task.task_type not in [task_type.value for task_type in DealifySearchTaskTypes]:
        log_data = f"Task Type: {task.task_type}"
        log_error(log_messages(
        ).search_worker.error_execute_search_task_unfamiliar_task_type, log_data)
        return None
    log_data = f"Task ID: {task.task_id}"
    log(log_messages().search_worker.log_execute_search_task_started, log_data)
    task_config = validate_search_task_config(task)
    if not task_config:
        log_error(
            log_messages().search_worker.error_validate_task_config_no_task_config)
        return None
    if task.task_type == DealifySearchTaskTypes.SearchOverdueCraigslistQueries.value:

        log_data = f"Task ID: {task.task_id}"
        log(log_messages().search_worker.log_execute_search_task_started, log_data)
        await work_overdue_craigslist_queries(conn, **task_config.dict(exclude_unset=True))
    elif task.task_type == DealifySearchTaskTypes.SetOverdueCraigslistQueries.value:
        await set_overdue_craigslist_queries(conn)
    log(log_messages().search_worker.log_execute_search_task_finished, log_data)
    return True


def validate_task_config(task):

    task_config_base = map_task_config(task.task_type)
    if not task_config_base:
        log_error(
            log_messages().search_worker.error_value_is_none.format(value='Task Config'))
        return None
    if not task.task_config:
        log("No Custom Task Config Specified, Using Default")
        return task_config_base()  # If no custom task_config specified with task, use Default
    try:
        task_config = task_config_base(**json.loads(task.task_config))
        log(f"Task Config Validated Successfully")
        return task_config
    except ValidationError as ve:
        log_error(
            log_messages().search_worker.error_validate_task_config_ve, data=ve.json())
        return task_config_base()


async def run_dealify_task(task, conn):
    task_func = map_task(task.task_type)
    if not task_func:
        log_error(
            log_messages().search_worker.error_execute_search_task_unfamiliar_task_type)
        return None
    task_config = validate_task_config(task)
    if task_config:
        await task_func(conn, **task_config.dict(exclude_unset=True))
    else:
        await task_func(conn)
    log(log_messages().search_worker.log_execute_search_task_finished)
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


async def set_worker_status(worker, new_status, conn):
    log_enum_name = DealifyWorkerStatus.__name__
    if new_status not in [status.value for status in DealifyWorkerStatus]:
        log_error(
            log_messages().search_worker.error_enum_unfamiliar_type.format(enum_name=log_enum_name, new_value=new_status))
        return False

    if new_status == DealifyWorkerStatus.Error.value:
        await update_dealify_worker_status(worker.worker_id, DealifyWorkerStatus.Error.value, conn)
        log(log_messages().search_worker.log_enum_update_finished.format(
            enum_name=enum_name, new_value=new_status, old_value=worker.worker_status))
        return True

    if worker.worker_status == DealifyWorkerStatus.Killed.value:
        if new_status == DealifyWorkerStatus.Dormont.value:
            await update_dealify_worker_status(worker.worker_id, DealifyWorkerStatus.Dormont.value, conn)
            log(log_messages().search_worker.log_enum_update_finished.format(
                enum_name=log_enum_name, new_value=new_status, old_value=worker.worker_status))
            return True

        else:
            log_error(log_messages().search_worker.error_enum_illegal_option.format(
                enum_name=enum_name, new_value=new_status, old_value=worker.worker_status))
            return False

    if new_status == DealifyWorkerStatus.Dormont.value:
        if worker.worker_status == DealifyWorkerStatus.Running.value:
            await update_dealify_worker_status(worker.worker_id, DealifyWorkerStatus.Dormont.value, conn)
            log(log_messages().search_worker.log_enum_update_finished.format(
                enum_name=log_enum_name, new_value=new_status, old_value=worker.worker_status))
            return True

        else:
            log_error(log_messages().search_worker.error_enum_illegal_option.format(enum_name=log_enum_name,
                                                                                    new_value=new_status, old_value=worker.worker_status))
    elif new_status == DealifyWorkerStatus.Running.value:
        if worker.worker_status == DealifyWorkerStatus.Started.value:
            await update_dealify_worker_status(worker.worker_id, DealifyWorkerStatus.Running.value, conn)
            log(log_messages().search_worker.log_enum_update_finished.format(
                enum_name=log_enum_name, new_value=new_status, old_value=worker.worker_status))
            return True
        else:
            log_error(log_messages().search_worker.error_enum_illegal_option.format(
                enum_name=log_enum_name, new_value=new_status, old_value=worker.worker_status))
    elif new_status == DealifyWorkerStatus.Started.value:
        if worker.worker_status == DealifyWorkerStatus.Dormont.value:
            await update_dealify_worker_status(worker.worker_id, DealifyWorkerStatus.Started.value, conn)
            log(log_messages().search_worker.log_enum_update_finished.format(
                enum_name=log_enum_name, new_value=new_status, old_value=worker.worker_status))
            return True
    elif new_status == DealifyWorkerStatus.Killed.value:
        await update_dealify_worker_status(worker.worker_id, DealifyWorkerStatus.Killed.value, conn)
        log(log_messages().search_worker.log_enum_update_finished.format(
            enum_name=log_enum_name, new_value=new_status, old_value=worker.worker_status))
        return True
    else:
        log_error(log_messages().search_worker.error_enum_invalid_option.format(
            enum_name=log_enum_name, new_value=new_status, old_value=worker.worker_status))
    return False
