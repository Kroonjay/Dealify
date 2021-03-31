from pydantic import BaseModel
from datetime import datetime
from enum import Enum, IntEnum
from typing import List, Dict, Set
import json


def model_to_values(model):
    return tuple(model.dict().values())


def model_to_json_string(model):
    return json.dumps(model.dict())


class DealifySources(IntEnum):
    Global = 0  # Search errythang
    Craigslist = 1


class LocationRestrictionTypes(IntEnum):
    Unrestricted = 0  # Search errywhere
    # Find Country from source_zip_code field and search all sites in same country
    HomeCountry = 1
    UnitedStatesOnly = 2  # US Only
    UnitedStatesOfCanada = 3  # US and Canada
    NorthAmerica = 4
    HomeState = 5  # Find State from source_zip_code field and search all sites in same State
    HomeCity = 6  # Find City from source_zip_code field and search all sites in same City
    MilesFromHome = 7


class DealifySearchTaskTypes(IntEnum):
    Unrestricted = 0  # Worker will attempt to execute all Tasks - Dangerous
    SearchOverdueCraigslistQueries = 1  # work_overdue_craigslist_queries
    CraigslistSites = 2  # Refresh Craigslist Sites & Location Data
    # Update query_status to 2 based on last_execution_at time
    SetOverdueCraigslistQueries = 3


class PriceRestrictionTypes(IntEnum):
    Unrestricted = 0
    MaxPrice = 1
    DiscountOnly = 2


class RestrictionTypes(IntEnum):
    Unrestricted = 0
    Location = 1
    Price = 2


class LocationRestrictionConfig(BaseModel):
    restriction_type: int = LocationRestrictionTypes.UnitedStatesOnly.value
    source_zip: int = 98105
    max_distance: int = 0


class PriceRestrictionConfig(BaseModel):
    restriction_type: int = PriceRestrictionTypes.Unrestricted.value
    max_price: int = None


class DealifySearchStatus(IntEnum):
    Dormant = 0  # Enabled, but not running and not yet due
    Running = 1  # Worker is actively running Search
    Overdue = 2  # Enabled, but not running and past due
    Disabled = 3  # User Disabled
    New = 4  # Newly Created Search, set for all new searches until queries are built
    Killed = 6  # Admin Disabled
    Error = 7  # App reported Error


class DealifyWorkerStatus(IntEnum):
    Dormont = 0
    Running = 1
    Started = 5
    Killed = 6  # Admin Kill Requested, Will Finish Current Task but won't start new One
    Error = 7


class DealifyItemBase(BaseModel):
    item_name: str = None  # Friendly Name
    price: int  # Item Price
    search_id: int  # ID of Dealify Search that Discovered Item
    source_url: str  # Direct link to item listing


class DealifyItem(DealifyItemBase):
    item_id: int = None  # Database ID for each item
    tags: List[str] = None
    # When Item was identified in search
    created_at: datetime = None  # When item was discovered in Dealify Search
    last_seen_at: datetime = None  # When item was last discovered in Search


class CraigslistOverdueSearchTaskConfig(BaseModel):
    query_sleep_seconds_min: int = 5
    query_sleep_seconds_max: int = 20
    query_max_retries: int = 10
    max_queries: int = 250


class DealifySearchTaskIn(BaseModel):
    task_name: str = None  # Friendly Name, used for Logging
    task_type: int = None  # DealifySearchTaskType Enum
    task_config: str = None  # Stringify'd SearchTaskConfig Object, dependant on task_type


class DealifySearchTask(DealifySearchTaskIn):
    task_id: int = 0
    task_status: int = DealifySearchStatus.Dormant.value
    created_at: datetime = None
    last_execution_at: datetime = None


class CraigslistItemIn(DealifyItemBase):
    source_id: int
    posted_at: datetime
    is_deleted: bool
    has_image: bool
    last_updated: datetime = None
    repost_of: str = None
    item_location: str = None


class CraigslistItem(DealifyItem):
    source_id: str = None  # Craigslist Item ID for listing
    posted_at: datetime = None  # When Item was listed on CL
    is_deleted: bool = None  # If item has been deleted from CL
    has_image: bool = None  # Does the post have images
    last_updated: datetime = None  # When listing was last updated on CL
    # Whether or not this was reposted, if not null will be...
    repost_of: str = None
    item_location: str = None  # Additional location field, unreliable for location data


class CraigslistConfig(BaseModel):
    queries: List[str]  # List of queries to search on Craigslist
    interval_mins: int = 1440
    search_titles: bool = False
    require_image: bool = False
    category: str = None


class SearchConfigIn(BaseModel):
    # JSON Stringify'd LocationRestrictionDetails object
    location_restriction_config: str = LocationRestrictionConfig().json()
    price_restriction_config: str = PriceRestrictionConfig().json()
    # Stringify'd CraigslistConfig Object, None if Craigslist is excluded from Search
    craigslist_config: str = None


class SearchConfig(SearchConfigIn):
    location_restriction_config: LocationRestrictionConfig = None
    price_restriction_config: PriceRestrictionConfig = None
    craigslist_config: CraigslistConfig = None


class DealifySearchIn(BaseModel):
    search_name: str = None  # Friendly Name
    # JSON Stringify'd list of DealifySourceEnum's to Search
    sources: str = None
    # JSON Stringify'd SearchConfig object, contains config objects for all services searched, can also set max price & distance
    search_config: str = None  # JSON Stringify'd SearchConfig Model


class DealifySearch(DealifySearchIn):
    search_id: int = None  # Database ID
    search_status: int = None
    sources: List[int] = None  # List of DealifySourceEnum's to Search
    created_at: datetime = None  # When Search was created
    search_config: SearchConfig = None


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


class CraigslistQuery(CraigslistQueryIn):
    query_id: int = None  # Database ID
    # Used to Monitor status of Task Execution
    query_status: int = DealifySearchStatus.Dormant.value
    created_at: datetime = None  # UTC current timestamp at object creation
    last_execution_at: datetime = None
    next_execution_at: datetime = None

# Used to initialize CraigslistForSale object to perform Craigslist search


class CraigslistQueryExecDetails(BaseModel):
    site: str
    area: str = None
    category: str = None
    filters: Dict = None


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


class CraigslistSite(CraigslistSiteIn):
    site_id: int = None
    created_at: datetime = None
    last_searched_at: datetime = None
    last_updated_at: datetime = None
    areas: List[str]


class DealifyWorkerTaskConfig(BaseModel):
    allowed_task_types: Set[int] = None


class DealifyWorkerIn(BaseModel):
    worker_name: str = None
    task_config: str = None


class DealifyWorker(DealifyWorkerIn):
    worker_id: int = None
    worker_status: int = None  # DealifySearchStatus
    current_task: int = None
    task_config: DealifyWorkerTaskConfig = None
    created_at: datetime = None
    started_at: datetime = None
