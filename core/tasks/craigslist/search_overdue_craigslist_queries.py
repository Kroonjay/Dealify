import asyncio
import logging
from time import perf_counter
from random import randint

from core.models.task_configs.craigslist import CraigslistOverdueQueriesTaskConfig
from core.models.craigslist.craigslist_query import CraigslistQuery
from core.enums.statuses import DealifySearchStatus
from core.database.db_helpers import run_sproc, read_model, read_models
from core.database.sprocs import read_craigslist_queries_by_status_sproc, read_old_craigslist_queries_sproc, update_craigslist_query_status_sproc
from core.utils.craigslist_utils import query_craigslist_items
from core.utils.dealify_utils import read_config_key
from core.enums.config_keys import ConfigKeys


async def run_task_search_overdue_craigslist_queries(pool, config: CraigslistOverdueQueriesTaskConfig = None):
    if not config:
        config = CraigslistOverdueQueriesTaskConfig()
    retries = 0
    queries = 0
    max_queries_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_MAX_QUERIES_PER_TASK)
    max_queries = max_queries_key.config_value
    max_retries_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_QUERY_MAX_RETRIES)
    max_retries = max_queries_key.config_value
    rate_limit_sleep_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_RATE_LIMIT_SLEEP_INTERVAL)
    rate_limit_sleep_interval = rate_limit_sleep_key.config_value
    query_sleep_seconds_min_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_QUERY_SLEEP_INTERVAL_MIN)
    query_sleep_seconds_min = query_sleep_seconds_min_key.config_value
    query_sleep_seconds_max_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_QUERY_SLEEP_INTERVAL_MAX)
    query_sleep_interval_max = query_sleep_seconds_max_key.config_value
    while retries < max_retries and queries < max_queries:
        cl_query = await read_model(pool, CraigslistQuery, read_old_craigslist_queries_sproc, [DealifySearchStatus.Overdue.value, 1])
        started_at = perf_counter()
        num_items = 0
        await run_sproc(pool, update_craigslist_query_status_sproc, [cl_query.query_id, DealifySearchStatus.Running.value])
        logging.debug(
            f"Started Craigslist Query with ID: {cl_query.query_id} - Data: {cl_query.json()}")
        queries += 1
        try:
            num_items = await query_craigslist_items(cl_query, pool)
            success = True

        except ConnectionError as ce:
            retries += 1
            sleep_for = rate_limit_sleep_interval
            logging.error(
                f"ConnectionError - Sleeping for {sleep_for}s before Retrying - Data: {ce}")
            success = False
            await run_sproc(pool, update_craigslist_query_status_sproc, [cl_query.query_id, DealifySearchStatus.Overdue.value])
            await asyncio.sleep(sleep_for)
        except ConnectionResetError as cre:
            retries += 1
            sleep_for = rate_limit_sleep_interval
            logging.error(
                f"ConnectionResetError - Sleeping for {sleep_for}s before Retrying - Data: {cre}")
            success = False
            await asyncio.sleep(sleep_for)
        if success:
            new_status = DealifySearchStatus.Dormant.value
        else:
            new_status = DealifySearchStatus.Overdue.value

        await run_sproc(pool, update_craigslist_query_status_sproc, [cl_query.query_id, new_status])
        finished_at = perf_counter()
        sleep_for = randint(query_sleep_seconds_min,
                            query_sleep_interval_max)
        logging.info(
            f"Finished Craigslist Query with ID: {cl_query.query_id} - Total Items: {num_items} - Total Time: {format(finished_at - started_at, '.3f')}s - Sleeping for {sleep_for}s Before Starting Next Query")
        await asyncio.sleep(sleep_for)
