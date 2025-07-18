"""Centralised runtime configuration (12‑factor‑style)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1. Load environment – .env is optional (for local development only)
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

# ---------------------------------------------------------------------------
# 2. AWS credentials & defaults
# ---------------------------------------------------------------------------
AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

# ---------------------------------------------------------------------------
# 3. Google Service Account & Sheet details
# ---------------------------------------------------------------------------
GOOGLE_SERVICE_ACCOUNT_FILE: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_SHEET_ID: str | None = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "product_profile")  # tab name

# ---------------------------------------------------------------------------
# 4. HubSpot Private App token
# ---------------------------------------------------------------------------
HUBSPOT_PRIVATE_APP_TOKEN: str | None = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")

# ---------------------------------------------------------------------------
# 5. Job runtime tuneables
# ---------------------------------------------------------------------------
MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "8"))
BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "50"))

# ---------------------------------------------------------------------------
# 6. S3 discovery prefixes (comma‑sep list) – each prefix should include trailing slash
#    Example: "s3://bucket/buyer-product-profile/,s3://bucket/seller-product-profile/"
# ---------------------------------------------------------------------------
S3_PREFIXES: List[str] = [p.strip() for p in os.getenv("S3_PREFIXES", "").split(",") if p.strip()]

# ---------------------------------------------------------------------------
# 7. Validate required settings early – fail‑fast in CI / container startup
# ---------------------------------------------------------------------------
_required = {
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "HUBSPOT_PRIVATE_APP_TOKEN": HUBSPOT_PRIVATE_APP_TOKEN,
    "GOOGLE_SERVICE_ACCOUNT_FILE": GOOGLE_SERVICE_ACCOUNT_FILE,
    "GOOGLE_SHEET_ID": GOOGLE_SHEET_ID,
}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(_missing)}")