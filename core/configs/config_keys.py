from pydantic import BaseModel


class ConfigKeys(BaseModel):
    base_logger_name: str = 'DealifyWorker'
    logger_format: str = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    app_root_path: str = os.getenv("APP_ROOT_PATH") if os.getenv(
        "APP_ROOT_PATH") else "/Dealify"
    nominatim_user_agent: str = "NotYoMammasUserAgent"
