from enum import IntEnum


class DealifyTaskTypes(IntEnum):
    Unrestricted = 0  # Worker will attempt to execute all Tasks - Dangerous
    CraigslistSearchOverdueQueries = 1  # work_overdue_craigslist_queries
    CraigslistSites = 2  # Refresh Craigslist Sites & Location Data
    # Update query_status to 2 based on last_execution_at time
    CraigslistSetOverdueQueries = 3
    CraigslistQueriesForNewDealifySearches = 4
    CraigslistSearchOldDeletedItems = 5
    SheetsCreateNewSearches = 6
    SheetsUpdateSearchResults = 7
