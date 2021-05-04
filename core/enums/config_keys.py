from enum import Enum
import os


class ConfigKeys(Enum):
    # Must be hard-coded or pulled from env, used prior to DB connection
    BASE_LOGGER_NAME = 'DealifyLogger'
    LOGGER_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    APP_ROOT_PATH = os.getenv("APP_ROOT_PATH") if os.getenv(
        "APP_ROOT_PATH") else "/Dealify"

    DEALIFY_DB_HOST = "dealify-database-do-user-6676412-0.b.db.ondigitalocean.com"
    DEALIFY_DB_PORT = 25060
    DEALIFY_DB_USERNAME = 'dealify'
    DEALIFY_DB_PASSWORD = os.getenv("DEALIFY_DB_PASSWORD")
    DEALIFY_DB_DATABASE = 'DealifyDb'

    # key_name values to pull from ConfigKeys table
    NOMINATIM_USER_AGENT = 'NominatimUserAgent'

    # Config Keys used by Craigslist Module
    CRAIGSLIST_SEARCH_INTERVAL_MIN = 'CraigslistSearchIntervalMinimum'
    CRAIGSLIST_SEARCH_INTERVAL_MAX = 'CraigslistSearchIntervalMaximum'
    CRAIGSLIST_SEARCH_INTERVAL_DEFAULT = 'CraigslistSearchIntervalDefault'
    CRAIGSLIST_QUERY_SLEEP_INTERVAL_MIN = 'CraigslistQuerySleepIntervalMinimum'
    CRAIGSLIST_QUERY_SLEEP_INTERVAL_MAX = 'CraigslistQuerySleepIntervalMaximum'
    CRAIGSLIST_RATE_LIMIT_SLEEP_INTERVAL = 'CraigslistRateLimitSleepInterval'
    CRAIGSLIST_QUERY_MAX_RETRIES = 'CraigslistQueryMaxRetries'
    CRAIGSLIST_MAX_QUERIES_PER_TASK = 'CraigslistMaxQueriesPerTask'
    CRAIGSLIST_ITEM_OLD_INTERVAL_DAYS = 'CraigslistItemOldIntervalDays'

    # Config Keys used by Sheets Module
    SHEETS_API_CREDENTIALS = 'SheetsApiCredentials'
    SHEETS_NEW_SEARCHES_SPREADSHEET_ID = 'SheetsNewSearchesSpreadsheetId'
    SHEETS_NEW_SEARCHES_HEADER_RANGE = 'SheetsNewSearchesHeaderRange'
    SHEETS_NEW_SEARCHES_DATA_RANGE = 'SheetsNewSearchesDataRange'
    SHEETS_API_SCOPES = 'SheetsApiScopes'
    SHEETS_BOOLEAN_TRUE_STRING = 'SheetsBooleanTrueString'
    SHEETS_BOOLEAN_FALSE_STRING = 'SheetsBooleanFalseString'
    SHEETS_MULTIPLE_CELL_VALUE_SEPARATION_CHAR = 'SheetsMultipleValueSeparationCharacter'
    SHEETS_SEARCH_RESULTS_PAGE_NAMES = 'SheetsResultsPageNames'
    SHEETS_SEARCH_RESULTS_PAGE_ROW_LIMIT = 'SheetsSearchResultsPageRowLimit'
    SHEETS_SEARCH_RESULTS_PAGE_COLUMN_LIMIT = 'SheetsSearchResultsPageColumnLimit'
    SHEETS_SEARCH_RESULTS_DEFAULT_SHARE_EMAILS = 'SheetsSearchResultsDefaultShareEmails'
    SHEETS_MAX_SEARCH_RESULTS_PER_TASK = 'SheetsMaxSearchResultsPerTask'
