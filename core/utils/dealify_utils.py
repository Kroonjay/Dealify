import logging

from core.database.db_helpers import read_model
from core.models.dealify.dealify_search import DealifySearch
from core.database.sprocs import read_dealify_search_by_id_sproc, update_dealify_search_config_sproc, read_config_key_by_name_sproc
from core.enums.config_keys import ConfigKeys
from core.models.dealify.config_keys import ConfigKey


class NoConfigKeyException(Exception):
    '''Raised when a ConfigKey is not present in environment variables or found in Database

    Attributes:
        message -- explanation of the error
        key_name -- name of config key that was searched
    '''

    def __init__(self, key_name):
        self.key_name = key_name
        self.message = f'Failed to Load ConfigKey - Key Name: {self.key_name}'
        logging.error(self.message)


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


async def read_config_key(pool, key_name):
    if not isinstance(key_name, ConfigKeys):
        logging.error(
            f"Config Key Name must be a valid ConfigKey member - Input Type: {type(key_name)} - Input Value: {key_name}")
        return None
    config_key = await read_model(pool, ConfigKey, read_config_key_by_name_sproc, [key_name.value])
    if not config_key:
        logging.error(
            f"No Config Key Found for Key Name - Key Name: {key_name.value}")
        raise NoConfigKeyException(key_name=key_name)
    logging.debug(
        f"Successfully Read Config Key - Key Name: {config_key.key_name} - Config Value: {config_key.config_value}")
    return config_key
