import asyncio
import logging
import aiomysql
import os
import json

from pymysql.err import IntegrityError
from pydantic import ValidationError

from models import CraigslistItem, DealifyWorkerTaskConfig, DealifyWorker, model_to_json_string, model_to_values, CraigslistQuery, DealifySearchTask, DealifySearchStatus, LocationRestrictionConfig, PriceRestrictionConfig, PriceRestrictionTypes, CraigslistConfig, DealifySearch, SearchConfig
from config import DEALIFY_DB_CREDS, SEARCH_CONFIG_CL_CONFIG_KEY_NAME, SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME, SEARCH_CONFIG_LOCATION_UNRESTRICTED_SEARCH_KEY, SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME
from sprocs import *
from prep_stmts import read_all_craigslist_site_ids_stmt


def row_to_dealify_search(row):
    if not isinstance(row, tuple):
        logging.error("Row to Dealify Search - Row Must be a Tuple")
        return None
    if not len(row) == 6:
        logging.error(
            f"Row to Dealify Search - Invalid Number of Values - Expected 7 - Got {len(row)} - Values: \n {row}")
        return
    sc_data = json.loads(row[4])
    logging.debug(sc_data)
    if sc_data[SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME]:
        sc_data[SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME] = LocationRestrictionConfig.parse_raw(
            sc_data[SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME])
        logging.debug(
            f"Successfully Loaded Restriction Config from Dealify Search - Data: {sc_data[SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME]}")
    if sc_data[SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME]:
        sc_data[SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME] = PriceRestrictionConfig.parse_raw(
            sc_data[SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME])
        logging.debug(
            f"Successfully Loaded Restriction Config from Dealify Search - Data: {sc_data[SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME]}")
    # Need to convert nested Config Objects from JSON strings before creating main SearchConfig object
    if sc_data[SEARCH_CONFIG_CL_CONFIG_KEY_NAME]:
        logging.debug(
            f"Successfully Loaded Craigslist Config from Dealify Search - Data: {sc_data[SEARCH_CONFIG_CL_CONFIG_KEY_NAME]}")
        sc_data[SEARCH_CONFIG_CL_CONFIG_KEY_NAME] = CraigslistConfig.parse_raw(
            sc_data[SEARCH_CONFIG_CL_CONFIG_KEY_NAME])
    try:
        ds = DealifySearch(
            search_id=row[0],
            search_status=row[1],
            search_name=row[2],
            sources=json.loads(row[3]),
            search_config=SearchConfig(**sc_data),
            created_at=row[5]
        )
        return ds
    except ValidationError as ve:
        logging.error(
            f"Failed to Build Dealify Search From Row - Validation Error -  Data: {ve.json()}")
        return None


def row_to_craigslist_item(row):
    vals_per_row = 15
    if len(row) < vals_per_row:
        logging.error(
            f"Row to Craigslist Item - Received Row with Invalid Number of Values - Expected {vals_per_row}, Got {len(row)} - Data: {row}")
        return None
    try:
        cl_item = CraigslistItem(
            item_id=row[0],
            item_name=row[1],
            price=row[2],
            search_id=row[3],
            source_url=row[4],
            tags=row[5],
            created_at=row[6],
            last_seen_at=row[7],
            source_id=row[8],
            posted_at=row[9],
            is_deleted=row[10],
            has_image=row[11],
            last_updated=row[12],
            repost_of=row[13],
            item_location=row[14]
        )
        return cl_item
    except ValidationError as ve:
        logging.error(
            f"Failed to Build Craigslist Item from Row - Validation Error - Data: {ve.json()}")
        return None
    logging.info(
        f"Row to Craigslist Item - Conversion Successful - Item ID: {item.item_id}")
    return cl_item


@asyncio.coroutine
def start_pool(dealify_db_creds: dict):
    if not dealify_db_creds["password"]:
        logging.critical("ERROR - Dealify Database Password is Unset!")
        return None
    pool = yield from aiomysql.create_pool(**dealify_db_creds)
    logging.info("Successfully Started Connection Pool!")
    return pool


