import boto3
import json
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
policies_table = dynamodb.Table(os.environ['POLICY_TABLE'])

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        name = body.get('name', 'New Policy')
        retention_days = int(body.get('retentionDays', 7))

        policy_id = f"policy-{uuid.uuid4().hex[:8]}"
        created_at = datetime.utcnow().isoformat()

        item = {
            "policy_id": policy_id,
            "name": name,
            "retentionDays": retention_days,
            "createdAt": created_at
        }

        policies_table.put_item(Item=item)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Policy created", "item": item})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
