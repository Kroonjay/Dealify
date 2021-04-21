from pydantic import BaseModel
from typing import List

from core.configs.sheets_configs import SEARCH_RESULTS_DEFAULT_SHARE_EMAILS


class SheetsConfig(BaseModel):
    spreadsheet_id: str = None
    share_with: List[str] = None
