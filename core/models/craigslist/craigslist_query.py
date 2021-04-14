from pydantic import BaseModel
from datetime import datetime
from typing import Dict
from core.enums.statuses import DealifySearchStatus


class CraigslistQueryExecDetails(BaseModel):
    site: str
    area: str = None
    category: str = None
    filters: Dict = None


class CraigslistQueryIn(BaseModel):
    search_id: int = 1  # DealifySearch ID
    query: str = None  # String to search for
    interval_mins: int = 1440  # Time between searches
    # ID of CraigslistSite to Search (ex. portland.craigslist.org)
    site_id: int = 1
    # More specific locations within a site.  Format is <site>.craigslist.org/<area>
    area: str = None
    category: str = None  # Craigslist category code.  Format is /search/<category>
    search_titles: bool = False  # Find only results with query string in title
    require_image: bool = False  # Find only results with images
    posted_today: bool = False  # Find only results posted within past 24hrs


class CraigslistQuery(BaseModel):
    query_id: int = None  # Database ID
    # Used to Monitor status of Task Execution
    query_status: int = DealifySearchStatus.Dormant.value
    search_id: int = 1  # DealifySearch ID
    query: str = None  # String to search for
    interval_mins: int = 1440  # Time between searches
    # ID of CraigslistSite to Search (ex. portland.craigslist.org)
    site_id: int = 1
    # More specific locations within a site.  Format is <site>.craigslist.org/<area>
    area: str = None
    category: str = None  # Craigslist category code.  Format is /search/<category>
    search_titles: bool = False  # Find only results with query string in title
    require_image: bool = False  # Find only results with images
    posted_today: bool = False  # Find only results posted within past 24hrs
    created_at: datetime = None  # UTC current timestamp at object creation
    last_execution_at: datetime = None
    next_execution_at: datetime = None
