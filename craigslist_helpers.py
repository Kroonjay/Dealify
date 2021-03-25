import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from pydantic import ValidationError
from craigslist import CraigslistForSale
from craigslist_config import CL_SITES_URL, CL_SITE_IGNORED_SUBDOMAINS, CL_NOMINATIM_AGENT, CL_QUERY_SLEEP_INTERVAL_SECONDS_MIN, CL_QUERY_SLEEP_INTERVAL_SECONDS_MAX, CL_QUERY_MAX_RETRIES, CL_QUERY_MAX_QUERIES, CL_QUERY_RATE_LIMIT_SLEEP_INTERVAL_SECONDS
from parsers import parse_price, parse_special
from models import CraigslistItemIn, CraigslistQueryIn, CraigslistQuery, CraigslistQueryExecDetails, CraigslistSiteIn, LocationRestrictionTypes, RestrictionTypes
from database_helpers import create_craigslist_query, create_craigslist_site, create_craigslist_item, read_craigslist_subdomain_by_site_id, read_all_craigslist_site_ids, read_craigslist_site_ids_by_country, start_next_overdue_craigslist_query, finish_craigslist_query
import json
from geopy.geocoders import Nominatim
import asyncio
from random import randint
from requests.exceptions import ConnectionError


def query_site_location(cl_site):
    geolocator = Nominatim(user_agent=CL_NOMINATIM_AGENT)
    location = geolocator.geocode(cl_site.site_name)
    if not location:
        logging.info("Location is None!!")
        return cl_site
    if location.latitude and location.longitude:
        cl_site.latitude = location.latitude
        cl_site.longitude = location.longitude
    if location.address:
        parsed_address = location.address.split(", ")
        if len(parsed_address) == 1:
            # Country Only
            cl_site.country = parse_special(parsed_address[0])
            return cl_site
        cl_site.city = parse_special(parsed_address[0])
        # Country will always be last item in list
        cl_site.country = parse_special(parsed_address[-1])
        # State always before Zip, always present if Zip is present
        try:
            if parsed_address[-2].isdecimal():
                cl_site.state_code = parse_special(parsed_address[-3])
            else:
                cl_site.state_code = parse_special(parsed_address[-2])
        except IndexError as ie:
            logging.info(
                f"No County - {cl_site.site_url} - Address: {parse_special(location.address)}")

    return cl_site


