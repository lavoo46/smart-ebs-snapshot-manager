import boto3
import json
import os

ec2 = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')
snapshots_table = dynamodb.Table(os.environ['SNAPSHOT_TABLE'])

def handler(event, context):
    try:
        # ✅ 요청 바디 파싱
        if "body" in event and event["body"]:
            body = json.loads(event["body"])
        else:
            body = event

        # ✅ 다양한 키 이름 지원
        snapshot_id = body.get("snapshot_id") or body.get("SnapshotId") or body.get("snapshotId")
        if not snapshot_id:
            raise ValueError("Missing 'snapshot_id' in request")

        # ✅ 실제 EC2 스냅샷 삭제
        ec2.delete_snapshot(SnapshotId=snapshot_id)

        # ✅ DynamoDB에서도 삭제
        snapshots_table.delete_item(Key={"snapshotId": snapshot_id})

        # ✅ 성공 응답 (CORS 완전 반영)
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE"
            },
            "body": json.dumps({
                "message": f"Snapshot {snapshot_id} deleted successfully"
            })
        }

    except Exception as e:
        # ✅ 실패 응답 (CORS 포함)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE"
            },
            "body": json.dumps({
                "message": f"Error deleting snapshot: {str(e)}"
            })
        }
