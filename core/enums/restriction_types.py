from enum import IntEnum


class LocationRestrictionTypes(IntEnum):
    Unrestricted = 0  # Search errywhere
    # Find Country from source_zip_code field and search all sites in same country
    HomeCountry = 1
    UnitedStates = 2  # US Only
    UnitedStatesOfCanada = 3  # US and Canada
    NorthAmerica = 4
    HomeState = 5  # Find State from source_zip_code field and search all sites in same State
    HomeCity = 6  # Find City from source_zip_code field and search all sites in same City
    MilesFromHome = 7


class PriceRestrictionTypes(IntEnum):
    Unrestricted = 0
    DiscountAny = 1
    DiscountFivePercent = 2


class RestrictionTypes(IntEnum):
    Unrestricted = 0
    Location = 1
    Price = 2
