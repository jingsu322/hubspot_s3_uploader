import os
from pathlib import Path

from dotenv import load_dotenv

#  .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=False)

# -------- AWS --------
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")            # 
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")    # 
AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")

# -------- HubSpot --------
HUBSPOT_TOKEN: str = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")        # 

# -------- Google Service Account --------
GOOGLE_CREDS_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # *.json 

# -------- S3 --------
BUCKET = "dsld-upload"
PREFIXES = {
    "buyer":  "s3-hubspot/buyer-product-profile/",
    "seller": "s3-hubspot/seller-product-profile/",
    "amazon": "s3-hubspot/amazon-product-profile/",
}

DEST_DONE  = "s3-hubspot/done/"
DEST_ERROR = "s3-hubspot/error/"