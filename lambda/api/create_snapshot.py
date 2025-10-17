import boto3
import json
import os
from datetime import datetime

# EC2 / DynamoDB 클라이언트 초기화
ec2 = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')
snapshots_table = dynamodb.Table(os.environ['SNAPSHOT_TABLE'])

def lambda_handler(event, context):
    try:
        # -------------------------------
        # ① 요청 Body 파싱
        # -------------------------------
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        # 다양한 형태의 키 지원
        volume_id = body.get("volume_id") or body.get("VolumeId") or body.get("volumeId")
        if not volume_id:
            raise ValueError("Missing 'volume_id' in request")

        # -------------------------------
        # ② EC2 스냅샷 생성
        # -------------------------------
        response = ec2.create_snapshot(
            VolumeId=volume_id,
            Description=f"Snapshot created for {volume_id}"
        )

        snapshot_id = response["SnapshotId"]
        created_at = datetime.utcnow().isoformat()

        # -------------------------------
        # ③ DynamoDB에 기록
        # -------------------------------
        item = {
            "snapshotId": snapshot_id,
            "volumeId": volume_id,
            "status": "creating",
            "createdAt": created_at,
            "region": os.environ.get("AWS_REGION", "ap-northeast-2")
        }
        snapshots_table.put_item(Item=item)

        # -------------------------------
        # ④ 정상 응답 (CORS 헤더 포함)
        # -------------------------------
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({
                "message": "Snapshot created successfully",
                "snapshotId": snapshot_id,
                "volumeId": volume_id
            })
        }

    except Exception as e:
        # -------------------------------
        # ⑤ 오류 응답 (CORS 헤더 포함)
        # -------------------------------
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({
                "message": f"Error creating snapshot: {str(e)}"
            })
        }
