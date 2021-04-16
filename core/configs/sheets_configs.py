from core.configs.config import DEV_MODE

SPREADSHEET_ID = '12G-EDF2dxhcNKkUHTExqJFJmwQTTs_My1h79GPURR9g'

NEW_SEARCH_HEADER_RANGE = 'NewSearches!A1:L1'

NEW_SEARCH_DATA_RANGE = 'NewSearches!A2:L'

API_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


if DEV_MODE:
    SERVICE_ACCOUNT_CREDS_FILE = 'sheets.creds.json'
else:
    SERVICE_ACCOUNT_CREDS_FILE = './sheets.creds.json'

BOOLEAN_STRING_TRUE_VALUE = 'Yes'

BOOLEAN_STRING_FALSE_VALUE = 'No'

MULTIPLE_CELL_VALUE_SEPARATION_CHAR = ','
