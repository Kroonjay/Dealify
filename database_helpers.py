import asyncio
import logging
import aiomysql
import os
import json

from pymysql.err import IntegrityError
from pydantic import ValidationError

from models import model_to_json_string, model_to_values, CraigslistQuery, DealifySearchTask, DealifySearchStatus
from config import DEALIFY_DB_CREDS
from sprocs import start_next_dealify_search_task_sproc, read_dealify_search_task_by_id_sproc, read_dealify_search_task_by_id_sproc, create_dealify_search_sproc, create_craigslist_query_sproc, create_craigslist_item_sproc, create_craigslist_site_sproc, read_craigslist_subdomain_by_site_id_sproc, read_dealify_search_by_id_sproc, read_craigslist_site_ids_by_country_sproc, start_next_overdue_craigslist_query_sproc, finish_craigslist_query_sproc, user_disable_dealify_search_sproc, read_craigslist_items_by_search_id_sproc, create_dealify_search_task_sproc
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
            f"Failed to Build Dealify Search From Row, Data: {ve.json}")
        return None


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
    logging.info("Retrieved All Site IDS")
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
def start_next_overdue_craigslist_query(conn):
    cur = yield from conn.cursor()
    yield from cur.callproc(start_next_overdue_craigslist_query_sproc)
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
def read_craigslist_items_by_search_id(search_id, conn):
    if not isinstance(search_id, int):
        logging.error(f"Search ID must be an Integer - Got: {type(search_id)}")
        return None
    cur = yield from conn.cursor()
    yield from cur.callproc(read_craigslist_items_by_search_id_sproc, [search_id])


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
