from pydantic import BaseModel, parse_raw_as, validator
from typing import List
from datetime import datetime
from core.models.dealify.search_config import SearchConfig


class DealifySearchIn(BaseModel):

    # JSON Stringify'd list of DealifySourceEnum's to Search
    sources: str = None
    # JSON Stringify'd SearchConfig object, contains config objects for all services searched, can also set max price & distance
    search_config: str = None  # JSON Stringify'd SearchConfig Model


class DealifySearch(BaseModel):
    search_id: int = None  # Database ID
    search_status: int = None
    search_name: str = None  # Friendly Name
    sources: List[int] = None  # List of DealifySourceEnum's to Search
    search_config: SearchConfig = None
    created_at: datetime = None  # When Search was created

    @validator('sources', pre=True)
    def build_sources_list(cls, v):
        return parse_raw_as(List[int], v)

    @validator('search_config', pre=True)
    def build_search_config(cls, v):
        return SearchConfig.parse_raw(v)
