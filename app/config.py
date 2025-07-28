import os
from pathlib import Path

from dotenv import load_dotenv

# 自动读取仓库根目录下 .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=False)

# -------- AWS --------
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")            # 必填
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")    # 必填
AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")

# -------- HubSpot --------
HUBSPOT_TOKEN: str = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")        # 必填

# -------- Google Service Account --------
GOOGLE_CREDS_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # *.json 路径或 JSON 字符串

# -------- S3 --------
BUCKET = "dsld-upload"
PREFIXES = {
    "buyer":  "s3-hubspot/buyer-product-profile/",
    "seller": "s3-hubspot/seller-product-profile/",
    "amazon": "s3-hubspot/amazon-product-profile/",
}

DEST_DONE  = "s3-hubspot/done/"
DEST_ERROR = "s3-hubspot/error/"
