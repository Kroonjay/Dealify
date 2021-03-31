
from dealify_worker import DealifyWorker
import pprint as pp
import asyncio
import json
from datetime import datetime
from config import DEALIFY_DB_CREDS
from models import DealifySearchTaskIn, DealifyWorkerIn, DealifyWorkerTaskConfig
from dealify_helpers import create_queries_for_new_searches
from database_helpers import read_dealify_worker_by_id, create_dealify_worker, read_new_dealify_search_ids, create_dealify_search_task, read_dealify_search_task_by_id, connect_dealify_db, disconnect_dealify_db
dst_in = DealifySearchTaskIn(task_name="Set Craigslist Queries",
                             task_type=3)

dwtc_in = DealifyWorkerTaskConfig(allowed_task_types=[1, 2])

dw_in = DealifyWorkerIn(worker_name="Craigslist-01",
                        task_config=dwtc_in.json())


# async def test_create_craigslist_site():
#     conn = await connect_dealify_db(DEALIFY_DB_CREDS)
#     result = await read_dealify_worker_by_id(1, conn)
#     print(result.json())
#     print(result.task_config.allowed_task_types)
#     # new_search_ids = await read_new_dealify_search_ids(conn)
#     # dst = await read_dealify_search_task_by_id(2, conn)
#     # dst = await start_next_dealify_search_task(dst.task_id, conn)
#     disconnect_dealify_db(conn)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_create_craigslist_site())

dw = DealifyWorker()
dw.work()
