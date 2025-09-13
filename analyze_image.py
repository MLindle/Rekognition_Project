import os
from datetime import datetime
import boto3

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

TABLE_BETA = os.environ.get('DYNAMODB_TABLE_BETA')
TABLE_PROD = os.environ.get('DYNAMODB_TABLE_PROD')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        timestamp = record['eventTime']

        # Determine branch and table
        if key.startswith('beta/'):
            branch = 'beta'
            table_name = TABLE_BETA
        elif key.startswith('prod/'):
            branch = 'prod'
            table_name = TABLE_PROD
        else:
            print(f"Unknown branch for key: {key}")
            continue

        # Call Rekognition
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10
        )
        labels = [
            {'Name': label['Name'], 'Confidence': label['Confidence']}
            for label in response['Labels']
        ]

        # Write to DynamoDB
        table = dynamodb.Table(table_name)
        item = {
            'filename': key,
            'labels': labels,
            'timestamp': timestamp,
            'branch': branch
        }
        table.put_item(Item=item)
        print(f"Processed {key} and wrote to {table_name}")

    return {'statusCode': 200, 'body': 'Success'}