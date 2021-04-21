import logging

from core.database.db_helpers import read_model
from core.models.dealify.dealify_search import DealifySearch
from core.database.sprocs import read_dealify_search_by_id_sproc, update_dealify_search_config_sproc


async def update_dealify_search_config(pool, dealify_search):
    ds_db = await read_model(pool, DealifySearch, read_dealify_search_by_id_sproc, [dealify_search.search_id])
    if not ds_db:
        logging.error(
            f'Failed to Update Search - No Search to Update - Search ID: {dealify_search.search_id}')
        return None
    sc_db = ds_db.search_config
    sc_in = dealify_search.search_config
    if not sc_in:
        logging.error(
            f"Failed to Update Search Config - Input SearchConfig is None")
        return None
    update_data = sc_in.dict(exclude_defaults=True)
    if not update_data:
        logging.error(f"Failed to Update Search Config, Update Data is None")
    sc_updated = sc_db.copy(deep=True, update=update_data)
    print(f"THIS IS WHAT WILL BE UPDATED: {sc_updated.json()}")
    updated = await read_model(pool, DealifySearch, update_dealify_search_config_sproc, [dealify_search.search_id, sc_updated.json()])
    if not updated:
        logging.error(
            f"Failed to Update Search Config - Received No Rows from Update Query")
    return updated
