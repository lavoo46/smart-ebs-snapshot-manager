import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
snapshots_table = dynamodb.Table(os.environ['SNAPSHOT_TABLE'])
policies_table = dynamodb.Table(os.environ['POLICY_TABLE'])

def handler(event, context):
    path = event.get('path', '')

    if '/list/snapshots' in path:
        return list_snapshots()
    elif '/list/policies' in path:
        return list_policies()
    else:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid path"})}

def list_snapshots():
    response = snapshots_table.scan()
    return {
        "statusCode": 200,
        "body": json.dumps({"items": response.get("Items", [])})
    }

def list_policies():
    response = policies_table.scan()
    return {
        "statusCode": 200,
        "body": json.dumps({"items": response.get("Items", [])})
    }
