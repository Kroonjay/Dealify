from pydantic import BaseModel, validator
from typing import List

from core.configs.craigslist_configs import CRAIGSLIST_SEARCH_INTERVAL_DEFAULT_VALUE, CRAIGSLIST_SEARCH_INTERVAL_MAX_VALUE, CRAIGSLIST_SEARCH_INTERVAL_MIN_VALUE


class CraigslistConfig(BaseModel):
    queries: List[str] = None  # List of queries to search on Craigslist
    categories: List[str] = None  # List of Craigslist Category Codes to Search
    interval_mins: int = None
    search_titles: bool = False
    require_image: bool = False

    @validator('interval_mins', pre=True)
    def validate_search_interval_mins(cls, v):
        if v:
            return v if int(v) > CRAIGSLIST_SEARCH_INTERVAL_MIN_VALUE and int(v) < CRAIGSLIST_SEARCH_INTERVAL_MAX_VALUE else CRAIGSLIST_SEARCH_INTERVAL_DEFAULT_VALUE
        else:
            return CRAIGSLIST_SEARCH_INTERVAL_DEFAULT_VALUE
