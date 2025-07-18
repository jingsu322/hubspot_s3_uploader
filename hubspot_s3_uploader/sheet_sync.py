"""Scan configured S3 prefixes and ensure each file exists as a row in the Sheet."""
from __future__ import annotations

import logging
import re
from pathlib import PurePosixPath

from . import config
from .s3_client import S3Client
from .sheets_client import append_row_if_absent

log = logging.getLogger(__name__)

# Regex to capture numeric record_id at end of filename
_RECORD_ID_RE = re.compile(r"(?P<id>\d+)\.json$")


def sync_sheet() -> None:
    """Discover *.json files and populate missing rows (idempotent)."""
    if not config.S3_PREFIXES:
        log.warning("S3_PREFIXES empty – discovery skipped")
        return

    for prefix in config.S3_PREFIXES:
        log.info("Scanning %s", prefix)
        for obj in S3Client(prefix).iter_objects():
            m = _RECORD_ID_RE.search(obj.key)
            if not m:
                continue  # skip non‑matching files
            record_id = m.group("id")

            # Expect key layout: {target}/{source}/{filename}.json
            path_parts = PurePosixPath(obj.key).parts
            if len(path_parts) < 3:
                log.warning("Unusual key layout: %s", obj.key)
                continue
            target, source = path_parts[0], path_parts[1]
            append_row_if_absent(source, target, record_id)