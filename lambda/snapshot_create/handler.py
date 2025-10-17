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
    """EBS 스냅샷 자동 생성 + SNS 알림"""
    try:
        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'tag:Backup', 'Values': ['true']}]
        )['Volumes']

        if not volumes:
            msg = "⚠ No EBS volumes found with tag: Backup=true"
            print(msg)
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="⚠ EBS Backup Warning",
                Message=msg
            )
            return {"statusCode": 200, "body": msg}

        created_snapshots = []

        for volume in volumes:
            vol_id = volume['VolumeId']
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            description = f"Automated backup of {vol_id} at {now}"

            snapshot = ec2.create_snapshot(
                VolumeId=vol_id,
                Description=description
            )

            snapshot_id = snapshot['SnapshotId']
            created_snapshots.append(snapshot_id)

            # DynamoDB 기록
            snapshots_table.put_item(
                Item={
                    'snapshotId': snapshot_id,
                    'volumeId': vol_id,
                    'createdAt': now,
                    'region': REGION,
                    'status': 'creating'
                }
            )

            # 태그 추가
            ec2.create_tags(
                Resources=[snapshot_id],
                Tags=[
                    {'Key': 'Name', 'Value': f"Backup-{vol_id}"},
                    {'Key': 'CreatedBy', 'Value': 'SmartEbsSnapshotManager'}
                ]
            )

        # SNS 알림
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
✅ **EBS Backup Notification**

📦 Snapshot(s) Created Successfully!

🆔 Snapshot ID(s): {json.dumps(created_snapshots, ensure_ascii=False)}
🌏 Region: {REGION}
🕒 Time: {time_str}
📊 Status: Completed

- SmartEBS Snapshot Manager
"""

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="✅ EBS Backup Completed",
            Message=message
        )

        print("SNS Notification Sent.")
        return {
            "statusCode": 200,
            "body": f"EBS Snapshot(s) created successfully: {created_snapshots}"
        }

    except Exception as e:
        error_message = f"❌ EBS Backup Failed: {str(e)}"
        print(error_message)
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="❌ EBS Backup Failed",
            Message=error_message
        )
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
