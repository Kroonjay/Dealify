import logging

from config import BASE_LOGGER_NAME, DEV_MODE
from log_models import DealifyLogs


def log_messages():
    return DealifyLogs()


def log(log_msg, data=None):
    if not isinstance(log_msg, str):
        return
    if data:
        log_msg = f"{log_msg}\n{data}"
    logger_name = f"{BASE_LOGGER_NAME}.{__name__}"
    logger = logging.getLogger(logger_name)
    logger.info(log_msg)


def log_debug(log_msg, data=None):
    if not isinstance(log_msg, str):
        return
    if DEV_MODE:
        if data:
            log_msg = f"{log_msg} - Data:\n{data}"
        logger_name = f"{BASE_LOGGER_NAME}.{__name__}"
        logger = logging.getLogger(logger_name)
        logger.info(log_msg)


def log_error(log_msg, is_critical=False, data=None):
    if not isinstance(log_msg, str):
        return
    if data:
        log_msg = f"{log_msg} - Data:\n{data}"
    logger_name = f"{BASE_LOGGER_NAME}.{__name__}"
    logger = logging.getLogger(logger_name)
    if is_critical:
        logger.critical(log_msg)
    else:
        logging.error(log_msg)
