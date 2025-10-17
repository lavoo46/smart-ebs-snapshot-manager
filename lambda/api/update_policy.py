import boto3
import json
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
policies_table = dynamodb.Table(os.environ['POLICY_TABLE'])

def handler(event, context):
    try:
        # 요청 파싱
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        policy_id = body.get("policy_id") or body.get("PolicyId")
        if not policy_id:
            raise ValueError("Missing 'policy_id' in request")

        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        # name 업데이트 (예약어 처리)
        if "name" in body and body["name"]:
            update_expr.append("#n = :n")
            expr_attr_names["#n"] = "name"
            expr_attr_values[":n"] = body["name"]

        # retentionDays 업데이트
        if "retentionDays" in body and body["retentionDays"]:
            update_expr.append("retentionDays = :r")
            expr_attr_values[":r"] = int(body["retentionDays"])

        if not update_expr:
            raise ValueError("No fields to update")

        update_expr.append("updatedAt = :u")
        expr_attr_values[":u"] = datetime.utcnow().isoformat()

        # DynamoDB 업데이트
        params = {
            "Key": {"policy_id": policy_id},
            "UpdateExpression": "SET " + ", ".join(update_expr),
            "ExpressionAttributeValues": expr_attr_values
        }

        if expr_attr_names:
            params["ExpressionAttributeNames"] = expr_attr_names

        policies_table.update_item(**params)

        # ✅ 성공 응답 (CORS 포함)
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
            },
            "body": json.dumps({
                "message": f"Policy {policy_id} updated successfully"
            })
        }

    except Exception as e:
        # ✅ 에러 응답에도 CORS 포함
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
            },
            "body": json.dumps({
                "message": f"Error updating policy: {str(e)}"
            })
        }
