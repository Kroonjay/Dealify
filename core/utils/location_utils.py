import logging
import re

from pydantic import BaseModel, ValidationError
from geopy.geocoders import Nominatim

from core.configs.config import DEALIFY_NOMINATIM_USER_AGENT


def parse_price(source_price):
    if not source_price:
        return None
    out_price = ''.join(i for i in source_price if i.isalnum())
    return int(out_price)


def parse_special(source_text):
    if not source_text:
        return None
    # Simple regex to strip all special chars https://stackoverflow.com/questions/43358857/how-to-remove-special-characters-except-space-from-a-file-in-python/43358965
    out_text = re.sub(r"\W+|_", " ", source_text)
    return out_text


class LocationDetails(BaseModel):
    city: str = None
    state: str = None
    county: str = None
    zip_code: str = None
    country: str = None


def query_location(address):
    if not isinstance(address, str):
        if isinstance(address, int):
            address = str(address)
        else:
            logging.error(f"Address Must be a String, Got: {type(address)}")
            return None
    geolocator = Nominatim(user_agent=DEALIFY_NOMINATIM_USER_AGENT)
    location = geolocator.geocode(address)
    split_address = location.address.split(",")
    # Format should be City, County, State, Zip, Country
    if len(split_address) == 5:
        try:
            loc_details = LocationDetails(
                city=parse_special(split_address[0]).strip(),
                county=parse_special(split_address[1]).strip(),
                state=parse_special(split_address[2]).strip(),
                zip_code=parse_special(split_address[3]).strip(),
                country=parse_special(split_address[4]).strip())
            return loc_details
        except ValidationError as ve:
            logging.error(
                f"Failed to Validate Location - Details: {ve.json()}")
            return None
    else:
        logging.error(
            f"Failed to Validate Location - Not Enough Address Sections - Needed 5, Got {len(split_address)}")
        return None
