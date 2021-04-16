from pydantic import ValidationError
import logging

from core.models.google_sheets.new_search_sheet_row import NewSearchSheetRow
from core.models.dealify.dealify_search import DealifySearchIn
from core.models.dealify.search_config import LocationRestrictionConfig, PriceRestrictionConfig, SearchConfigIn
from core.models.craigslist.craigslist_config import CraigslistConfig
from core.enums.sources import DealifySources


def dealify_search_from_sheet_row(nssr: NewSearchSheetRow):
    sci = SearchConfigIn()
    sources = []
    try:
        lrc = LocationRestrictionConfig(
            restriction_type=nssr.location_restriction_type, source_zip=nssr.source_zip)
        sci.location_restriction_config = lrc.json()
    except ValidationError as ve:
        logging.error(
            f"Failed to Validate LocationRestrictionConfig - Using Default")
        sci.location_restriction_config = LocationRestrictionConfig().json()
    try:
        prc = PriceRestrictionConfig(
            restriction_type=nssr.price_restriction_type, standard_price=nssr.standard_price)
        sci.price_restriction_config = prc.json()
    except ValidationError as ve:
        logging.error(
            f"Failed to Validate PriceRestrictionConfig - Using Default")
        sci.price_restriction_config = PriceRestrictionConfig().json()
    if nssr.search_craigslist:
        try:
            clc = CraigslistConfig(
                queries=nssr.craigslist_queries,
                categories=nssr.craigslist_categories,
                interval_mins=nssr.craigslist_search_interval_mins,
                search_titles=nssr.craigslist_search_titles,
                require_image=nssr.craigslist_require_image
            )
            sci.craigslist_config = clc.json()
            sources.append(DealifySources.Craigslist.value)
        except ValidationError as ve:
            logging.error(
                f"Failed to Validate Craigslist Config - Using None - Data: {ve.json()}")
    if not sources:
        logging.error(
            f"Failed to Create Deailfy Search from Sheets Row - No Sources!")
        return None
    try:
        dsi = DealifySearchIn(search_name=nssr.search_name,
                              sources=sources, search_config=sci)
        #print(f"SUCCESSFULLY CREATED DEALIFY SEARCH - VALUES: \n{dsi.json()}")
        return dsi
    except ValidationError as ve:
        print(f"Failed to Validate Dealify Search - Data: {ve.json()}")
        return None
