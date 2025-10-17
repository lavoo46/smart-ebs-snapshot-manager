import boto3
import datetime
import os
import json

# AWS 리소스 초기화
ec2 = boto3.client('ec2')
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

# 환경 변수 로드
POLICIES_TABLE = os.environ.get('POLICIES_TABLE')
SNAPSHOTS_TABLE = os.environ.get('SNAPSHOTS_TABLE')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
REGION = os.environ.get('REGION', 'ap-northeast-2')

# DynamoDB 테이블 객체
snapshots_table = dynamodb.Table(SNAPSHOTS_TABLE)


def handler(event, context):
    """EBS 스냅샷 상태 동기화 (EC2 → DynamoDB)"""
    try:
        print("[INFO] Starting snapshot state sync process...")

        # SmartEbsSnapshotManager가 생성한 스냅샷만 조회
        snapshots = ec2.describe_snapshots(
            Filters=[{'Name': 'tag:CreatedBy', 'Values': ['SmartEbsSnapshotManager']}],
            OwnerIds=['self']
        )['Snapshots']

        updated_items = []

        for snap in snapshots:
            snapshot_id = snap['SnapshotId']
            state = snap['State']  # pending / completed / error
            start_time = snap['StartTime'].strftime("%Y-%m-%d %H:%M:%S")

            # DynamoDB에 업데이트
            snapshots_table.update_item(
                Key={'snapshotId': snapshot_id},
                UpdateExpression="SET #st = :s, #upd = :u",
                ExpressionAttributeNames={
                    '#st': 'status',
                    '#upd': 'lastSyncedAt'
                },
                ExpressionAttributeValues={
                    ':s': state,
                    ':u': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            )
            updated_items.append({"snapshotId": snapshot_id, "status": state})

        # SNS 요약 보고
        message = f"""
🔄 **EBS Snapshot State Sync Completed**

📅 Time: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
📦 Updated Snapshots:
{json.dumps(updated_items, indent=2, ensure_ascii=False)}

- SmartEBS Snapshot Manager
"""

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🔄 EBS Snapshot State Synced",
            Message=message
        )

        print("[INFO] Snapshot states synced successfully.")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Snapshot states synced", "updated": updated_items})
        }

    except Exception as e:
        error_message = f"❌ Snapshot Sync Failed: {str(e)}"
        print(error_message)
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="❌ EBS Snapshot Sync Failed",
            Message=error_message
        )
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
