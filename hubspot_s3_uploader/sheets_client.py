import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dateutil import parser
from .config import GOOGLE_SERVICE_ACCOUNT_JSON, SHEET_KEYS

# Initialize gspread
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SERVICE_ACCOUNT_JSON, scope)
gc = gspread.authorize(creds)

prod_ws = gc.open_by_key(SHEET_KEYS['product_profile']).worksheet('product_profile')
buyer_ws = gc.open_by_key(SHEET_KEYS['buyer_lookup']).worksheet('lookup_update')
seller_ws = gc.open_by_key(SHEET_KEYS['seller_lookup']).worksheet('lookup_update')


def build_lookup_dict(ws, rec_col='record_id', date_col='Date Scraped'):
    values = ws.get_all_values()
    header = values[0]
    rid_idx = header.index(rec_col)
    ds_idx = header.index(date_col)
    mapping = {}
    for row in values[1:]:
        rid = row[rid_idx].strip()
        date_raw = row[ds_idx].strip()
        if rid and date_raw:
            try:
                mapping[rid] = datetime.strptime(date_raw, '%m-%d-%Y').strftime('%Y-%m-%d')
            except Exception:
                mapping[rid] = parser.parse(date_raw).date().isoformat()
    return mapping