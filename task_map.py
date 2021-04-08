from models import DealifySearchTaskTypes, CraigslistOverdueSearchTaskConfig, CheckOldCraigslistItemDeletedTaskConfig
from craigslist_helpers import work_overdue_craigslist_queries, check_deleted_old_craigslist_items
from database_helpers import set_overdue_craigslist_queries
from dealify_tasks import create_queries_for_new_searches
import logging


task_map = {
    DealifySearchTaskTypes.SearchOverdueCraigslistQueries.value: work_overdue_craigslist_queries,
    # Placeholder, not yet supported
    DealifySearchTaskTypes.CraigslistSites.value: None,
    DealifySearchTaskTypes.SetOverdueCraigslistQueries.value: set_overdue_craigslist_queries,
    DealifySearchTaskTypes.BuildQueriesForNewDealifySearches.value: create_queries_for_new_searches,
    DealifySearchTaskTypes.CheckDeletedOldCraigslistItems: check_deleted_old_craigslist_items}

task_config_map = {
    DealifySearchTaskTypes.SearchOverdueCraigslistQueries.value: CraigslistOverdueSearchTaskConfig,
    DealifySearchTaskTypes.CheckDeletedOldCraigslistItems: CheckOldCraigslistItemDeletedTaskConfig}


def map_task_config(task_type: int):
    try:
        value = task_config_map[task_type]
        return value
    except KeyError:
        logging.error(
            f"Unable to Map Task - KeyError - Task Type: {task_type}")
        return None


def map_task(task_type: int):
    try:
        value = task_map[task_type]
        return value
    except KeyError:
        logging.error(
            f"Unable to Map Task - KeyError - Task Type: {task_type}")
        return None