@asyncio.coroutine
def run_sproc(pool, sproc: str, params: list = None):
    if not pool:
        logging.error(
            f'Failed to Run Stored Procedure - Connection Pool is None')
        return None
    rows = None
    with (yield from pool) as conn:
        cur = yield from conn.cursor()
        if params:
            yield from cur.callproc(sproc, params)
        else:
            yield from cur.callproc(sproc)
        try:
            rows = yield from cur.fetchall()

        except ValueError as vale:
            logging.error(
                f"Run Stored Procedure - Value Error - No Response Rows - Sproc: {sproc} - Params: {params}")
    logging.info(
        f"Run Stored Procedure - Finished - Sproc: {sproc} - Response Rows: {0 if rows is None else len(rows)}")
    return rows


async def connect_dealify_db(dealify_db_creds):
    if not dealify_db_creds["password"]:
        logging.critical("ERROR - Dealify Database Password is Unset!")
        return None
    connection = await aiomysql.connect(**dealify_db_creds, autocommit=True)
    logging.info("Successfully Connected to Database!")
    return connection


def disconnect_dealify_db(conn):
    conn.close()
    logging.info("Successfully Closed Connection!")


async def create_dealify_search(dealify_search, conn):
    if dealify_search.search_config:
        logging.debug(dealify_search.search_config)
    else:
        logging.error("ERROR - Required SearchConfig not Found!")
        return None
    values = model_to_values(dealify_search)
    logging.debug(values)
    async with conn.cursor() as cur:
        await cur.callproc(create_dealify_search_sproc, values)
        # await conn.commit()
        logging.info("New Dealify Search Created!")


async def create_craigslist_query(cl_query, conn):

    values = model_to_values(cl_query)
    logging.debug(values)
    async with conn.cursor() as cur:
        await cur.callproc(create_craigslist_query_sproc, values)
        # await conn.commit()
        logging.info("New Dealify Search Created!")


async def create_craigslist_item(cl_item, conn):
    values = model_to_values(cl_item)
    logging.debug(values)
    async with conn.cursor() as cur:
        await cur.callproc(create_craigslist_item_sproc, values)
        # await conn.commit()
        logging.info("New Craigslist Item Created!")


async def create_craigslist_site(cl_site, conn):

    values = model_to_values(cl_site)
    logging.debug(values)
    async with conn.cursor() as cur:
        try:
            await cur.callproc(create_craigslist_site_sproc, values)
            # await conn.commit()
            logging.info("New Craigslist Site Created!")
        except IntegrityError as ie:
            logging.error(
                f"Duplicate Key for Craigslist Site - Skipping - Data: {ie}")


@asyncio.coroutine
def read_craigslist_subdomain_by_site_id(site_id, conn):
    if not isinstance(site_id, int):
        logging.error("Site ID Must be an Integer")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_craigslist_subdomain_by_site_id_sproc, [site_id])
    (subdomain, ) = yield from cur.fetchone()
    if not subdomain:
        logging.error("No Subdomain Found!")
        return None
    logging.debug(subdomain)
    return subdomain


@asyncio.coroutine
# Returns a Generator of Tuples where SiteID is first val - Correct Usage: for site_id, in await read_all_craigslist_site_ids(conn):
def read_all_craigslist_site_ids(conn):
    site_ids = None
    cur = yield from conn.cursor()
    yield from cur.execute(read_all_craigslist_site_ids_stmt)
    site_ids = yield from cur.fetchall()
    logging.info("Retrieved All Site IDS")
    return site_ids


@asyncio.coroutine
# Returns a Generator of Tuples where SiteID is first val - Correct Usage: for site_id, in await read_all_craigslist_site_ids(conn):
def read_craigslist_site_ids_by_country(country, conn):
    site_ids = None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_craigslist_site_ids_by_country_sproc, [country])
    site_ids = yield from cur.fetchall()
    logging.info(f"Retrieved All Site IDS for Country: {country}")
    return site_ids


