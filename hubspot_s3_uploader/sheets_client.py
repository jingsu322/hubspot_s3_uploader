"""Google Sheets adapter using gspread."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import gspread
from google.oauth2.service_account import Credentials

from . import config

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. Authorise – Service Account JSON file must be present locally or on disk
# ---------------------------------------------------------------------------
_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
_creds = Credentials.from_service_account_file(
    Path(config.GOOGLE_SERVICE_ACCOUNT_FILE), scopes=_SCOPES
)
_client = gspread.authorize(_creds)
_sheet = _client.open_by_key(config.GOOGLE_SHEET_ID).worksheet(config.GOOGLE_SHEET_NAME)


# ---------------------------------------------------------------------------
# 2. Row wrapper & helpers
# ---------------------------------------------------------------------------
class SheetRow:
    """Represents four columns: source | target | record_id | status."""

    def __init__(self, idx: int, row: List[str]):
        self.idx = idx  # 1‑based index in Sheet
        # Ensure list is at least length‑4
        padded = row + ([""] * (4 - len(row)))
        self.source, self.target, self.record_id, self.status = padded[:4]

    # quick mutator ↓
    def mark(self, new_status: str):
        _sheet.update_cell(self.idx, 4, new_status)


def iter_rows() -> List[SheetRow]:
    """Return SheetRow objects **after header row** (assume headers on row‑1)."""
    raw = _sheet.get_all_values()[1:]  # skip header row (row‑0)
    return [SheetRow(idx=i + 2, row=r) for i, r in enumerate(raw)]


# ---------------------------------------------------------------------------
# 3. Append‑if‑absent utility – used by sheet_sync
# ---------------------------------------------------------------------------

def append_row_if_absent(source: str, target: str, record_id: str):
    existing_ids = _sheet.col_values(3)  # record_id column
    if record_id in existing_ids:
        return
    _sheet.append_row([source, target, record_id, "pending"], value_input_option="USER_ENTERED")
    log.info("Sheet row added – %s | %s | %s", source, target, record_id)