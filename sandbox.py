from pydantic import BaseModel, parse_raw_as, parse_obj_as
from dealify_worker import DealifyWorker
import pprint as pp
import pydantic
import asyncio
import json
from datetime import datetime
from config import *
from models import *
from sprocs import *
from dealify_tasks import create_queries_for_new_searches
from database_helpers import *
from model_map import model_from_name, schema_from_name
from typing import Optional, Union, List, Dict, Any, Mapping, Type, TypeVar, Generic
import os

clc = CraigslistConfig(
    queries=["Culvert", '12" pipe', "drainage pipe", "drain tile"], categories=["gra", "maa", "foa", "hva"])

lrc_in = LocationRestrictionConfig(
    restriction_type=LocationRestrictionTypes.HomeState.value, source_zip=98208)

sc_in = SearchConfigIn(
    location_restriction_config=lrc_in.json(), craigslist_config=clc.json())


dwtc_in = DealifyWorkerTaskConfig(allowed_task_types=[5])

dw_in = DealifyWorkerIn(worker_name="Test-Craigslist-OldItemsOnly",
                        task_config=dwtc_in.json())

dsi = DealifySearchIn(search_name="Gimme dat Pipe",
                      sources=json.dumps([1]), search_config=sc_in.json())

otc = CheckOldCraigslistItemDeletedTaskConfig()

dst_in = DealifySearchTaskIn(task_name="Check Old Craigslist Items and Set is_deleted Status",
                             task_type=5, task_config=otc.json())


# async def test_create_craigslist_site():
#     conn = await connect_dealify_db(DEALIFY_DB_CREDS)
#     # await create_dealify_search_task(dst_in, conn)
#     # items = await read_old_craigslist_item_ids(2, conn)
#     # await create_dealify_worker(dw_in, conn)
#     # await create_dealify_search(dsi, conn)
#     # result = await create_queries_for_new_searches(conn)
#     # new_search_ids = await read_new_dealify_search_ids(conn)
#     # dst = await read_dealify_search_task_by_id(2, conn)
#     # dst = await start_next_dealify_search_task(dst.task_id, conn)
#     disconnect_dealify_db(conn)

def model_name_from_ref(model_ref: str):
    ref_path = MODEL_REFERENCE_PATH
    model_name = None
    try:
        split_ref = model_ref.split(ref_path)
    except Exception as e:
        logging.error(
            f"Failed to Split Base Reference Path - Model Ref is Invalid - Model Ref: {model_ref} - Base Path: {ref_path} - Data: {e}")
        return model_name
    if not len(split_ref) == 2:
        logging.error(
            f"Invalid Number of Sections for Reference Path - Model Ref is Invalid - Model Ref: {model_ref} - Base Path: {ref_path} - Split Reference: {split_ref}")
        return model_name
    else:
        model_name = split_ref[1]
        logging.debug(
            f"Retrieved Model Name from Reference Path - Model Name: {model_name} - Model Ref: {model_ref} - Base Path: {ref_path}")
        return model_name


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


def model_properties_from_schema(schema: dict):
    model_props = dict()
    title_key = 'title'
    properties_key = 'properties'
    ref_key = '$ref'
    try:
        model_name = schema['title']
    except Exception as e:
        logging.error(
            f"Title Key Not Found in Schema - Input Schema is Invalid - Title Key: {title_key} - Schema: \n{schema}")
        return model_props

    if not properties_key in schema.keys():
        logging.error(
            f"Properties Key Not Found in Schema - Input Schema is Invalid - Model: {model_name} Properties Key: {properties_key} - Schema: \n {schema}")
        return model_props
    else:
        for prop, value_dict in schema[properties_key].items():
            if ref_key in value_dict.keys():
                model_ref = value_dict[ref_key]
                nested_model_name = model_name_from_ref(model_ref)
                if not nested_model_name:
                    logging.error(
                        f"Failed to Get Model Name from Reference Path - Reference Key is Invalid - Model: {model_name} - Reference Path: {model_ref} - Schema: \n{schema}")
                    continue
                logging.debug(
                    f"Retrieved Nested Model Name from Schema - Model: {model_name} - Nested Model: {nested_model_name}")
                nested_model = model_from_name(nested_model_name)
                if not nested_model:
                    logging.error(
                        f"Failed to Retrieve Nested Model from Map - Model: {model_name} - Nested Model: {nested_model_name}")
                    continue
                else:
                    model_props[prop] = nested_model
            else:
                logging.debug(
                    f"Model Property is Not Nested Object - Model: {model_name} - Property: {prop} - Values: {value_dict}")
                model_props[prop] = None
    logging.debug(
        f"Retrieved Properties for Model: {model_name} - Properties: {model_props}")
    return model_props


