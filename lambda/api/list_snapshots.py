import boto3
import os
import json
from decimal import Decimal

# DynamoDB 연결
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SNAPSHOT_TABLE'])

# Decimal → float 변환용
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    try:
        # DynamoDB에서 모든 스냅샷 항목 가져오기
        response = table.scan()
        items = response.get("Items", [])

        # 결과 반환
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"items": items}, cls=DecimalEncoder)
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }
