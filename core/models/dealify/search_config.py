from pydantic import BaseModel, validator, ValidationError
from core.models.craigslist.craigslist_config import CraigslistConfig
from core.models.google_sheets.sheets_config import SheetsConfig
from core.enums.restriction_types import LocationRestrictionTypes, PriceRestrictionTypes


class LocationRestrictionConfig(BaseModel):
    restriction_type: int = LocationRestrictionTypes.HomeCity.value
    source_zip: int = 98105
    max_distance: int = 0


class PriceRestrictionConfig(BaseModel):
    restriction_type: int = PriceRestrictionTypes.Unrestricted.value
    standard_price: int = 1


class SearchConfigIn(BaseModel):
    # JSON Stringify'd LocationRestrictionDetails object
    location_restriction_config: str = None
    price_restriction_config: str = None
    # Stringify'd CraigslistConfig Object, None if Craigslist is excluded from Search
    craigslist_config: str = None
    sheets_config: str = None


class SearchConfig(BaseModel):
    craigslist_config: CraigslistConfig = None
    price_restriction_config: PriceRestrictionConfig = None
    location_restriction_config: LocationRestrictionConfig = None
    sheets_config: SheetsConfig = None

    @validator('craigslist_config', pre=True)
    def build_craigslist_config(cls, v):
        if isinstance(v, str):
            return CraigslistConfig.parse_raw(v)
        elif isinstance(v, dict):
            return CraigslistConfig.parse_obj(v)
        elif isinstance(v, CraigslistConfig):
            return v
        elif not v:
            return None
        else:
            print(
                f"Craigslist Config - Unrecognized Type - Type: {type(v)} - Data: {v}")
            return None

    @validator('price_restriction_config', pre=True)
    def build_price_restriction_config(cls, v):
        if isinstance(v, str):
            return PriceRestrictionConfig.parse_raw(v)
        elif isinstance(v, dict):
            return PriceRestrictionConfig.parse_obj(v)
        elif isinstance(v, PriceRestrictionConfig):
            return v
        elif not v:
            return None
        else:
            print(
                f"PriceRestrictionConfig - Unrecognized Type - Type: {type(v)} - Data: {v}")
            return None

    @validator('location_restriction_config', pre=True)
    def build_location_restriction_config(cls, v):
        if isinstance(v, str):
            return LocationRestrictionConfig.parse_raw(v)
        elif isinstance(v, dict):
            return LocationRestrictionConfig.parse_obj(v)
        elif isinstance(v, LocationRestrictionConfig):
            return v
        elif not v:
            return None
        else:
            print(
                f"LocationRestrictionConfig - Unrecognized Type - Type: {type(v)} - Data: {v}")
            return None

    @validator('sheets_config', pre=True)
    def build_sheets_config(cls, v):
        if isinstance(v, str):
            return SheetsConfig.parse_raw(v)
        elif isinstance(v, dict):
            return SheetsConfig.parse_obj(v)
        elif isinstance(v, SheetsConfig):
            return v
        elif not v:
            return None
        else:
            print(
                f"Sheets Config - Unrecognized Type - Type: {type(v)} - Data: {v}")
            return None
