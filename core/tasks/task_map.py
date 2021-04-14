import logging

from core.enums.task_types import DealifyTaskTypes
from core.models.task_configs.craigslist import CraigslistOldDeletedItemsTaskConfig, CraigslistOverdueQueriesTaskConfig
from core.tasks.craigslist.search_overdue_craigslist_queries import run_task_search_overdue_craigslist_queries
from core.tasks.craigslist.update_old_items import run_task_old_deleted_craigslist_items
from core.tasks.craigslist.set_overdue_craigslist_queries import run_task_set_overdue_craigslist_queries


task_map = {
    DealifyTaskTypes.CraigslistSearchOverdueQueries.value: run_task_search_overdue_craigslist_queries,
    # Placeholder, not yet supported
    DealifyTaskTypes.CraigslistSites.value: None,
    DealifyTaskTypes.CraigslistSetOverdueQueries.value: run_task_set_overdue_craigslist_queries,
    DealifyTaskTypes.CraigslistSearchOldDeletedItems.value: run_task_old_deleted_craigslist_items}

task_config_map = {
    DealifyTaskTypes.CraigslistSearchOverdueQueries.value: CraigslistOverdueQueriesTaskConfig,
    DealifyTaskTypes.CraigslistSearchOldDeletedItems.value: CraigslistOldDeletedItemsTaskConfig}


def map_task_config(task_type: int):
    try:
        value = task_config_map[task_type]
        return value
    except KeyError:
        logging.error(
            f"Unable to Map Task Config - KeyError - Task Type: {task_type}")
        return None


def map_task(task_type: int):
    try:
        value = task_map[task_type]
        return value
    except KeyError:
        logging.error(
            f"Unable to Map Task - KeyError - Task Type: {task_type}")
        return None
