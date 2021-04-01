
from dealify_worker import DealifyWorker
import pprint as pp
import asyncio
import json
from datetime import datetime
from config import DEALIFY_DB_CREDS
from models import DealifySearchTaskIn, DealifyWorkerIn, DealifyWorkerTaskConfig, DealifySearchIn, LocationRestrictionConfig, LocationRestrictionTypes, SearchConfigIn, CraigslistConfig
from dealify_tasks import create_queries_for_new_searches
from database_helpers import read_dealify_worker_by_id, create_dealify_worker, read_new_dealify_search_ids, create_dealify_search_task, read_dealify_search_task_by_id, connect_dealify_db, disconnect_dealify_db, create_dealify_search

clc = CraigslistConfig(
    queries=["Renegade", "Can Am ATV", "Outlander"], category="sna")

lrc_in = LocationRestrictionConfig(
    restriction_type=LocationRestrictionTypes.HomeState.value, source_zip=98208)

sc_in = SearchConfigIn(
    location_restriction_config=lrc_in.json(), craigslist_config=clc.json())

dst_in = DealifySearchTaskIn(task_name="Build Queries for New Dealify Searches",
                             task_type=4)

dwtc_in = DealifyWorkerTaskConfig(allowed_task_types=[1, 3])

dw_in = DealifyWorkerIn(worker_name="Craigslist-Local",
                        task_config=dwtc_in.json())

dsi = DealifySearchIn(search_name="Find a Quad",
                      sources=json.dumps([1]), search_config=sc_in.json())


# async def test_create_craigslist_site():
#     conn = await connect_dealify_db(DEALIFY_DB_CREDS)
#     await create_dealify_search_task(dst_in, conn)
#     # await create_dealify_search(dsi, conn)
#     # result = await create_queries_for_new_searches(conn)
#     # new_search_ids = await read_new_dealify_search_ids(conn)
#     # dst = await read_dealify_search_task_by_id(2, conn)
#     # dst = await start_next_dealify_search_task(dst.task_id, conn)
#     disconnect_dealify_db(conn)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_create_craigslist_site())

dw = DealifyWorker()
dw.work()
