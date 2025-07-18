"""High‑level orchestrator: discover rows ➜ extract ➜ update HubSpot ➜ mark Sheet."""
from __future__ import annotations

import concurrent.futures as futures
import logging
from pathlib import PurePosixPath

from . import config, logger  # noqa: F401 – initialises logging globally
from .hubspot_client import update_company_properties
from .processors.base import Processor
from .s3_client import S3Client
from .sheets_client import iter_rows, SheetRow
from .sheet_sync import sync_sheet

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Per‑row worker
# ---------------------------------------------------------------------------

def _process_row(row: SheetRow) -> None:
    if row.status.lower() == "done":
        return  # skip already processed

    # 1. Choose extractor by source
    try:
        processor = Processor.for_source(row.source)
    except ValueError:
        row.mark("unsupported source"); return

    # 2. Download JSON for this record
    bucket_prefix = f"s3://{row.target}/{row.source}/"
    client = S3Client(bucket_prefix)
    expected_key_end = f"{row.record_id}.json"
    obj = next((o for o in client.iter_objects() if o.key.endswith(expected_key_end)), None)
    if obj is None:
        row.mark("file not found"); return

    # 3. Extract → HubSpot
    properties = processor.property_map(obj.body)
    try:
        update_company_properties(row.record_id, properties)
        row.mark("done")
    except Exception as exc:  # noqa: BLE001
        log.exception("HubSpot update failed for %s: %s", row.record_id, exc)
        row.mark("error")


# ---------------------------------------------------------------------------
# 2. Entry‑point
# ---------------------------------------------------------------------------

def run() -> None:
    # Step 1 – ensure Sheet has rows for every S3 file
    sync_sheet()

    # Step 2 – iterate & process rows concurrently
    rows = iter_rows()
    if not rows:
        log.info("No rows in Sheet – nothing to do")
        return

    with futures.ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as pool:
        pool.map(_process_row, rows)


# Allow `python -m hubspot_s3_uploader` to run pipeline
if __name__ == "__main__":
    run()