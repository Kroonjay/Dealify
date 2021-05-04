from core.models.task_configs.craigslist import CraigslistOldDeletedItemsTaskConfig
from core.models.craigslist.craigslist_item import CraigslistItem
from core.utils.craigslist_utils import craigslist_item_is_deleted
from core.utils.dealify_utils import read_config_key
from core.enums.config_keys import ConfigKeys
from core.enums.statuses import DealifySearchStatus
from core.database.db_helpers import read_model, read_models
from core.database.sprocs import set_deleted_craigslist_item_sproc, read_old_craigslist_items_sproc
import asyncio
import logging


async def craigslist_update_old_item(pool, cl_item: CraigslistItem, old_interval_days: int):
    if cl_item.is_deleted:
        return True
    deleted = await craigslist_item_is_deleted(cl_item)
    if deleted:
        updated = await read_model(pool, CraigslistItem, set_deleted_craigslist_item_sproc, [
            cl_item.item_id, deleted])
        logging.debug(
            f'Successfully Deleted Old Item - Data: {updated.json()}')
    return


async def run_task_old_deleted_craigslist_items(pool):
    old_interval_days_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_ITEM_OLD_INTERVAL_DAYS)
    old_interval_days = old_interval_days_key.config_value
    max_queries_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_MAX_QUERIES_PER_TASK)
    max_queries = max_queries_key.config_value
    models = await read_models(pool, CraigslistItem, read_old_craigslist_items_sproc, [old_interval_days, max_queries])
    tasks = []
    for cl_item in models:
        tasks.append(craigslist_update_old_item(
            pool=pool, cl_item=cl_item, old_interval_days=old_interval_days))
    await asyncio.gather(*tasks)