def query_site_areas(cl_site):
    response = requests.get(cl_site.site_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    site_areas = []
    for link in soup.find_all('a'):
        if len(link.get('href').strip('/')) == 3:
            site_area = link.get('href')
            # logging.info(f"SITE AREA URL: {site_area}")
            site_areas.append(site_area)
    return site_areas


def check_if_site_url(link):
    url = link.get('href')
    text = link.text
    if not url:
        logging.info(f"Not a Site URL - No href Attribute - Link: {link}")
        return None

    if not text:
        logging.info(f"Not a Site URL - No Link Text - Link: {link}")
        return None
    parsed = urlparse(url)
    if not parsed.path == "/":
        logging.info(
            f"Not a Site URL - Has a Path - URL: {parsed.geturl()} - Path: {parsed.path}")
        return None
    parsed_netloc = str(parsed.netloc).split(".")
    if len(parsed_netloc) < 3:
        logging.info("Not a Site URL - Only 2 Netloc Sections")
        return None
    if parsed_netloc[0] not in CL_SITE_IGNORED_SUBDOMAINS:
        logging.info(
            f"Found a Site URL - Site: {parsed_netloc[0]} - URL: {parsed.geturl()}")
        try:
            new_site = CraigslistSiteIn(
                subdomain=parsed_netloc[0], site_name=text, site_url=parsed.geturl())
            return new_site
        except ValidationError as ve:
            logging.info(
                f"Couldn't Create Site from URL - ValidationError - Data: {ve.json}")
    # else:
    #     logging.info(
    #         f"Not a Site URL - In Restricted Subdomains - URL: {parsed.geturl()}")
    return None


async def query_craigslist_sites(conn):
    response = requests.get(CL_SITES_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    cl_sites = []
    for link in soup.find_all('a', href=True):
        cl_site = check_if_site_url(link)
        if cl_site:
            site_areas = query_site_areas(cl_site)
            if site_areas:
                cl_site.areas = json.dumps(site_areas)
            cl_site = query_site_location(cl_site)
            created = await create_craigslist_site(cl_site, conn)
    return cl_sites


def parse_craigslist_item(cl_result, search_id):
    if not cl_result['name']:
        logging.error("Name is Required!")
        return None
    if not cl_result['price']:
        logging.error("Price is Required!")
        return None
    if not cl_result['url']:
        logging.error("Source URL is Required!")
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


async def cl_query_exec_details(cl_query, conn):
    site = await read_craigslist_subdomain_by_site_id(cl_query.site_id, conn)
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


@asyncio.coroutine
async def query_craigslist_items(cl_query, conn):
    exec_details = await cl_query_exec_details(cl_query, conn)
    if not exec_details:
        logging.error("NO EXECUTION DETAILS!!!")
        return None

    cl_fs = CraigslistForSale(**exec_details.dict(exclude_unset=True))

    logging.debug(exec_details.json())
    cl_items = 0
    for cl_result in cl_fs.get_results():
        cl_item = parse_craigslist_item(
            cl_result, search_id=cl_query.search_id)
        logging.debug(cl_item.json())
        created = await create_craigslist_item(cl_item, conn)
    logging.info(
        f"Finished Query Craigslist Items - Found {cl_items} Items for Query {cl_query.query_id}")
    return


async def query_unrestricted_sites(dealify_search, conn):
    cl_sites = None
    if dealify_search.search_config.location_restriction_config:
        if dealify_search.search_config.location_restriction_config.restriction_type == LocationRestrictionTypes.UnitedStatesOnly.value:
            logging.debug("Location Restricted to US Only")
            cl_sites = await read_craigslist_site_ids_by_country(
                'United States', conn)
            return cl_sites
        else:
            logging.error(
                f"Location Restriction Unsupported! - Option: {dealify_search.search_config.location_restriction_config.restriction_type}")
    else:
        logging.critical("Unrestricted Search Requested - Watch Out!")
        return cl_sites


async def create_craigslist_queries(dealify_search, conn):
    cl_sites = await query_unrestricted_sites(dealify_search, conn)
    if not cl_sites:
        logging.error("No Sites!!!!")
        return None
    for site_id, in cl_sites:
        for query in dealify_search.search_config.craigslist_config.queries:
            try:
                cl_query = CraigslistQueryIn(
                    search_id=dealify_search.search_id,
                    query=query,
                    site_id=site_id,
                    **dealify_search.search_config.craigslist_config.dict()

                )
            except ValidationError as ve:
                logging.error(
                    f"Failed to Create Craigslist Query - Data: {ve.json()}")
                continue
            await create_craigslist_query(cl_query, conn)
            logging.info("Created Craigslist Query")


@asyncio.coroutine
async def work_overdue_craigslist_queries(conn, query_sleep_seconds_min=CL_QUERY_SLEEP_INTERVAL_SECONDS_MIN, query_sleep_seconds_max=CL_QUERY_SLEEP_INTERVAL_SECONDS_MAX, rate_limit_sleep_interval=CL_QUERY_RATE_LIMIT_SLEEP_INTERVAL_SECONDS, query_max_retries=CL_QUERY_MAX_RETRIES, max_queries=CL_QUERY_MAX_QUERIES):
    retries = 0
    queries = 0
    while retries < query_max_retries and queries < max_queries:
        cl_query = None
        cl_query = await start_next_overdue_craigslist_query(conn)
        if not cl_query:
            logging.info("Work Overdue Craigslist Queries - No Queries")
            break
        logging.info(f"Started Craigslit Query with ID: {cl_query.query_id}")
        logging.debug(cl_query.json())
        try:
            await query_craigslist_items(cl_query, conn)
        except ConnectionError as ce:
            retries += 1
            sleep_for = rate_limit_sleep_interval
            logging.error(
                f"Encountered RequestExecption While initialising CraigslistForSale object - Sleeping for {sleep_for}s before Retrying")
            await asyncio.sleep(sleep_for)
            continue

        finished = await finish_craigslist_query(cl_query.query_id, conn)
        if not finished:
            logging.error("Failed to Finish Craigslist Query!!!!")
        sleep_for = randint(query_sleep_seconds_min, query_sleep_seconds_max)
        logging.info(
            f"Finished Craigslist Query with ID: {cl_query.query_id} - Sleeping for {sleep_for}s befor next Query")
        await asyncio.sleep(sleep_for)
        queries += 1
    logging.info("Finished All Overdue Craigslist Queries!")
