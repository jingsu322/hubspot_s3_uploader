import logging

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from .config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

logger = logging.getLogger(__name__)

def get_s3_client():
    try:
        session = boto3.Session(
            aws_access_key_id     = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            region_name           = AWS_REGION,
        )
        return session.client("s3", config=Config(retries={"max_attempts": 10, "mode": "adaptive"}))
    except (BotoCoreError, ClientError) as e:
        logger.exception("Failed to create S3 client")
        raise