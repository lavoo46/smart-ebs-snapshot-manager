import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')
snapshots_table = dynamodb.Table(os.environ['SNAPSHOT_TABLE'])

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        snapshot_id = body.get('snapshotId')

        if not snapshot_id:
            return {"statusCode": 400, "body": json.dumps({"error": "snapshotId required"})}

        snapshots_table.delete_item(Key={"snapshotId": snapshot_id})
        return {"statusCode": 200, "body": json.dumps({"message": f"Snapshot {snapshot_id} deleted"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
