import asyncio
import gspread
import logging

from gspread_formatting import *

from core.database.db_helpers import read_model, read_models, values_from_model
from core.database.sprocs import read_dealify_searches_by_status_sproc, read_craigslist_items_by_search_id_sproc
from core.models.dealify.dealify_search import DealifySearch
from core.enums.statuses import DealifySearchStatus
from core.enums.sources import DealifySources
from core.utils.sheets_utils import new_spreadsheet_body_base
from core.utils.dealify_utils import update_dealify_search_config
from core.configs.sheets_configs import SERVICE_ACCOUNT_CREDS_FILE, SEARCH_RESULTS_PAGE_NAMES, SEARCH_RESULTS_PAGE_DEFAULT_COLUMN_LENGTH, SEARCH_RESULTS_PAGE_DEFAULT_ROW_LENGTH
from core.models.craigslist.craigslist_item import CraigslistItem
from core.models.google_sheets.sheets_config import SheetsConfig
from core.utils.dealify_utils import read_config_key
from core.enums.config_keys import ConfigKeys
test_header_fmt = cellFormat(
    backgroundColor=color.fromHex('#b7b7b7'),
    textFormat=textFormat(
        bold=True, fontSize=16, foregroundColor=color.fromHex('#000000')),
    horizontalAlignment='CENTER'
)


async def run_task_update_dealify_search_results_sheets(pool):
    creds = await read_config_key(pool, ConfigKeys.SHEETS_API_CREDENTIALS)
    if not creds:
        logging.error(f"Failed to Run Google Sheets Task - No Credentials")
    svc_acc = gspread.service_account_from_dict(creds.config_value)
    logging.debug('Loaded Service Account')
    max_searches_per_task_key = await read_config_key(pool, ConfigKeys.SHEETS_MAX_SEARCH_RESULTS_PER_TASK)
    max_searches_per_task = max_searches_per_task_key.config_value
    column_limit_key = await read_config_key(pool, ConfigKeys.SHEETS_SEARCH_RESULTS_PAGE_COLUMN_LIMIT)
    column_limit = column_limit_key.config_value
    row_limit_key = await read_config_key(pool, ConfigKeys.SHEETS_SEARCH_RESULTS_PAGE_ROW_LIMIT)
    row_limit = row_limit_key.config_value
    default_share_emails_key = await read_config_key(pool, ConfigKeys.SHEETS_SEARCH_RESULTS_DEFAULT_SHARE_EMAILS)
    default_share_emails = default_share_emails_key.config_value
    searches_to_update = await read_models(pool, DealifySearch, read_dealify_searches_by_status_sproc, [DealifySearchStatus.Dormant.value, max_searches_per_task])
    logging.info(f"Found {len(searches_to_update)} Searches to Update!")
    for search in searches_to_update:

        if DealifySources.GoogleSheets.value in search.sources:
            logging.debug(f"Found GoogleSheets in Sources! - Search: {search}")
            if not search.search_config.sheets_config:
                search.search_config.sheets_config = SheetsConfig()
                logging.debug(
                    f"Found GoogleSheets in Sources but No Sheets Config - Search ID: {search.search_id}")
            if not search.search_config.sheets_config.spreadsheet_id:
                body = new_spreadsheet_body_base(search)
                spreadsheet = svc_acc.create(
                    f"Search Results - {search.search_name[:30]}")
                logging.info(
                    f"Created Spreadsheet - Spreadsheet ID: {spreadsheet.id}")
                spreadsheet.share('videogameking96@gmail.com',
                                  perm_type='user', role='writer')
                search.search_config.sheets_config.spreadsheet_id = spreadsheet.id
                search = await update_dealify_search_config(pool, search)
                if not search.search_config.sheets_config.spreadsheet_id:
                    logging.error(
                        f"SpreadSheetID still Unset after Creation and Config Update - Search ID: {search.search_id}")
                    return None
            sheet = svc_acc.open_by_key(
                search.search_config.sheets_config.spreadsheet_id)

            worksheet = None
            sheet_name = 'CraigslistItems'
            try:
                worksheet = sheet.worksheet(sheet_name)
                logging.debug("Opened Worksheet")
            except gspread.exceptions.WorksheetNotFound as wne:
                logging.error(
                    f"Received WorksheetNotFound Error, Attempting to Create - Sheet Name: {sheet_name} - Search ID: {search.search_id}")
                sheet.add_worksheet(
                    sheet_name, cols=column_limit, rows=row_limit)
                worksheet = sheet.worksheet(sheet_name)
            if not worksheet:
                logging.error(
                    f'Failed to Retrieve Worksheet even after creating, skipping this Sheet name in Searcvh - Sheet Name: {sheet_name} - Search: {search.search_id}')
                continue

            try:
                worksheet.delete_rows(
                    2, row_limit)
            except gspread.exceptions.APIError as gspe:
                logging.error(
                    f"Received InvalidArgument Error - Spreadsheet has No Rows to Delete")
                logging.error(f"Unknown APIError - Data: {gspe.args}")
            items_to_add = await read_models(pool, CraigslistItem, read_craigslist_items_by_search_id_sproc, [search.search_id, row_limit])
            headers = list(CraigslistItem().dict().keys())
            item_data = []
            item_data.append(headers)

            if not items_to_add:
                item_data.append(['No Items'])
            else:
                for item in items_to_add:
                    values = values_from_model(item)
                    item_data.append(values)
            worksheet.update('A1', item_data)
            format_cell_ranges(worksheet, [('A1:O1', test_header_fmt)])
            logging.info("Success!")
