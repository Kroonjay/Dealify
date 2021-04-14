from pydantic import BaseModel


class CraigslistOverdueQueriesTaskConfig(BaseModel):
    query_sleep_seconds_min: int = 5
    query_sleep_seconds_max: int = 20
    rate_limit_sleep_seconds: int = 60
    query_max_retries: int = 10
    max_queries: int = 250


class CraigslistOldDeletedItemsTaskConfig(BaseModel):
    old_interval_days: int = 2
    sleep_seconds_min: int = 5
    sleep_seconds_max: int = 20
    rate_limit_sleep_seconds: int = 60
    max_items: int = 250
