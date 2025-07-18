"""Tiny wrapper around boto3 for JSON file iteration."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Iterator

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from . import config

log = logging.getLogger(__name__)

# Create a single boto3 Session → reused across instances
_session = boto3.session.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION,
)
_s3 = _session.resource("s3")


def parse_s3_uri(uri: str) -> tuple[str, str]:
    """Return (bucket, key_prefix) from an S3 URI."""
    if not uri.startswith("s3://"):
        raise ValueError("S3 URI must start with s3://")
    path = uri.replace("s3://", "", 1)
    bucket, _, key = path.partition("/")
    return bucket, key


@dataclass
class S3Object:
    """Represents a JSON object from S3."""
    key: str
    body: list | dict  # JSON‑decoded payload


class S3Client:
    """Iterate `.json` objects under a prefix."""

    def __init__(self, s3_prefix: str):
        self.bucket_name, self.prefix = parse_s3_uri(s3_prefix)
        self.bucket = _s3.Bucket(self.bucket_name)

    # ---------------------------------------------------------------------
    # Iterator of S3Object
    # ---------------------------------------------------------------------
    def iter_objects(self) -> Iterator[S3Object]:
        for obj in self.bucket.objects.filter(Prefix=self.prefix):
            if not obj.key.endswith(".json"):
                continue
            try:
                body_bytes = obj.get()["Body"].read()
                yield S3Object(key=obj.key, body=json.loads(body_bytes))
            except (ClientError, NoCredentialsError, json.JSONDecodeError) as exc:
                log.error("Unable to fetch/parse %s – %s", obj.key, exc)