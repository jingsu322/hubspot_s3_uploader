# HubSpot S3 Uploader

This package implements an ETL pipeline to:
1. Read raw JSON files from S3
2. Extract product ingredient profiles
3. Lookup scrape dates via Google Sheets
4. Update HubSpot company records
5. Move processed files in S3

## Installation
```
pip install .
```

## Configuration
Set environment variables or edit `hubspot_s3_uploader/config.py`:
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
- GOOGLE_SERVICE_ACCOUNT_JSON (path)
- HUBSPOT_PRIVATE_APP_TOKEN
- S3_BUCKET, PREFIXES
- SHEET_KEYS

## Usage
Install and run:
```
run-profile-etl
```

Or via script:
```
bash scripts/run_etl.sh
```