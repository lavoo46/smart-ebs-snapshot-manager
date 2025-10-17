import boto3
import json
import os
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb')
policies_table = dynamodb.Table(os.environ['POLICY_TABLE'])

def handler(event, context):
    try:
        # 요청 파싱
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        # ✅ 모든 키 케이스 대응
        policy_name = (
            body.get("policy_name") or
            body.get("PolicyName") or
            body.get("name") or
            body.get("Name")
        )
        retention_days = int(
            body.get("retention_days") or
            body.get("RetentionDays") or
            body.get("retentionDays") or
            7
        )

        if not policy_name:
            raise ValueError("Missing 'policy_name' in request")

        policy_id = f"policy-{uuid.uuid4().hex[:8]}"
        created_at = datetime.utcnow().isoformat()

        item = {
            "policy_id": policy_id,
            "name": policy_name,
            "retentionDays": retention_days,
            "createdAt": created_at
        }

        policies_table.put_item(Item=item)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({
                "message": "Policy created successfully",
                "policy": item
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({
                "message": f"Error creating policy: {str(e)}"
            })
        }
