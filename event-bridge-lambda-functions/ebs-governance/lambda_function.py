import json
import os
import re
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2")
sns = boto3.client("sns")
scheduler = boto3.client("scheduler")

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
SCHEDULER_ROLE_ARN = os.environ["SCHEDULER_ROLE_ARN"]
CLEANUP_DELAY_MINUTES = int(os.environ.get("CLEANUP_DELAY_MINUTES", "5"))
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"
SCHEDULER_TARGET_LAMBDA_ARN = os.environ.get("SCHEDULER_TARGET_LAMBDA_ARN", "")


def publish_notification(subject, message):
    if not SNS_TOPIC_ARN:
        return
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject[:100], Message=message)
    except ClientError as exc:
        print(f"SNS notification failed: {exc}")


def first_value(*values):
    return next((value for value in values if value), None)


def extract_volume_id(event):
    # 1. Check resources first
    resources = event.get("resources", [])

    for resource in resources:
        if isinstance(resource, str) and ":volume/" in resource:
            return resource.split(":volume/", 1)[1]

    # 2. Check detail
    detail = event.get("detail", {})

    # Handle detail being a JSON string
    if isinstance(detail, str):
        try:
            detail = json.loads(detail)
        except json.JSONDecodeError:
            return None

    if not isinstance(detail, dict):
        return None

    req = detail.get("requestParameters", {})
    resp = detail.get("responseElements", {})

    if not isinstance(req, dict):
        req = {}

    if not isinstance(resp, dict):
        resp = {}

    return first_value(
        detail.get("volumeId"),
        detail.get("resourceId"),
        req.get("volumeId"),
        resp.get("volumeId"),
    )


def safe_schedule_name(resource_id):
    raw = f"ebs-check-{resource_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    return re.sub(r"[^A-Za-z0-9_.-]", "-", raw)[:64]


def schedule_recheck(volume_id, context):
    run_at = datetime.now(timezone.utc) + timedelta(minutes=CLEANUP_DELAY_MINUTES)
    name = safe_schedule_name(volume_id)
    target_arn = SCHEDULER_TARGET_LAMBDA_ARN or context.invoked_function_arn

    scheduler.create_schedule(
        Name=name,
        ScheduleExpression=f"at({run_at.strftime('%Y-%m-%dT%H:%M:%S')})",
        ScheduleExpressionTimezone="UTC",
        FlexibleTimeWindow={"Mode": "OFF"},
        Target={
            "Arn": target_arn,
            "RoleArn": SCHEDULER_ROLE_ARN,
            "Input": json.dumps(
                {
                    "action": "recheck",
                    "resource_type": "ebs",
                    "volume_id": volume_id,
                }
            ),
        },
        ActionAfterCompletion="DELETE",
    )
    return name


def get_volume(volume_id):
    response = ec2.describe_volumes(VolumeIds=[volume_id])
    volumes = response.get("Volumes", [])
    return volumes[0] if volumes else None


def lambda_handler(event, context):
    print(json.dumps(event, default=str))

    if event.get("action") == "recheck":
        return check_and_cleanup_volume(event["volume_id"])

    volume_id = extract_volume_id(event)
    if not volume_id:
        raise ValueError("Could not find EBS volume ID in EventBridge event")

    volume = get_volume(volume_id)
    if volume is None:
        return {"status": "not_found", "volume_id": volume_id}

    tags = {tag["Key"]: tag["Value"] for tag in volume.get("Tags", [])}
    if tags.get("CleanupExempt", "").lower() == "true":
        publish_notification(
            "EBS cleanup exemption",
            f"Volume {volume_id} has CleanupExempt=true. Action: KEEP",
        )
        return {"status": "exempt", "volume_id": volume_id}

    publish_notification(
        "EBS volume detected",
        f"Volume {volume_id} detected. Checking again after "
        f"{CLEANUP_DELAY_MINUTES} minutes.",
    )

    if DRY_RUN:
        print(f"[DRY RUN] Would schedule recheck for {volume_id}")
        return {"status": "dry_run", "volume_id": volume_id}

    name = schedule_recheck(volume_id, context)
    return {"status": "scheduled", "volume_id": volume_id, "schedule_name": name}


def check_and_cleanup_volume(volume_id):
    try:
        volume = get_volume(volume_id)
        if volume is None:
            return {"status": "not_found", "volume_id": volume_id}

        tags = {tag["Key"]: tag["Value"] for tag in volume.get("Tags", [])}
        if tags.get("CleanupExempt", "").lower() == "true":
            return {"status": "exempt", "volume_id": volume_id}

        state = volume["State"]
        if state == "available":
            if DRY_RUN:
                publish_notification(
                    "EBS dry-run cleanup",
                    f"[DRY RUN] Would delete unattached volume {volume_id}",
                )
                return {"status": "dry_run_would_delete", "volume_id": volume_id}

            ec2.delete_volume(VolumeId=volume_id)
            publish_notification(
                "EBS volume deleted",
                f"Volume {volume_id} was available and has been deleted.",
            )
            return {"status": "deleted", "volume_id": volume_id}

        if state == "in-use":
            publish_notification(
                "EBS volume retained",
                f"Volume {volume_id} is in-use. Action: KEEP",
            )
            return {"status": "kept", "volume_id": volume_id}

        return {"status": "unknown_state", "volume_id": volume_id, "state": state}

    except ClientError as exc:
        publish_notification(
            "EBS governance remediation failed",
            f"Volume {volume_id}\nError: {exc}",
        )
        raise
