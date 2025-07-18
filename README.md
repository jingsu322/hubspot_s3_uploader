# HubSpot S3 → Top‑Ingredients Updater

Populate & maintain the **top_ingredients** property on HubSpot companies by mining JSON files in S3.  A Google Sheet controls which records are processed and tracks status.

```bash
# install
poetry install
cp .env.example .env  # then fill secrets

# one‑time: discover S3 → Sheet rows
poetry run python - <<'PY'
from hubspot_s3_uploader.sheet_sync import sync_sheet; sync_sheet()
PY

# normal run (discovery + processing)
poetry run python -m hubspot_s3_uploader