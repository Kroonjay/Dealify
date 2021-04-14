from pydantic import BaseModel
from datetime import datetime
from typing import List


class CraigslistItemIn(BaseModel):
    item_name: str = None  # Friendly Name
    price: int = None  # Item Price
    search_id: int = None  # ID of Dealify Search that Discovered Item
    source_url: str = None  # Direct link to item listing
    source_id: int
    posted_at: datetime
    is_deleted: bool
    has_image: bool
    last_updated: datetime = None
    repost_of: str = None
    item_location: str = None


class CraigslistItem(BaseModel):
    item_id: str = None  # Craigslist Item ID for listing
    item_name: str = None  # When Item was listed on CL
    price: int = None  # If item has been deleted from CL
    search_id: int = None  # Does the post have images
    source_url: str = None  # When listing was last updated on CL
    # Whether or not this was reposted, if not null will be...
    tags: List[str] = None
    created_at: datetime = None  # Additional location field, unreliable for location data
    last_seen_at: datetime = None
    source_id: int = None
    posted_at: datetime = None
    is_deleted: bool = None
    has_image: bool = None
    last_updated: datetime = None
    repost_of: str = None
    item_location: str = None
