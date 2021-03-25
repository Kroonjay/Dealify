
from models import DealifySearchIn, DealifySearch, SearchConfig, DealifySearchTask, DealifySearchTaskIn, CraigslistOverdueSearchTaskConfig, CraigslistConfig, CraigslistQueryIn, CraigslistItemIn, SearchConfigIn
from database_helpers import start_next_dealify_search_task, read_dealify_search_task_by_id, create_dealify_search, create_dealify_search_task, connect_dealify_db, disconnect_dealify_db, model_to_json_string, create_craigslist_item, create_craigslist_query, create_craigslist_site, read_all_craigslist_site_ids, read_craigslist_subdomain_by_site_id, read_dealify_search_by_search_id, read_craigslist_site_ids_by_country, start_next_overdue_craigslist_query
from craigslist_helpers import query_craigslist_items, query_craigslist_sites, create_craigslist_queries, work_overdue_craigslist_queries
from dealify_worker import DealifyWorker
import pprint as pp
import asyncio
import json
from datetime import datetime
from config import DEALIFY_DB_CREDS
dst_in = DealifySearchTaskIn(task_name="OverdueCraigslistQueries-Test",
                             task_type=1, task_config=CraigslistOverdueSearchTaskConfig().json())

cl_config = CraigslistConfig(
    queries=['KitchenAid Range', 'Kitchenaid Stove', 'Wolf Range'], search_titles=True, category="ppa")

ds_config_in = SearchConfigIn(
    craigslist_config=cl_config.json())

ds_config = SearchConfig(max_price=6500, max_distance=500,
                         source_zip=98105, craigslist_config=cl_config)

ds_in = DealifySearchIn(search_name="Find a Range", sources=json.dumps([0]),
                        search_config=ds_config_in.json())

ds = DealifySearch(search_id=1, search_name="Test1", sources=[0],
                   search_config=ds_config)

cl_query = CraigslistQueryIn(
    search_id=1, query="Duramax", site_id=390, area='see', search_titles=True, require_image=True)

cl_item = CraigslistItemIn(item_name="2006 Duramax", price=24000, search_id=1, source_url="test.url", source_id=42069,
                           posted_at=datetime.utcnow(), is_deleted=False, has_image=True, last_updated=datetime.utcnow())


async def test_create_craigslist_site():
    conn = await connect_dealify_db(DEALIFY_DB_CREDS)
    # await create_dealify_search(ds_in, conn)
    # new_ds = await read_dealify_search_by_search_id(3, conn)
    # await query_craigslist_sites(conn)
    # await create_craigslist_queries(new_ds, conn)
    dst = DealifySearchTask()
    # dst = await read_dealify_search_task_by_id(1, conn)
    dst = await start_next_dealify_search_task(dst.task_id, conn)
    print(dst.json())
    disconnect_dealify_db(conn)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_create_craigslist_site())

dw = DealifyWorker()
dw.work()