@asyncio.coroutine
# Returns a Generator of Tuples where SiteID is first val - Correct Usage: for site_id, in await read_all_craigslist_site_ids(conn):
def read_craigslist_site_ids_by_state(state, conn):
    site_ids = None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_craigslist_site_ids_by_state_sproc, [state])
    site_ids = yield from cur.fetchall()
    logging.error(
        f"Retrieved All Site IDS for State: {state} - Site IDS: {site_ids}")
    return site_ids


@asyncio.coroutine
# Returns a Generator of Tuples where SiteID is first val - Correct Usage: for site_id, in await read_all_craigslist_site_ids(conn):
def read_craigslist_site_ids_by_city(city, conn):
    site_ids = None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_craigslist_site_ids_by_state_sproc, [city])
    site_ids = yield from cur.fetchall()
    logging.error(
        f"Retrieved All Site IDS for State: {state} - Site IDS: {site_ids}")
    return site_ids


@asyncio.coroutine
def read_dealify_search_by_search_id(search_id, conn):
    if not isinstance(search_id, int):
        logging.error("Search ID must be an Integer")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_dealify_search_by_id_sproc, [search_id])
    (row, ) = yield from cur.fetchall()
    if not row:
        logging.error(f"No Dealify Search Found for Search ID: {search_id}")
        return None
    return row_to_dealify_search(row)


@asyncio.coroutine
def read_next_overdue_craigslist_query_id(conn):
    cur = yield from conn.cursor()
    yield from cur.callproc(read_next_overdue_craigslist_query_id_sproc)
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.info(
            "Read Next Overdue Craigslist Query ID - Value Error - No Overdue Queries")
        return None
    query_id = row[0]
    return query_id


@asyncio.coroutine
def set_deleted_craigslist_item(conn, item_id: int, is_deleted: bool):
    cur = yield from conn.cursor()
    yield from cur.callproc(set_deleted_craigslist_item_sproc, [item_id, is_deleted])

    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.info(
            f"Set Deleted Craigslist Item - Value Error - No Item Found for ID: {item_id}")
        return None
    item = None
    if row:
        item = row_to_craigslist_item(row)
    if not item:
        logging.error(
            f"Set Deleted Craigslist Item - Failed to Convert Row to Object - Item ID: {item_id}")
        return None
    if item.is_deleted == is_deleted:
        logging.info(
            f"Set Deleted Craigslist Item - Updated Successfully - Item ID: {item_id}")
        return True
    else:
        logging.error(
            f"Set Deleted Craigslist Item - Update Not Successful, is_deleted is False - Item ID: {item_id}")
        return None


@asyncio.coroutine
def start_overdue_craigslist_query(query_id, conn):
    if not isinstance(query_id, int):
        logging.error("Search ID must be an Integer")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(start_overdue_craigslist_query_sproc, [query_id])
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.info(
            "Start Next Overdue Query - Value Error - No Overdue Queries")
        return None
    try:
        cq = CraigslistQuery(
            query_id=row[0],
            search_id=row[1],
            query=row[2],
            site_id=row[3],
            area=row[4],
            category=row[5],
            search_titles=row[6],
            require_image=row[7],
            posted_today=row[8]
        )
    except ValidationError as ve:
        logging.error(
            f"Failed to Convert Row to CraigslistQuery - Data: {ve.json()}")
        return None
    yield from cur.close()
    return cq


