from core.models.dealify.dealify_search import DealifySearch
from core.models.craigslist.craigslist_item import CraigslistItem
from core.models.dealify.dealify_worker import DealifyWorkerModel
from core.database.db_helpers import start_pool, read_models, read_model, run_sproc
from core.database.sprocs import read_dealify_search_by_id_sproc, read_craigslist_items_by_search_id_sproc, read_old_craigslist_items_sproc, update_dealify_worker_status_sproc, read_dealify_worker_by_id_sproc
from core.configs.config import DEALIFY_DB_CREDS
from core.utils.craigslist_utils import craigslist_item_is_deleted
from worker.dealify_worker import DealifyWorker
import asyncio


async def test_func():
    pool = await start_pool(DEALIFY_DB_CREDS)
    response = await run_sproc(pool, update_dealify_worker_status_sproc, [2, 1])
    model = await read_model(pool, DealifyWorkerModel, read_dealify_worker_by_id_sproc, [2])
    print(model.json())


# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_func())
dw = DealifyWorker()
dw.run()
