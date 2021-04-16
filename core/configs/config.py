from os import getenv
import logging

DEALIFY_DB_CREDS = {
    "host": "dealify-database-do-user-6676412-0.b.db.ondigitalocean.com",
    "port": 25060,
    "user": "dealify",
    "password": getenv("DEALIFY_DB_PASSWORD"),
    "db": "DealifyDb"
}

BASE_LOGGER_NAME = "DealifySearchWorker"

LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

APP_ROOT_PATH = getenv("APP_ROOT_PATH") if getenv(
    "APP_ROOT_PATH") else "/Dealify"

MODEL_REFERENCE_PATH = '#/definitions/'

SCHEMA_PATH = 'schemas/'
SCHEMA_ACTIVE_FILE_EXTENSION = '-Latest.json'

DEALIFY_NOMINATIM_USER_AGENT = 'dealify'

DEV_MODE = os.getenv("DEV_MODE")
