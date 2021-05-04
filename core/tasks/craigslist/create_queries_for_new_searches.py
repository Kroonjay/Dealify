import asyncio
import logging

from pydantic import ValidationError

from core.utils.craigslist_utils import query_unrestricted_sites
from core.utils.dealify_utils import read_config_key
from core.database.db_helpers import read_models, run_sproc, values_from_model
from core.models.dealify.dealify_search import DealifySearch
from core.database.sprocs import read_dealify_searches_by_status_sproc, update_dealify_search_status_sproc, create_craigslist_query_sproc
from core.enums.statuses import DealifySearchStatus
from core.enums.sources import DealifySources
from core.enums.config_keys import ConfigKeys
from core.models.craigslist.craigslist_query import CraigslistQueryIn


async def create_craigslist_queries_for_dealify_search(pool, dealify_search):
    if not dealify_search.search_config:
        logging.error(
            f"Failed to Create Craigslist Queries for Dealify Search - LocationRestrictionConfig is None - Search ID: {dealify_search.search_id}")
        return

    if DealifySources.Craigslist.value not in dealify_search.sources:
        logging.debug(
            f"Craigslist Not Found in Sources for Dealify Search - Skipping Creating Queries - Search ID: {dealify_search.search_id}")
        return
    cl_sites = await query_unrestricted_sites(pool, dealify_search.search_config.location_restriction_config)
    if not cl_sites:
        logging.error(
            f"No Craigslist Sites Found for Dealify Search - Search ID: {dealify_search.search_id}")
        return
    queries = dealify_search.search_config.craigslist_config.queries
    categories = dealify_search.search_config.craigslist_config.categories
    try:
        total_new_queries = len(cl_sites) * len(queries) * len(categories)
    except TypeError as te:
        logging.error(
            f"Failed to Calculate Total New Queries - Required Value has no Length - Sites: {cl_sites} - Queries: {queries} - Categories: {categories} - Data: {te}")
        return None
    logging.debug(
        f"Create Craigslist Queries - Started - Search ID: {dealify_search.search_id} - Total Queries: {total_new_queries}")
    new_queries = 0
    for site in cl_sites:
        for query in queries:
            for category in categories:
                try:
                    cl_query = CraigslistQueryIn(
                        search_id=dealify_search.search_id,
                        category=category,
                        query=query,
                        site_id=site.site_id,
                        **dealify_search.search_config.craigslist_config.dict()

                    )
                except ValidationError as ve:
                    logging.error(
                        f"Failed to Create Craigslist Query - Data: {ve.json()}")
                    continue
                logging.debug(
                    f"Create Craigslist Queries - Validation Successful - Query Data: {cl_query.json()}")
                await run_sproc(pool, create_craigslist_query_sproc, values_from_model(cl_query))
                new_queries += 1
                logging.debug(
                    f"Successfully Created Craigslist Query {new_queries} of {total_new_queries} for Search ID: {dealify_search.search_id}")
    await run_sproc(pool, update_dealify_search_status_sproc, [dealify_search.search_id, DealifySearchStatus.Dormant.value])
    logging.info(
        f"Create Craigslist Queries - Finished - Search ID: {dealify_search.search_id} - Queries Created: {new_queries}")


async def run_task_create_craigslist_queries_for_new_searches(pool):
    max_queries_key = await read_config_key(pool, ConfigKeys.CRAIGSLIST_MAX_QUERIES_PER_TASK)
    max_queries = max_queries_key.config_value
    new_searches = await read_models(pool, DealifySearch, read_dealify_searches_by_status_sproc, [
        DealifySearchStatus.New.value, max_queries])
    if not new_searches:
        logging.info(f"No New Searches Needing CraigslistQueries")
        return
    tasks = []
    for search in new_searches:
        tasks.append(create_craigslist_queries_for_dealify_search(
            pool=pool, dealify_search=search))
    await asyncio.gather(*tasks)
