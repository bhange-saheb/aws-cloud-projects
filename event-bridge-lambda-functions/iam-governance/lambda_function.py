import json
import os
import boto3
from botocore.exceptions import ClientError

iam = boto3.client("iam")
sns = boto3.client("sns")

BOUNDARY_POLICY_ARN = os.environ["BOUNDARY_POLICY_ARN"]
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


def publish_notification(subject, message):
    if not SNS_TOPIC_ARN:
        return
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],
            Message=message,
        )
    except ClientError as exc:
        print(f"SNS notification failed: {exc}")


def lambda_handler(event, context):
    print(json.dumps(event, default=str))
    detail = event.get("detail", {})
    request_parameters = detail.get("requestParameters", {})
    username = request_parameters.get("userName")

    if not username:
        print("Username not found in event")
        return {"statusCode": 400, "message": "Username not found in event"}

    try:
        iam.put_user_permissions_boundary(
            UserName=username,
            PermissionsBoundary=BOUNDARY_POLICY_ARN,
        )

        message = (
            "AWS IAM GOVERNANCE ALERT\n\n"
            f"User: {username}\n"
            f"Permissions Boundary: {BOUNDARY_POLICY_ARN}\n"
            "Action: Permissions boundary attached automatically."
        )
        print(message)
        publish_notification("IAM permissions boundary applied", message)

        return {
            "statusCode": 200,
            "user": username,
            "boundary": BOUNDARY_POLICY_ARN,
        }

    except ClientError as exc:
        message = f"Failed to attach permissions boundary to {username}: {exc}"
        print(message)
        publish_notification("IAM governance remediation failed", message)
        raise
