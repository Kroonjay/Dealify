import logging

from core.enums.task_types import DealifyTaskTypes
from core.models.task_configs.craigslist import CraigslistOldDeletedItemsTaskConfig, CraigslistOverdueQueriesTaskConfig
from core.tasks.craigslist.search_overdue_craigslist_queries import run_task_search_overdue_craigslist_queries
from core.tasks.craigslist.update_old_items import run_task_old_deleted_craigslist_items
from core.tasks.craigslist.set_overdue_craigslist_queries import run_task_set_overdue_craigslist_queries
from core.tasks.google_sheets.new_dealify_search_from_sheets import run_task_create_new_dealify_searches_from_sheets
from core.tasks.craigslist.create_queries_for_new_searches import run_task_create_craigslist_queries_for_new_searches
from core.tasks.google_sheets.update_dealify_items_sheets import run_task_update_dealify_search_results_sheets
task_map = {
    DealifyTaskTypes.CraigslistSearchOverdueQueries.value: run_task_search_overdue_craigslist_queries,
    # Placeholder, not yet supported
    DealifyTaskTypes.CraigslistSites.value: None,
    DealifyTaskTypes.CraigslistSetOverdueQueries.value: run_task_set_overdue_craigslist_queries,
    DealifyTaskTypes.CraigslistQueriesForNewDealifySearches.value: run_task_create_craigslist_queries_for_new_searches,
    DealifyTaskTypes.CraigslistSearchOldDeletedItems.value: run_task_old_deleted_craigslist_items,
    DealifyTaskTypes.SheetsCreateNewSearches.value: run_task_create_new_dealify_searches_from_sheets,
    DealifyTaskTypes.SheetsUpdateSearchResults.value: run_task_update_dealify_search_results_sheets}

task_config_map = {
    DealifyTaskTypes.CraigslistSearchOverdueQueries.value: CraigslistOverdueQueriesTaskConfig,
    DealifyTaskTypes.CraigslistSearchOldDeletedItems.value: CraigslistOldDeletedItemsTaskConfig}


def map_task_config(task_type: int):
    try:
        value = task_config_map[task_type]
        return value
    except KeyError:
        logging.debug(
            f"No Task Config - KeyError - Task Type: {task_type}")
        return None


def map_task(task_type: int):
    try:
        value = task_map[task_type]
        return value
    except KeyError:
        logging.error(
            f"No Task - KeyError - Task Type: {task_type}")
        return None
