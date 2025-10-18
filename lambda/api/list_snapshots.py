import boto3
import os
import json
from decimal import Decimal
from botocore.exceptions import ClientError

# EC2 및 DynamoDB 연결
ec2 = boto3.client('ec2')
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
        # DynamoDB의 기존 스냅샷 목록 불러오기
        response = table.scan()
        items = response.get("Items", [])

        # EC2에서 실제 스냅샷 상태를 조회
        ec2_response = ec2.describe_snapshots(OwnerIds=["self"])
        ec2_snapshots = ec2_response.get("Snapshots", [])

        # EC2 스냅샷 상태를 DynamoDB 데이터에 반영
        updated_items = []
        for ec2_snap in ec2_snapshots:
            snap_id = ec2_snap["SnapshotId"]
            vol_id = ec2_snap.get("VolumeId", "-")
            state = ec2_snap.get("State", "-")
            start_time = str(ec2_snap.get("StartTime"))
            region = os.environ.get("AWS_REGION", "ap-northeast-2")

            # DynamoDB의 동일한 스냅샷 항목 찾기
            match = next((item for item in items if item.get("snapshotId") == snap_id), None)

            # 업데이트
            if match:
                if match.get("status") != state:
                    table.update_item(
                        Key={"snapshotId": snap_id},
                        UpdateExpression="SET #s = :s",
                        ExpressionAttributeNames={"#s": "status"},
                        ExpressionAttributeValues={":s": state}
                    )
                match["status"] = state
            else:
                # DynamoDB에 없던 새 스냅샷이면 추가
                table.put_item(Item={
                    "snapshotId": snap_id,
                    "volumeId": vol_id,
                    "status": state,
                    "createdAt": start_time,
                    "region": region
                })
                match = {
                    "snapshotId": snap_id,
                    "volumeId": vol_id,
                    "status": state,
                    "createdAt": start_time,
                    "region": region
                }

            updated_items.append(match)

        # 결과 반환 (EC2 기준 최신 데이터)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"items": updated_items}, cls=DecimalEncoder)
        }

    except ClientError as e:
        print("AWS Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"AWS Error: {str(e)}"})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }
