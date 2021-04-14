from core.database.db_helpers import run_sproc
from core.database.sprocs import set_overdue_craigslist_queries_sproc
import asyncio
import logging


@asyncio.coroutine
async def run_task_set_overdue_craigslist_queries(pool):
    row = await run_sproc(pool, set_overdue_craigslist_queries_sproc)
    if row:
        overdue_query_count = row[0]
    else:
        overdue_query_count = 0
    logging.info(
        f"Set Overdue Craigslsit Queries Completed - {overdue_query_count} Total Overdue Queries")
    return overdue_query_count
