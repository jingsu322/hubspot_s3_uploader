import json
import logging
from pathlib import Path
from typing import Any

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from .config import GOOGLE_CREDS_JSON

logger = logging.getLogger(__name__)

_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

def _load_credentials() -> ServiceAccountCredentials:
    if GOOGLE_CREDS_JSON.endswith(".json") and Path(GOOGLE_CREDS_JSON).exists():
        cred_path = GOOGLE_CREDS_JSON
    else:
        cred_path = "/tmp/_svc_account.json"
        Path(cred_path).write_text(GOOGLE_CREDS_JSON, encoding="utf-8")

    return ServiceAccountCredentials.from_json_keyfile_name(cred_path, _SCOPE)

def get_client() -> gspread.Client:
    try:
        gc = gspread.authorize(_load_credentials())
        return gc
    except Exception as e:  # noqa: BLE001
        logger.exception("Failed to create gspread client")
        raise

def open_ws(client: gspread.Client, spreadsheet_key: str, sheet_name: str) -> Any:
    sh = client.open_by_key(spreadsheet_key)
    return sh.worksheet(sheet_name)