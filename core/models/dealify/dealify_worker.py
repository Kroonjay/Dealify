from pydantic import BaseModel, parse_raw_as, validator
from datetime import datetime
from typing import Set


class DealifyWorkerTaskConfig(BaseModel):
    allowed_task_types: Set[int] = None


class DealifyWorkerIn(BaseModel):
    worker_name: str = None
    task_config: str = None


class DealifyWorkerModel(BaseModel):
    worker_id: int = None
    worker_name: str = None
    worker_status: int = None  # DealifySearchStatus
    current_task: int = None
    task_config: DealifyWorkerTaskConfig = None
    created_at: datetime = None
    started_at: datetime = None

    @validator('task_config', pre=True)
    def build_task_config(cls, v):
        return parse_raw_as(DealifyWorkerTaskConfig, v)
