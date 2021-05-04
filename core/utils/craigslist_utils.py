import asyncio
import aiohttp
import logging
import re
import requests

from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError
from craigslist import CraigslistForSale


from core.database.db_helpers import run_sproc, read_model, values_from_model, read_models
from core.models.craigslist.craigslist_query import CraigslistQueryExecDetails
from core.models.craigslist.craigslist_site import CraigslistSite
from core.models.craigslist.craigslist_item import CraigslistItemIn
from core.models.craigslist.craigslist_site import CraigslistSite
from core.database.sprocs import read_craigslist_site_by_id_sproc, create_craigslist_item_sproc, read_craigslist_sites_by_city_sproc, read_craigslist_sites_by_country_sproc, read_craigslist_sites_by_state_sproc
from core.utils.location_utils import query_location
from core.enums.restriction_types import LocationRestrictionTypes

craigslist_category_map = {
    'Antiques': 'ata',
    'Appliances': 'ppa',
    'Arts & Crafts': 'ara',
    "ATV/UTV/Snomobile": 'sna',
    'Auto Parts': 'pta',
    'Aviation': 'ava',
    'Baby & Kid Stuff': 'baa',
    'Barter': 'bar',
    'Beauty & Health': 'haa',
    'Bike Parts': 'bip',
    'Bikes': 'bia',
    'Boat Parts': 'bpa',
    'Boats': 'boo',
    'Books': 'bka',
    'Business': 'bfa',
    'Cars & Trucks': 'cta',
    'CD/DVD/VHS': 'ema',
    'Cell Phones': 'moa',
    'Clothes & Accessories': 'cla',
    'Collectibles': 'cba',
    'Computer Parts': 'syp',
    'Computers': 'sya',
    'Electronics': 'ela',
    'Farm & Garden': 'gra',
    'Free Stuff': 'zip',
    'Furniture': 'fua',
    'Garage Sale': 'gms',
    'General': 'foa',
    'Heavy Equipment': 'hva',
    'Household Stuff': 'hsa',
    'Jewelery': 'jwa',
    'Materials': 'maa',
    'Motorcycle Parts': 'mpa',
    'Motorcycles': 'mca',
    'Musical Instruments': 'msa',
    'Photo & Video Stuff': 'pha',
    "RV's & Camping Gear": 'rva',
    'Sporting Goods': 'sga',
    'Tickets': 'tia',
    'Tools': 'tla',
    'Toys & Games': 'taa',
    'Trailers': 'tra',
    'Video Games': 'vga',
    'Wanted': 'waa',
    'Wheels & Tires': 'wta'
}


def map_craigslist_category(category_name: str):
    if not category_name in craigslist_category_map.keys():
        logging.error(
            f"Invalid Craigslist Category - No Value Found for Category Name: {category_name}")
        return None
    else:
        return craigslist_category_map[category_name]


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
                    logging.debug(
                        f"Received 404 Response - Craigslist Item is Definitely Deleted")
                    return True
                else:
                    logging.error(
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

    logging.debug(
        f"Finished Query Craigslist Items - Found {cl_items} Items for Query {cl_query.query_id}")
    return cl_items


async def query_unrestricted_sites(pool, location_restriction_config):
    cl_sites = None
    if not location_restriction_config:
        logging.error(
            f"Failed to Query Craigslist Sites - LocationRestrictionConfig Not Provided")
        return None
    source_loc = query_location(
        location_restriction_config.source_zip)
    if location_restriction_config.restriction_type == LocationRestrictionTypes.UnitedStates.value:
        logging.debug("Location Restricted to US Only")
        cl_sites = await read_models(pool, CraigslistSite, read_craigslist_sites_by_country_sproc, ['United States'])
    elif location_restriction_config.restriction_type == LocationRestrictionTypes.HomeState.value:
        if not source_loc:
            logging.error(
                f"Unable to Query Unrestricted Sites - Location Not Found or Invalid - Source ZIP Code: {location_restriction_config.source_zip}")

        else:
            cl_sites = await read_models(pool, CraigslistSite, read_craigslist_sites_by_state_sproc, [source_loc.state])
            logging.debug(
                f"Query Unrestricted Sites - Successfully Retrieved Sites for HomeState Search - Sites: {cl_sites}")

    elif location_restriction_config.restriction_type == LocationRestrictionTypes.HomeCity.value:
        logging.debug(
            f"Query Unrestricted Sites - Location Restricted to HomeCity Only - LRC Data: {location_restriction_config.json()}")
        if not source_loc:
            logging.error(
                f"Unable to Query Unrestricted Sites - Location Not Found or Invalid - Source ZIP Code: {location_restriction_config.source_zip}")
        else:
            cl_sites = await read_models(pool, CraigslistSite, read_craigslist_sites_by_city_sproc, [source_loc.city])
    else:
        logging.error(
            f"Location Restriction Unsupported! - Option: {location_restriction_config.restriction_type}")
    return cl_sites
