from pydantic import BaseModel

# TODO load log messages from a JSON config file via log_messages function rather than default arguments in objects


class DealifySearchWorkerLogs(BaseModel):
    error_default_task_config_none_task_type: str = "Failed to Retrieve Default SearchTaskConfig - Task Type is None"
    error_default_task_config_unfamiliar_task_type: str = "Failed to Retrieve Default SearchTaskConfig - Unfamiliar Task Type"
    error_validate_task_config_no_task_config: str = "Function Received Invalid Input - Task Config is None"
    error_execute_search_task_none_task_config: str = "Failed to Execute Search Task - Task Config is None"
    error_execute_search_task_unfamiliar_task_type: str = "Failed to Execute Search Task - Unfamiliar Task Type"
    error_validate_task_config_ve: str = "Failed to Validate Task Config - ValidationError"
    log_execute_search_task_started: str = "Starting Search Task..."
    log_execute_search_task_finished: str = "Finished Search Task"


class DealifyLogs(BaseModel):
    search_worker: DealifySearchWorkerLogs = DealifySearchWorkerLogs()
