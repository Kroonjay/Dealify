import logging
import asyncio

from googleapiclient.discovery import build
from google.oauth2 import service_account
from pydantic import ValidationError
from core.configs.sheets_configs import SERVICE_ACCOUNT_CREDS_FILE, API_SCOPES, SPREADSHEET_ID, NEW_SEARCH_HEADER_RANGE, NEW_SEARCH_DATA_RANGE
from core.models.google_sheets.new_search_sheet_row import NewSearchSheetRow
from core.utils.sheets_utils import dealify_search_from_sheet_row
from core.models.dealify.dealify_search import DealifySearch
from core.database.db_helpers import run_sproc, values_from_model
from core.database.sprocs import create_dealify_search_sproc, read_dealify_search_by_name_sproc


async def run_task_create_new_dealify_searches_from_sheets(pool):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_CREDS_FILE, scopes=API_SCOPES)
    if not creds:
        logging.error(f"Failed to Load Service Account Credentials")
        return None

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    headers = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                 range=NEW_SEARCH_HEADER_RANGE).execute()
    ds_input_dict_keys = headers.get('values', [])[0]
    if not ds_input_dict_keys:
        logging.error(
            f"Failed to Load Dealify Search Inputs - Header Row is None")
        return None
    new_search_rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                         range=NEW_SEARCH_DATA_RANGE).execute()
    rows = new_search_rows.get('values', [])
    new_search_count = 0
    duplicate_search_count = 0
    for row in rows:
        if row:
            nssr_input_dict = dict(zip(ds_input_dict_keys, row))
            try:
                nssr = NewSearchSheetRow(**nssr_input_dict)
            except ValidationError as ve:
                logging.error(
                    f"Failed to Validate NewSearchSheetsRow - Data: {ve.json()}")
            dsi = dealify_search_from_sheet_row(nssr)
            if not dsi:
                logging.error(
                    f"Failed to Create Dealify Search From Sheet Row - Skipping")
                continue
            sheet_exists = await run_sproc(pool, read_dealify_search_by_name_sproc, [dsi.search_name])
            if sheet_exists:
                logging.debug(
                    f"Dealify Search with Name Already Exists - Skipping - Search Name: {dsi.search_name}")
                duplicate_search_count += 1
                continue
            else:
                values = values_from_model(dsi)
                await run_sproc(pool, create_dealify_search_sproc, values)
                new_search_count += 1
                logging.debug(
                    f"New Dealify Search Created from Sheets - Search Name: {dsi.search_name}")
    logging.info(
        f"Successfully Created New Dealify Searches from Sheets - Rows: {len(rows)} - New Searches: {new_search_count} - Duplicates: {duplicate_search_count}")
