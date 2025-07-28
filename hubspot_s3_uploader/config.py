import os

# AWS
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
S3_BUCKET = os.environ.get('S3_BUCKET', 'dsld-upload')
PREFIXES = {
    'buyer': 's3-hubspot/buyer-product-profile/',
    'seller': 's3-hubspot/seller-product-profile/',
    'amazon': 's3-hubspot/amazon-product-profile/',
}

# HubSpot
HUBSPOT_TOKEN = os.environ.get('HUBSPOT_PRIVATE_APP_TOKEN')

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
SHEET_KEYS = {
    'product_profile': '1OQgyb9_tjSs3rfjXW_9sOF7ye6chFGlEuAszTjroc78',
    'buyer_lookup': '1AP1O9mB25OIzUACKn8vc6rpKY0Mk_s_5pH-1Zc4bdOM',
    'seller_lookup': '12rAhXZ9ao5dsSGYYH-zTn_3xTs1b3KA-4g1EBubrF6Q',
}

# Rate limiting
HUBSPOT_DELAY = float(os.environ.get('HUBSPOT_DELAY', 1.0))