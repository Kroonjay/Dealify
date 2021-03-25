
from dealify_worker import DealifyWorker
import pprint as pp
import asyncio
import json
from datetime import datetime
from config import DEALIFY_DB_CREDS
from models import DealifySearchTaskIn
from database_helpers import create_dealify_search_task, read_dealify_search_task_by_id, connect_dealify_db, disconnect_dealify_db
dst_in = DealifySearchTaskIn(task_name="Set Craigslist Queries",
                             task_type=3)


# async def test_create_craigslist_site():
#     conn = await connect_dealify_db(DEALIFY_DB_CREDS)

#     await create_dealify_search_task(dst_in, conn)
#     dst = await read_dealify_search_task_by_id(2, conn)
#     # dst = await start_next_dealify_search_task(dst.task_id, conn)
#     print(dst.json())
#     disconnect_dealify_db(conn)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_create_craigslist_site())

dw = DealifyWorker()
dw.work()
