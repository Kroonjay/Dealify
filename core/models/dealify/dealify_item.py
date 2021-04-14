from pydantic import BaseModel
from typing import List
from datetime import datetime


class DealifyItemBase(BaseModel):
    item_name: str = None  # Friendly Name
    price: int = None  # Item Price
    search_id: int = None  # ID of Dealify Search that Discovered Item
    source_url: str = None  # Direct link to item listing


class DealifyItem(DealifyItemBase):
    item_id: int = None  # Database ID for each item
    tags: List[str] = None
    # When Item was identified in search
    created_at: datetime = None  # When item was discovered in Dealify Search
    last_seen_at: datetime = None  # When item was last discovered in Search
