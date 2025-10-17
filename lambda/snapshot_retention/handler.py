import boto3
import datetime
import os
import json

ec2 = boto3.client('ec2')
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

POLICIES_TABLE = os.environ.get('POLICIES_TABLE')
SNAPSHOTS_TABLE = os.environ.get('SNAPSHOTS_TABLE')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
REGION = os.environ.get('REGION', 'ap-northeast-2')

snapshots_table = dynamodb.Table(SNAPSHOTS_TABLE)

def handler(event, context):
    """오래된 스냅샷 자동 삭제 (Retention Lambda)"""
    try:
        retention_days = 7
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=retention_days)

        snapshots = ec2.describe_snapshots(
            Filters=[{'Name': 'tag:CreatedBy', 'Values': ['SmartEbsSnapshotManager']}],
            OwnerIds=['self']
        )['Snapshots']

        deleted_snapshots = []

        for snap in snapshots:
            start_time = snap['StartTime'].replace(tzinfo=None)
            if start_time < cutoff_date:
                snapshot_id = snap['SnapshotId']
                try:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots.append(snapshot_id)

                    snapshots_table.update_item(
                        Key={'snapshotId': snapshot_id},
                        UpdateExpression="SET #st = :s",
                        ExpressionAttributeNames={'#st': 'status'},
                        ExpressionAttributeValues={':s': 'deleted'}
                    )
                except Exception as inner_e:
                    print(f"⚠ 스냅샷 {snapshot_id} 삭제 실패: {inner_e}")

        message = f"""
🧹 **EBS Snapshot Retention Report**

🗓️ Retention Days: {retention_days}
🕒 Checked at: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
🧾 Deleted Snapshots: {json.dumps(deleted_snapshots, ensure_ascii=False)}

- SmartEBS Snapshot Manager
"""

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🧹 EBS Snapshot Retention Completed",
            Message=message
        )

        print(f"[INFO] Deleted snapshots: {deleted_snapshots}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Retention completed",
                "deleted_snapshots": deleted_snapshots
            })
        }

    except Exception as e:
        error_message = f"❌ Retention Lambda Error: {str(e)}"
        print(error_message)
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="❌ EBS Snapshot Retention Failed",
            Message=error_message
        )
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
