from pydantic import BaseModel, validator, parse_raw_as
from datetime import datetime
from typing import List


class CraigslistSiteIn(BaseModel):
    subdomain: str
    # Friendly Name, pulled from Craigslist sites page Usually a city but can be county, country
    site_name: str
    site_url: str
    city: str = None
    state_code: str = None
    country: str = None
    latitude: float = None
    longitude: float = None
    areas: str = None  # JSON Stringify'd list of areas, if applicable


class CraigslistSite(BaseModel):
    site_id: int = None
    subdomain: str = None
    # Friendly Name, pulled from Craigslist sites page Usually a city but can be county, country
    site_name: str = None
    site_url: str = None
    city: str = None
    state_code: str = None
    country: str = None
    latitude: float = None
    longitude: float = None
    created_at: datetime = None
    last_searched_at: datetime = None
    last_updated_at: datetime = None
    areas: List[str] = None

    @validator('areas', pre=True)
    def build_sources_list(cls, v):
        if not v:
            return None
        else:
            return parse_raw_as(List[str], v)
