import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
snapshots_table = dynamodb.Table(os.environ['SNAPSHOT_TABLE'])

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        volume_id = body.get('volumeId', 'unknown')

        snapshot_id = f"snap-{uuid.uuid4().hex[:10]}"
        created_at = datetime.utcnow().isoformat()

        item = {
            "snapshotId": snapshot_id,
            "volumeId": volume_id,
            "status": "creating",
            "createdAt": created_at,
            "region": os.environ.get("AWS_REGION", "ap-northeast-2")
        }

        snapshots_table.put_item(Item=item)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Snapshot created", "item": item})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
