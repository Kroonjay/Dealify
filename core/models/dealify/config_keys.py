from pydantic import BaseModel, validator
from enum import IntEnum
from datetime import datetime
from typing import Any
import json


class ConfigKeyTypes(IntEnum):
    numeric = 1
    string = 2
    kv_map = 3


class ConfigKeyIn(BaseModel):
    key_name: str = None
    config_value: str = None
    notes: str = None

    @validator('config_value', pre=True)
    def dump_config_value(cls, v):
        config_value = None
        try:
            config_value = json.dumps(v)
        except Exception as e:
            logging.error(
                f"Failed to Dump Config Key Value - Data: {e} - Input: {v}")
        return config_value


class ConfigKey(BaseModel):
    key_id: int = None
    key_name: str = None
    config_value: Any = None
    created_at: datetime = None
    last_used_at: datetime = None
    last_updated_at: datetime = None
    notes: str = None

    @validator('config_value', pre=True)
    def load_config_value(cls, v):
        config_value = None
        try:
            config_value = json.loads(v)
        except Exception as e:
            logging.error(
                f"Failed to load Config Key Value - Data: {e} - Input: {v}")
        return config_value
