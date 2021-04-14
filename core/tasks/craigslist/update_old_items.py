from core.models.task_configs.craigslist import CraigslistOldDeletedItemsTaskConfig
from core.models.craigslist.craigslist_item import CraigslistItem
from core.utils.craigslist_utils import craigslist_item_is_deleted
from core.database.db_helpers import read_model, read_models
from core.database.sprocs import set_deleted_craigslist_item_sproc, read_old_craigslist_items_sproc
import asyncio


async def craigslist_update_old_item(pool, cl_item: CraigslistItem, old_interval_days: int):
    if cl_item.is_deleted:
        return True
    deleted = await craigslist_item_is_deleted(cl_item)
    if deleted:
        updated = await read_model(pool, CraigslistItem, set_deleted_craigslist_item_sproc, [
            cl_item.item_id, deleted])
        print(updated.json())
    return


async def run_task_old_deleted_craigslist_items(pool):
    models = await read_models(pool, CraigslistItem, read_old_craigslist_items_sproc, [4, 5])
    tasks = []
    for cl_item in models:
        tasks.append(craigslist_update_old_item(
            pool=pool, cl_item=cl_item, old_interval_days=2))
    await asyncio.gather(*tasks)
