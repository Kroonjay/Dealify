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

test_header_fmt = cellFormat(
    backgroundColor=color.fromHex('#b7b7b7'),
    textFormat=textFormat(
        bold=True, fontSize=16, foregroundColor=color.fromHex('#000000')),
    horizontalAlignment='CENTER'
)


async def run_task_update_dealify_search_results_sheets(pool):

    try:
        svc_acc = gspread.service_account(filename=SERVICE_ACCOUNT_CREDS_FILE)
        print("Loaded Service Account")
    except FileNotFoundError:
        logging.error(
            f"Failed to Run Google Sheets Task - Service Account Credential File Not Found")
        return None

    searches_to_update = await read_models(pool, DealifySearch, read_dealify_searches_by_status_sproc, [DealifySearchStatus.Dormant.value, 250])
    print(f"Found {len(searches_to_update)} Searches to Update!")
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
                    sheet_name, cols=SEARCH_RESULTS_PAGE_DEFAULT_COLUMN_LENGTH, rows=SEARCH_RESULTS_PAGE_DEFAULT_ROW_LENGTH)
                worksheet = sheet.worksheet(sheet_name)
            if not worksheet:
                logging.error(
                    f'Failed to Retrieve Worksheet even after creating, skipping this Sheet name in Searcvh - Sheet Name: {sheet_name} - Search: {search.search_id}')
                continue

            try:
                worksheet.delete_rows(
                    2, SEARCH_RESULTS_PAGE_DEFAULT_ROW_LENGTH)
            except gspread.exceptions.APIError as gspe:
                logging.error(
                    f"Received InvalidArgument Error - Spreadsheet has No Rows to Delete")
                logging.error(f"Unknown APIError - Data: {gspe.args}")
            items_to_add = await read_models(pool, CraigslistItem, read_craigslist_items_by_search_id_sproc, [search.search_id, SEARCH_RESULTS_PAGE_DEFAULT_ROW_LENGTH])
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
