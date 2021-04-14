import asyncio
import aiohttp
import logging
import re

from bs4 import BeautifulSoup
from craigslist import CraigslistForSale
import requests

from core.database.db_helpers import run_sproc, read_model, values_from_model
from core.models.craigslist.craigslist_query import CraigslistQueryExecDetails
from core.models.craigslist.craigslist_site import CraigslistSite
from core.models.craigslist.craigslist_item import CraigslistItemIn
from core.database.sprocs import read_craigslist_site_by_id_sproc, create_craigslist_item_sproc


def parse_price(source_price):
    if not source_price:
        return None
    out_price = ''.join(i for i in source_price if i.isalnum())
    return int(out_price)


def parse_special(source_text):
    if not source_text:
        return None
    # Simple regex to strip all special chars https://stackoverflow.com/questions/43358857/how-to-remove-special-characters-except-space-from-a-file-in-python/43358965
    out_text = re.sub(r"\W+|_", " ", source_text)
    return out_text


def cl_query_exec_details(cl_query, site: str):
    if not site:
        logging.error("Can't Query Craigslist FS, No Site!")
        return None
    logging.debug(f"SITE: {site}")
    filters = None
    if not cl_query.query:
        logging.error("Query is Required!")
        return None
    filters = {"query": cl_query.query}
    if cl_query.search_titles:
        filters['search_titles'] = True
    if cl_query.require_image:
        filters['has_image'] = True
    if cl_query.posted_today:
        filters['posted_today'] = True
    if not filters:
        return CraigslistQueryExecDetails(site=site, **cl_query.dict(exclude_unset=True))
    else:
        return CraigslistQueryExecDetails(site=site, filters=filters, **cl_query.dict(exclude_unset=True))


async def craigslist_item_is_deleted(cl_item):
    if cl_item.is_deleted:
        return True
    async with aiohttp.ClientSession() as session:
        async with session.get(cl_item.source_url) as response:
            if not response.status == 200:
                if response.status == 404:
                    print(
                        f"Received 404 Response - Craigslist Item is Definitely Deleted")
                    return True
                else:
                    print(
                        f"Received Unknown Response Code - Unsure if Item is Deleted or Error - Status: {response.status}")
                    return False
            else:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                deleted_headers = soup.find_all('h2')
                if deleted_headers:
                    logging.debug(
                        f"Found H2 Header for Listing - Item was Probably Deleted - Item ID: {cl_item.item_id}")
                    return True
                return False


def parse_craigslist_item(cl_result, search_id):
    if not cl_result['name']:
        logging.error(f"Name is Required! - Data: {cl_result}")
        return None
    if not cl_result['price']:
        logging.error(f"Price is Required! - Data: {cl_result}")
        return None
    if not cl_result['url']:
        logging.error(f"Source URL is Required! - Data: {cl_result}")
        return None
    cl_item = CraigslistItemIn(
        item_name=parse_special(cl_result['name']),
        price=parse_price(cl_result['price']),
        search_id=search_id,
        source_url=cl_result['url'],
        source_id=cl_result['id'],
        posted_at=cl_result['datetime'],
        is_deleted=cl_result['deleted'],
        has_image=cl_result['has_image'],
        last_updated=cl_result['last_updated'],
        repost_of=cl_result['repost_of'],
        item_location=parse_special(cl_result['where']))

    return cl_item


@asyncio.coroutine
async def query_craigslist_items(cl_query, pool):
    cl_site = await read_model(pool, CraigslistSite, read_craigslist_site_by_id_sproc, [cl_query.site_id])
    cl_items = 0
    if not cl_site:
        logging.error(
            f"Unable to Query Craigslist Items - Site is None - Craigslist Query: {cl_query}")
        return cl_items
    exec_details = cl_query_exec_details(cl_query, cl_site.subdomain)
    if not exec_details:
        logging.error("NO EXECUTION DETAILS!!!")
        return cl_items

    logging.debug(exec_details.json())

    try:
        cl_fs = CraigslistForSale(**exec_details.dict(exclude_unset=True))
        for cl_result in cl_fs.get_results():
            cl_item = parse_craigslist_item(
                cl_result, search_id=cl_query.search_id)
            if cl_item:
                logging.debug(cl_item.json())
                values = values_from_model(cl_item)
                created = await run_sproc(pool, create_craigslist_item_sproc, values)
                cl_items += 1
    except requests.exceptions.ConnectionError as ce:
        logging.error(
            f"ConnectionError While Querying Craigslist Items - We're Probably Being Rate-Limited - Data: {ce}")
        return cl_items

    logging.info(
        f"Finished Query Craigslist Items - Found {cl_items} Items for Query {cl_query.query_id}")
    return cl_items
