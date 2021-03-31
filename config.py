from os import getenv
import logging

DEALIFY_DB_CREDS = {
    "host": "dealify-database-do-user-6676412-0.b.db.ondigitalocean.com",
    "port": 25060,
    "user": "dealify",
    "password": getenv("DEALIFY_DB_PASSWORD"),
    "db": "DealifyDb"
}

SEARCH_CONFIG_LOCATION_UNRESTRICTED_SEARCH_KEY = "Unrestricted"
SEARCH_CONFIG_CL_CONFIG_KEY_NAME = "craigslist_config"
SEARCH_CONFIG_LOCATION_RESTRICTION_KEY_NAME = "location_restriction_config"
SEARCH_CONFIG_PRICE_RESTRICTION_KEY_NAME = "price_restriction_config"

WORKER_LOG_FILE = "worker.log"
WORKER_LOG_LEVEL = logging.INFO

BASE_LOGGER_NAME = "DealifySearchWorker"

WORKER_LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

WORKER_ID = getenv("DEALIFY_WORKER_ID")

DEV_MODE = getenv("DEV_MODE_ENABLED")
