from os import getenv
import logging

WORKER_ID = getenv("DEALIFY_WORKER_ID")


WORKER_LOG_FILE = 'worker.log'
WORKER_LOG_LEVEL = logging.INFO
WORKER_LOG_FILE = "worker.log"


BASE_LOGGER_NAME = "DealifySearchWorker"

DEV_MODE = True

WORKER_LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
