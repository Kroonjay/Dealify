from pydantic import BaseModel, validator
from datetime import datetime
from typing import List

from core.configs.sheets_configs import BOOLEAN_STRING_FALSE_VALUE, BOOLEAN_STRING_TRUE_VALUE, MULTIPLE_CELL_VALUE_SEPARATION_CHAR
from core.configs.craigslist_configs import CRAIGSLIST_SEARCH_INTERVAL_MIN_VALUE, CRAIGSLIST_SEARCH_INTERVAL_MAX_VALUE, CRAIGSLIST_SEARCH_INTERVAL_DEFAULT_VALUE
from core.utils.craigslist_utils import map_craigslist_category
from core.enums.restriction_types import LocationRestrictionTypes, PriceRestrictionTypes


class NewSearchSheetRow(BaseModel):
    timestamp: str = None
    search_name: str = None
    source_zip: int = None
    location_restriction_type: int = None
    standard_price: int = None
    price_restriction_type: int = None
    search_craigslist: bool = None
    craigslist_queries: List[str] = None
    craigslist_categories: List[str] = None
    craigslist_search_titles: bool = None
    craigslist_require_image: bool = None
    craigslist_search_interval_mins: int = None

    @validator('location_restriction_type', pre=True)
    def parse_location_restriction_type(cls, v):
        # Strip All Whitespace, including between words
        stripped = v.replace(" ", "")
        return LocationRestrictionTypes[stripped] if stripped in LocationRestrictionTypes.__members__ else LocationRestrictionTypes.HomeCity.value

    @validator('standard_price', pre=True)
    def parse_standard_price(cls, v):
        if not v:
            return
        try:
            return int(v) if int(v) > 0 else 1
        except TypeError:
            return 1

    @validator('price_restriction_type', pre=True)
    def parse_price_restriction_type(cls, v):
        if not v:
            return PriceRestrictionTypes.Unrestricted.value
        stripped = v.replace(" ", "")
        return PriceRestrictionTypes[stripped] if stripped in PriceRestrictionTypes.__members__ else PriceRestrictionTypes.Unrestricted.value

    # Pretty sure it's actually more code to re-use a validator than to duplicate the code: https://github.com/samuelcolvin/pydantic/issues/940

    @validator('search_craigslist', pre=True)
    def parse_search_craigslist(cls, v):
        return True if v == BOOLEAN_STRING_TRUE_VALUE else False

    @validator('craigslist_queries', pre=True)
    def queries_string_to_list(cls, v):
        if not v:
            return None
        else:
            return [(query.strip()) for query in v.split(MULTIPLE_CELL_VALUE_SEPARATION_CHAR)]

    @validator('craigslist_categories', pre=True)
    def craigslist_category_names_to_values(cls, v):
        if not v:
            return None
        else:
            category_names = [(c_name.strip()) for c_name in v.split(
                MULTIPLE_CELL_VALUE_SEPARATION_CHAR)]
            if not category_names:
                return None
            else:
                category_values = []
                for c_name in category_names:
                    c_val = map_craigslist_category(c_name)
                    if c_val:
                        category_values.append(c_val)
                return category_values

    @validator('craigslist_search_titles', pre=True)
    def parse_search_titles(cls, v):
        return True if v == BOOLEAN_STRING_TRUE_VALUE else False

    @validator('craigslist_require_image', pre=True)
    def parse_require_image(cls, v):
        return True if v == BOOLEAN_STRING_TRUE_VALUE else False

    @validator('craigslist_search_interval_mins', pre=True)
    def validate_cl_search_interval(cls, v):
        return v if int(v) > CRAIGSLIST_SEARCH_INTERVAL_MIN_VALUE and int(v) < CRAIGSLIST_SEARCH_INTERVAL_MAX_VALUE else CRAIGSLIST_SEARCH_INTERVAL_DEFAULT_VALUE
