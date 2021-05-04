import asyncio
import aiomysql
import pymysql
from pydantic import BaseModel, parse_obj_as, ValidationError
import logging


def values_from_model(model):
    try:
        return list(model.dict().values())
    except Exception as e:
        logging.error(
            f"Failed to Read Values From Model - Model: {model} - Data: {e}")
        return None


def model_from_row(model_cls, row: tuple):
    if not issubclass(model_cls, BaseModel):
        logging.error(
            f"Failed to Build Object from Row - Out Object must be a Class Inheriting BaseModel - Received: {type(model_cls)}")
        return None
    if not isinstance(row, tuple):
        logging.error(f"Row Object Must be a Tuple - Received: {type(row)}")
        return None
    input_keys = model_cls().dict().keys()
    input_dict = dict(zip(input_keys, row))
    try:
        model = parse_obj_as(model_cls, input_dict)
        logging.debug(f"Successfully Parsed Model from Object: {model}")
        return model
    except ValidationError as ve:
        logging.error(f"Row Validation Error - Data: {ve.json()}")
        return None


def list_from_rows(rows):
    output = []
    try:
        for row in rows:
            output.append([(item) for item in row])
        return output
    except Exception as e:
        logging.error(f"Failed to Build List from Rows - Data: {e}")
        return output


@asyncio.coroutine
def start_pool(dealify_db_creds: dict):
    if not dealify_db_creds["password"]:
        logging.critical("ERROR - Dealify Database Password is Unset!")
        return None
    pool = yield from aiomysql.create_pool(**dealify_db_creds, autocommit=True)
    logging.info("Successfully Started Connection Pool!")
    return pool


@asyncio.coroutine
def run_sproc(pool, sproc: str, params: list = None):
    if not pool:
        logging.error(
            f'Failed to Run Stored Procedure - Connection Pool is None')
        return None
    rows = None
    with (yield from pool) as conn:
        cur = yield from conn.cursor()
        try:
            if params:
                yield from cur.callproc(sproc, params)
            else:
                yield from cur.callproc(sproc)
            rows = yield from cur.fetchall()
        except ValueError as vale:
            logging.error(
                f"Run Stored Procedure - Value Error - No Response Rows - Sproc: {sproc} - Params: {params}")
        except pymysql.err.IntegrityError as ie:
            logging.error(
                f"Duplicate Key Error for Stored Procedure - Row Not Created - Sproc: {sproc} - Params: {params}")
        except pymysql.err.DataError as de:
            logging.error(
                f"Value out of Range Error for Stored Procedure - Row Not Created - Sproc: {sproc} - Params: {params}")
    logging.debug(
        f"Run Stored Procedure - Finished - Sproc: {sproc} - Response Rows: {0 if rows is None else len(rows)}")
    return rows


@asyncio.coroutine
def read_model(pool, model_cls, sproc: str, params: list = None):
    if not issubclass(model_cls, BaseModel):
        logging.error(
            f"Failed to Read Models - Model Cls Must Inherit BaseModel - Model Cls: {model_cls} - Type: {type(model_cls)} - Sproc: {sproc} - Params: {params}")
        return None
    try:
        (row,) = yield from run_sproc(pool, sproc, params)
    except ValueError as ve:
        logging.error(f"Failed to Read Models - No Rows!")
        row = None
    if not row:
        logging.error(f"Failed to Read Models - No Rows!")
        return None
    model = model_from_row(model_cls, row)
    logging.debug(
        f"Successfully Retrieved Models - Model Cls: {model_cls} - Num Items: {len(row)}")

    return model


@asyncio.coroutine
def read_models(pool, model_cls, sproc: str, params: list = None):
    if not issubclass(model_cls, BaseModel):
        logging.error(
            f"Failed to Read Models - Model Cls Must Inherit BaseModel - Received: {type(model_cls)}")
        return None
    rows = yield from run_sproc(pool, sproc, params)
    models = []
    if not rows:
        logging.error(f"Failed to Read Models - No Rows!")
        return None
    logging.debug(
        f"Successfully Retrieved Models - Model Cls: {model_cls} - Num Items: {len(rows)}")
    return [(model_from_row(model_cls, row)) for row in rows]
