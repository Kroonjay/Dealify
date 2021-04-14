from pydantic import BaseModel, validator
from core.models.craigslist.craigslist_config import CraigslistConfig
from core.enums.restriction_types import LocationRestrictionTypes, PriceRestrictionTypes


class LocationRestrictionConfig(BaseModel):
    restriction_type: int = LocationRestrictionTypes.UnitedStatesOnly.value
    source_zip: int = 98105
    max_distance: int = 0


class PriceRestrictionConfig(BaseModel):
    restriction_type: int = PriceRestrictionTypes.Unrestricted.value
    max_price: int = None


class SearchConfigIn(BaseModel):
    # JSON Stringify'd LocationRestrictionDetails object
    location_restriction_config: str = None
    price_restriction_config: str = None
    # Stringify'd CraigslistConfig Object, None if Craigslist is excluded from Search
    craigslist_config: str = None


class SearchConfig(SearchConfigIn):
    craigslist_config: CraigslistConfig = None
    price_restriction_config: PriceRestrictionConfig = None
    location_restriction_config: LocationRestrictionConfig = None

    @validator('craigslist_config', pre=True)
    def build_craigslist_config(cls, v):
        return CraigslistConfig.parse_raw(v)

    @validator('price_restriction_config', pre=True)
    def build_price_restriction_config(cls, v):
        return PriceRestrictionConfig.parse_raw(v)

    @validator('location_restriction_config', pre=True)
    def build_location_restriction_config(cls, v):
        return LocationRestrictionConfig.parse_raw(v)
