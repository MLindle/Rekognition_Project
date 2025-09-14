import os, json, urllib.parse
from datetime import datetime
import boto3
import logging
from decimal import Decimal

log = logging.getLogger()
log.setLevel(logging.INFO)

rekognition = boto3.client('rekognition')
dynamodb   = boto3.resource('dynamodb')

TABLE_BETA = os.environ.get('DYNAMODB_TABLE_BETA')
TABLE_PROD = os.environ.get('DYNAMODB_TABLE_PROD')

INPUT_ROOT = "rekognition-input/"

def table_for_key(key: str) -> tuple[str, str] | tuple[None, None]:
    if not key.startswith(INPUT_ROOT):
        return None, None
    rest = key[len(INPUT_ROOT):]
    env  = rest.split('/', 1)[0] or ""
    if env == "beta":
        return "beta", TABLE_BETA
    if env == "prod":
        return "prod", TABLE_PROD
    return None, None

def lambda_handler(event, context):
    for rec in event.get('Records', []):
        bucket = rec['s3']['bucket']['name']
        rawkey = rec['s3']['object']['key']
        key    = urllib.parse.unquote_plus(rawkey)
        event_time = rec.get('eventTime') or datetime.utcnow().isoformat() + "Z"

        branch, table_name = table_for_key(key)
        if not branch or not table_name:
            log.info({"skip":"unknown-branch", "key": key})
            continue

        try:
            response = rekognition.detect_labels(
                Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                MaxLabels=10
            )
            labels = [
                {"Name": l["Name"], "Confidence": Decimal(str(l["Confidence"]))}
                for l in response.get("Labels", [])
            ]

            item = {
                'timestamp': event_time,
                'filename':  key,
                'branch':    branch,
                'bucket':    bucket,
                'requestId': context.aws_request_id,
                'labels':    labels
            }
            dynamodb.Table(table_name).put_item(Item=item)
            log.info({"wrote_to": table_name, "item_pk": item["timestamp"]})
        except Exception as e:
            log.error({"ddb_or_rekognition_failed": str(e), "table": table_name, "key": key})
            raise

    return {"statusCode": 200, "body": "Success"}
