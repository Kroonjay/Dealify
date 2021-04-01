from dealify_utils import log, log_debug, log_error, log_messages
from database_helpers import read_new_dealify_search_ids, read_dealify_search_by_search_id, set_dormant_dealify_search
from craigslist_helpers import create_craigslist_queries


async def create_queries_for_new_searches(conn):
    new_search_ids = await read_new_dealify_search_ids(conn)
    if not new_search_ids:
        log(log_messages().search_worker.log_build_queries_task_no_new_searches)
        return None
    log_data = f"New Searches Total: {len(new_search_ids)}"
    log(log_messages().search_worker.log_build_queries_task_started, log_data)
    for search_id in new_search_ids:
        search = await read_dealify_search_by_search_id(search_id, conn)
        log_data = f"Search ID: {search_id} - Sources: {search.sources}"
        if not search:
            log_error(log_messages(
            ).search_worker.error_build_queries_task_unknown_search_id, log_data)
            continue
        if DealifySources.Craigslist.value in search.sources:
            await create_craigslist_queries(search, conn)
        log_debug(
            log_messages().search_worker.debug_build_queries_query_finished, log_data)
    await set_dormant_dealify_search(search_id, conn)
    log(log_messages().search_worker.log_build_queries_task_finished)
    return
