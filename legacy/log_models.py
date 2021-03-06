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
    log_build_queries_task_no_new_searches: str = "Create Queries for New Searches Task Not Executed - No New Searches"
    log_build_queries_task_started: str = "Create Queries for New Searches Task - Starting Now..."
    log_build_queries_task_finished: str = "Create Queries for New Searches Task - Finished"
    error_build_queries_task_unknown_search_id: str = "Failed to Retrieve Dealify Search - Invalid Search ID"
    debug_build_queries_query_finished: str = "Create Queries for New Searches Task - Completed Query"
    error_value_is_none: str = "Required Value '{value}' is None"
    error_enum_invalid_option: str = "{enum_name} Received Invalid Option - New Value: {new_value} Does Not Exist in Enum Values"
    error_enum_illegal_option: str = "{enum_name} Received Illegal Option - Illegal to Update to New Value: {new_value} from Old Value: {old_value}"
    log_enum_update_finished: str = "{enum_name} Update Finished - Successfully Updated to New Value: {new_value} from Old Value: {old_value}"


class ErrorLogs(BaseModel):
    required_value_is_none: str = 'Operation Failed - Required Value is None - Value: {value}'
    required_value_invalid_type: str = 'Operation Failed - Required Value is Invalid Type - Received: {received} - Required: {required}'
    enum_option_unsupported: str = 'Unsupported Option for Enum - Enum: {enum} - Option: {option}'
    model_validation_failed: str = 'Model Validation Failed - Model: {model} - Input Data: {data} - Error Msg: {error}'
    database_not_connected: str = 'Unable to Connect to Database'
    query_no_return_values: str = 'Query Expected Return Rows but Received None - Query: {query} - Params: {params}'
    worker_no_task_types: str = 'Worker Started but has No Task Types - Worker ID: {worker_id}'
    worker_no_task_ids: str = 'Worker Found No Task IDs for All Task Types - Worker ID: {worker_id} - Task Types: {task_types}'


class InfoLogs(BaseModel):
    database_connected: str = 'Successfully Connected to Dealify Database'


class DealifyLogs(BaseModel):
    search_worker: DealifySearchWorkerLogs = DealifySearchWorkerLogs()
