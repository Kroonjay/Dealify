from __future__ import print_function
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from core.models.dealify.dealify_search import DealifySearchIn
from core.models.dealify.search_config import SearchConfig, LocationRestrictionConfig, PriceRestrictionConfig, SearchConfigIn
from core.models.craigslist.craigslist_config import CraigslistConfig
from core.enums.restriction_types import LocationRestrictionTypes, PriceRestrictionTypes
from core.enums.sources import DealifySources
from core.database.db_helpers import run_sproc, values_from_model
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '12G-EDF2dxhcNKkUHTExqJFJmwQTTs_My1h79GPURR9g'
SAMPLE_RANGE_NAME = 'NewSearches!A2:M'


def run_task_create_new_dealify_search():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if not os.path.exists('token.json'):
        print("NO Token File")
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    new_searches = []
    if not values:
        print('No data found.')
    else:
        print('Rows:')
        for row in values:
            search_name = row[1]
            sources = []
            if row[2] == 'Yes':
                if row[4] == 'United States':
                    lr_type = LocationRestrictionTypes.UnitedStates.value
                else:
                    print(
                        f"Unsupported Location Restriction Type - Type: {row[4]}")
                    continue
                source_zip = row[3]
                lrc = LocationRestrictionConfig(
                    restriction_type=lr_type, source_zip=source_zip)
            else:
                print("LocationRestrictionConfig Not Provided - Using Default")
                lrc = LocationRestrictionConfig()
            if row[5] == 'Yes':
                if row[7] == 'AnyDiscount':
                    pr_type = PriceRestrictionTypes.DiscountAny.value
                else:
                    print(
                        f"Unsupported Price Restriction Type - Type: {row[7]}")
                    continue
            else:
                print("PriceRestrictionConfig Not Provided = Using Default")
                prc = PriceRestrictionConfig()
            if row[8] == 'Yes':
                sources.append(DealifySources.Craigslist.value)
                cl_queries = [(query) for query in row[9].strip().split(',')]
                if row[10] == 'Farm & Garden':
                    categories = ['gra']
                search_titles = True if row[11] == 'Yes' else False
                require_image = True if row[12] == 'Yes' else False
                cl_config = CraigslistConfig(
                    queries=cl_queries, categories=categories, search_titles=search_titles, require_image=require_image)
                sc = SearchConfigIn(location_restriction_config=lrc.json(
                ), price_restriction_config=prc.json(), craigslist_config=cl_config.json())
            else:
                cl_config = None
                sc = SearchConfigIn(location_restriction_config=lrc.json(
                ), price_restriction_config=prc.json())
            ds = DealifySearchIn(search_name=search_name,
                                 sources=json.dumps(sources), search_config=sc.json())
            new_searches.append(ds)
    return new_searches