@asyncio.coroutine
def finish_craigslist_query(query_id, conn):
    if not isinstance(query_id, int):
        logging.error(f"Query ID must be an Integer - Got: {type(search_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(finish_craigslist_query_sproc, [query_id])
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.error(
            "Finish Craigslist Query - Value Error - No Query ID or Status")
        return None
    try:
        query = CraigslistQuery(
            query_id=row[0],
            query_status=row[1]
        )
    except ValidationError as ve:
        logging.error(
            f"Failed to Retrieve Dealify Search Task - Data: {ve.json()}")
        return None

    if query.query_status == DealifySearchStatus.Dormant.value:
        return True
    yield from cur.close()
    return None


@asyncio.coroutine
def user_disable_dealify_search(search_id, conn):
    if not isinstance(search_id, int):
        logging.error(f"Search ID must be an Integer - Got: {type(search_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(user_disable_dealify_search_sproc, [search_id])


@asyncio.coroutine
def read_craigslist_items_by_search_id(search_id, conn, limit=10):
    items = []

    if not isinstance(search_id, int):
        logging.error(f"Search ID must be an Integer - Got: {type(search_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_craigslist_items_by_search_id_sproc, [search_id, limit])
    try:
        rows = yield from cur.fetchall()
    except ValueError as vale:
        logging.error(
            "Read Craigslist Items By Search ID - Value Error - No Items")
        return None

    for row in rows:
        try:
            item = CraigslistItem(
                item_id=row[0],
                item_name=row[1],
                price=row[2],
                search_id=row[3],
                source_url=row[4],
                tags=row[5],
                created_at=row[6],
                last_seen_at=row[7],
                source_id=row[8],
                posted_at=row[9],
                is_deleted=row[10],
                has_image=row[11],
                last_updated=row[12],
                repost_of=row[13],
                item_location=row[14]
            )
            items.append(item)
        except ValidationError as ve:
            logging.error(
                f"Failed to Retrieve Craigslist Item - Data: {ve.json()}")
            continue
    logging.info(
        f"Read Craigslist Items By Search ID - Found {len(items) if items else 0} for Search ID {search_id}")
    return items


@asyncio.coroutine
def create_dealify_search_task(task_in, conn):
    values = model_to_values(task_in)
    logging.debug(values)
    cur = yield from conn.cursor()
    yield from cur.callproc(create_dealify_search_task_sproc, values)


@asyncio.coroutine
def read_dealify_search_task_by_id(task_id, conn):
    if not isinstance(task_id, int):
        logging.error(f"Task ID must be an Integer - Got: {type(task_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_dealify_search_task_by_id_sproc, [task_id])
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.error("Read Search Task By ID - Value Error - No Tasks")
        return None
    try:
        task = DealifySearchTask(
            task_id=row[0],
            task_name=row[1],
            task_type=row[2],
            task_status=row[3],
            task_config=row[4],
            created_at=row[5],
            last_execution_at=row[6]
        )
        return task
    except ValidationError as ve:
        logging.error(
            f"Failed to Retrieve Dealify Search Task - Data: {ve.json()}")
        return None


@asyncio.coroutine
def start_next_dealify_search_task(conn):
    cur = yield from conn.cursor()
    yield from cur.callproc(start_next_dealify_search_task_sproc)
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.error("Read Next Search Task - Value Error - No Tasks")
        return None
    try:
        task = DealifySearchTask(
            task_id=row[0],
            task_name=row[1],
            task_type=row[2],
            task_config=row[3]
        )
        return task
    except ValidationError as ve:
        logging.error(
            f"Failed to Retrieve Dealify Search Task - Data: {ve.json()}")
        return None


@asyncio.coroutine
def set_overdue_craigslist_queries(conn):
    cur = yield from conn.cursor()
    yield from cur.callproc(set_overdue_craigslist_queries_sproc)
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.error(
            "Set Overdue Craigslist Queries - Value Error - Expected Overdue Query Count")
        return None
    overdue_query_count = row[0]
    logging.info(
        f"Set Overdue Craigslsit Queries Completed - {overdue_query_count} Total Overdue Queries")
    return overdue_query_count


@asyncio.coroutine
def read_new_dealify_search_ids(conn):
    cur = yield from conn.cursor()
    yield from cur.callproc(read_new_dealify_search_ids_sproc)
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.error(
            "Read New Dealify Search ID's - Value Error - No New Search ID's"
        )
        return None
    new_search_ids = [(item) for item in row]
    logging.info(f"{new_search_ids}")
    return new_search_ids


@asyncio.coroutine
def set_dormant_dealify_search(search_id, conn):
    if not isinstance(search_id, int):
        logging.error(f"Search ID must be an Integer - Got: {type(search_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(set_dormant_dealify_search_sproc, [search_id])
    logging.info(
        f"Set Dormant Dealify Search Finished - Search ID: {search_id}")
    return


@asyncio.coroutine
def create_dealify_worker(worker_in, conn):
    values = model_to_values(worker_in)
    logging.debug(values)
    cur = yield from conn.cursor()
    yield from cur.callproc(create_dealify_worker_sproc, values)


@asyncio.coroutine
def update_dealify_worker_status(worker_id, new_status, conn):
    if not isinstance(worker_id, int):
        logging.error(f"Worker ID must be an Integer - Got: {type(search_id)}")
        return None
    if not isinstance(new_status, int):
        logging.error(
            f"Worker Status must be an Integer - Got: {type(search_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(update_dealify_worker_status_sproc, [worker_id, new_status])


@asyncio.coroutine
def read_dealify_worker_by_id(worker_id, conn):
    if not isinstance(worker_id, int):
        logging.error(f"Worker ID must be an Integer - Got: {type(worker_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_dealify_worker_by_id_sproc, [worker_id])
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.error(
            f"Read Dealify Worker By ID - Value Error - No Worker Found for ID:{worker_id}"
        )
        return None

    try:
        worker = DealifyWorker(
            worker_id=row[0],
            worker_name=row[1],
            worker_status=row[2],
            current_task=row[3],
            task_config=DealifyWorkerTaskConfig(**json.loads(row[4])),
            created_at=row[5],
            started_at=row[6]
        )
        logging.debug(
            f"Read Dealify Worker By ID Successful - Values: {worker.json()}")
        return worker
    except ValidationError as ve:
        logging.error(
            f"Read Dealify Worker By ID Failed - Validation Error - Data: \n{ve.json()} \n Values: \n{row}"
        )
        return None
    except IndexError as ie:
        logging.error(
            f"Read Dealify Worker By ID Failed - Index Error - Data: \n{ie} \n Values: \n {row}"
        )
        return None


@asyncio.coroutine
def read_dealify_task_ids_by_type(task_type, conn):
    if not isinstance(task_type, int):
        logging.error(f"Task Type must be an Integer - Got: {type(search_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_dealify_task_ids_by_type_sproc, [task_type])
    try:
        (row, ) = yield from cur.fetchall()
    except ValueError as vale:
        logging.error(
            f"Read Dealify Task ID's By Type - Value Error - No Task ID's for Task Type: {task_type}"
        )
        return None
    task_ids = [(item) for item in row]
    logging.info(f"{task_ids}")
    return task_ids


@asyncio.coroutine
def read_old_craigslist_items(interval_days, conn, limit=250):

    cur = yield from conn.cursor()
    yield from cur.callproc(read_old_craigslist_item_ids_sproc, [interval_days, limit])
    try:
        rows = yield from cur.fetchall()
    except ValueError as vale:
        logging.error(
            f"Read Old Craigslist Item ID's - Value Error - No Items Older than {interval_days} Days to Retrieve"
        )
        return None
    old_items = []
    for row in rows:
        item = row_to_craigslist_item(row)
        if item:
            old_items.append(item)
        else:
            logging.error(
                f"Read Old Craigslist Items - Failed to Build Item from Row - Data: {row}")
            continue

    logging.info(
        f"Read Old Craigslist Item ID's - Successfully Retrieved {len(old_items)} Items Older than {interval_days} Days")
    return old_items


@asyncio.coroutine
def update_dealify_worker_current_task(worker_id, task_id, conn):
    if not isinstance(worker_id, int):
        logging.error(f"Worker ID must be an Integer - Got: {type(worker_id)}")
        return None
    if not isinstance(task_id, int):
        logging.error(f"Task ID must be an Integer - Got: {type(task_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(update_dealify_current_task_by_id_sproc, [worker_id, task_id])
