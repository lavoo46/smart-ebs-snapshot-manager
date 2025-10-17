import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')
policies_table = dynamodb.Table(os.environ['POLICY_TABLE'])

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        policy_id = body.get('policy_id')
        retention_days = body.get('retentionDays')

        if not policy_id:
            return {"statusCode": 400, "body": json.dumps({"error": "policy_id required"})}

        update_expr = []
        expr_values = {}

        if retention_days is not None:
            update_expr.append("retentionDays = :r")
            expr_values[":r"] = int(retention_days)

        if not update_expr:
            return {"statusCode": 400, "body": json.dumps({"error": "No fields to update"})}

        policies_table.update_item(
            Key={"policy_id": policy_id},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeValues=expr_values
        )

        return {"statusCode": 200, "body": json.dumps({"message": f"Policy {policy_id} updated"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
