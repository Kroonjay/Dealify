from pydantic import BaseModel
from typing import List

class CraigslistConfig(BaseModel):
    queries: List[str] = None  # List of queries to search on Craigslist
    categories: List[str] = None  # List of Craigslist Category Codes to Search
    interval_mins: int = 1440
    search_titles: bool = False
    require_image: bool = False