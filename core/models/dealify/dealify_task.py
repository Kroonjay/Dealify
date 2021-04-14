from pydantic import BaseModel
from core.enums.statuses import DealifySearchStatus
from datetime import datetime


class DealifyTaskIn(BaseModel):
    task_name: str = None  # Friendly Name, used for Logging
    task_type: int = None  # DealifySearchTaskType Enum
    task_config: str = None  # Stringify'd SearchTaskConfig Object, dependant on task_type


class DealifyTask(BaseModel):
    task_id: int = 0
    task_name: str = None  # Friendly Name, used for Logging
    task_type: int = None  # DealifySearchTaskType Enum
    task_status: int = None
    task_config: str = None  # Stringify'd SearchTaskConfig Object, dependant on task_type
    created_at: datetime = None
    last_execution_at: datetime = None