def get_props(model):
    schema = None
    # if isinstance(model, dict):
    #     class_name = next(iter(model))
    #     print(
    #         f"Successfully Loaded Schema from Dict - Class Name: {class_name}")
    #     return class_name().dict()
    try:
        if issubclass(model, BaseModel):
            schema = model().dict()
            print(
                f"Successfully Loaded Input Props from Class Reference - Class Name: {model}")
            return schema
    except TypeError:
        print("Received TypeError for Input Props - Model is Not a Class")
    try:
        if not schema and issubclass(model.__name__, BaseModel):
            schema = model.dict()
            print(
                f"Successfully Loaded Schema from Class Instance - Class Name: {model.__name__}")
            return schema
    except AttributeError as ae:
        print("Received TypeError for Input Dict Props - Model is Not Instance of Class")
    print(
        f"Failed to Load Schema from Model - Model is Not a Dict, BaseModel Class Reference, or Instance of BaseModel Class - Type: {type(model)}")
    return schema


def input_dict_props(model):
    props_dict = dict()
    schema = get_props(model)
    if not schema:
        print("Failed to Build Input Dict Props - No Schema")
        return None
    model_props = model.dict().keys()
    for key, value in model_props.items():
        # if value:
        #     nested_input_dict = input_dict_props(value)
        #     print(f"NESTED INPUT DICT: {nested_input_dict}")
        #     props_dict[key] = {value: nested_input_dict}
        # else:
        props_dict[key] = value
    print(
        f"Finished Creating Props Dict - Model: {model} - Items: {props_dict.items()}")
    return props_dict


async def new_test_func():
    pool = await start_pool(DEALIFY_DB_CREDS)
    rows = await run_sproc(pool, read_craigslist_items_by_search_id_sproc, [4, 100])
    for row in rows:
        ds = model_from_row(NewCraigslistItem, row)

        print(ds.search_id)
        # input_dict_keys = [(prop) for prop in schema['properties']]
        # print(f"Input Dictionary Keys: {input_dict_keys}")

    return
    # for item, values in schema['definitions'].items():
    #     if values['type'] == 'object':
    #         print(values)


def get_schema_file_path(schema):
    path_to_schemas = os.path.join(APP_ROOT_PATH, SCHEMA_PATH)
    schema_file_ext = SCHEMA_ACTIVE_FILE_EXTENSION
    try:
        model_name = schema['title']
    except Exception as e:
        logging.error(f"Schema File Name is Invalid - Schema: \n{schema}")
        return
    out_file_name = ''.join([model_name, schema_file_ext])
    return os.path.join(path_to_schemas, out_file_name)


def pydantic_to_sqlalchemy(schema: pydantic.main.ModelMetaclass) -> Any:
    __fields_dict__ = {}

    def recurse(obj: pydantic.main.ModelMetaclass, temp_key: str = "") -> None:
        if isinstance(obj, pydantic.main.ModelMetaclass):
            for key, value in obj.schema().items():
                recurse(obj=value, temp_key=temp_key +
                        key if temp_key else key)

        if isinstance(obj, dict):
            for key, value in obj.items():
                recurse(obj=value, temp_key=temp_key +
                        key if temp_key else key)

        if isinstance(obj, list):
            for item in range(len(obj)):
                recurse(
                    obj=obj[item],
                    temp_key=temp_key + str(item) if temp_key else str(item),
                )
        else:
            __fields_dict__[temp_key] = obj

    recurse(schema)
    return __fields_dict__


def save_schema(model, overwrite=False):
    if not issubclass(model, BaseModel):
        logging.error(
            f"Failed to Save Schema - Input Object must Inherit BaseModel")
        return
    schema = model.schema()
    out_file_path = get_schema_file_path(schema)
    if os.path.isfile(out_file_path):
        if not overwrite:
            logging.error(
                f"Schema File Already Exists but Overwrite is Disabled - Schema File Path: {out_file_path}")
            return
    with open(out_file_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=4)
        logging.info(
            f"Successfully Saved Schema to File - Schema File Path: {out_file_path}")


loop = asyncio.get_event_loop()
loop.run_until_complete(new_test_func())
