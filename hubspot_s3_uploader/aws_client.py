import boto3
from .config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
s3 = session.client('s3')


def list_json_keys(prefix):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.lower().endswith('.json'):
                yield key


def read_json(key):
    resp = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return resp['Body'].read()


def move_key(src_key, dest_prefix):
    dest_key = src_key.replace(src_key.split('/')[0] + '/', dest_prefix)
    s3.copy_object(Bucket=S3_BUCKET, CopySource={'Bucket': S3_BUCKET, 'Key': src_key}, Key=dest_key)
    s3.delete_object(Bucket=S3_BUCKET, Key=src_key)