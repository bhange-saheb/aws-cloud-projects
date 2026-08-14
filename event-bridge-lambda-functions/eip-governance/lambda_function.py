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


def extract_allocation_id(event):
    detail = event.get("detail", {})
    req = detail.get("requestParameters", {})
    resp = detail.get("responseElements", {})
    return first_value(
        detail.get("allocationId"),
        detail.get("resourceId"),
        req.get("allocationId"),
        resp.get("allocationId"),
    )


def safe_schedule_name(resource_id):
    raw = f"eip-check-{resource_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    return re.sub(r"[^A-Za-z0-9_.-]", "-", raw)[:64]


def schedule_recheck(allocation_id, context):
    run_at = datetime.now(timezone.utc) + timedelta(minutes=CLEANUP_DELAY_MINUTES)
    name = safe_schedule_name(allocation_id)
    target_arn = SCHEDULER_TARGET_LAMBDA_ARN or context.invoked_function_arn

    scheduler.create_schedule(
        Name=name,
        ScheduleExpression=f"at({run_at.strftime('%Y-%m-%dT%H:%M:%S')})",
        ScheduleExpressionTimezone="UTC",
        FlexibleTimeWindow={"Mode": "OFF"},
        Target={
            "Arn": target_arn,
            "RoleArn": SCHEDULER_ROLE_ARN,
            "Input": json.dumps({
                "action": "recheck",
                "resource_type": "eip",
                "allocation_id": allocation_id,
            }),
        },
        ActionAfterCompletion="DELETE",
    )
    return name


def get_address(allocation_id):
    response = ec2.describe_addresses(AllocationIds=[allocation_id])
    addresses = response.get("Addresses", [])
    return addresses[0] if addresses else None


def lambda_handler(event, context):
    print(json.dumps(event, default=str))

    if event.get("action") == "recheck":
        return check_and_release_address(event["allocation_id"])

    allocation_id = extract_allocation_id(event)
    if not allocation_id:
        raise ValueError("Could not find Elastic IP allocation ID in EventBridge event")

    address = get_address(allocation_id)
    if address is None:
        return {"status": "not_found", "allocation_id": allocation_id}

    publish_notification(
        "Elastic IP allocated",
        f"Allocation {allocation_id} detected. Checking association after "
        f"{CLEANUP_DELAY_MINUTES} minutes.",
    )

    if DRY_RUN:
        print(f"[DRY RUN] Would schedule recheck for {allocation_id}")
        return {"status": "dry_run", "allocation_id": allocation_id}

    name = schedule_recheck(allocation_id, context)
    return {"status": "scheduled", "allocation_id": allocation_id, "schedule_name": name}


def check_and_release_address(allocation_id):
    try:
        address = get_address(allocation_id)
        if address is None:
            return {"status": "not_found", "allocation_id": allocation_id}

        associated = bool(
            address.get("AssociationId")
            or address.get("InstanceId")
            or address.get("NetworkInterfaceId")
        )

        if associated:
            publish_notification(
                "Elastic IP retained",
                f"Allocation {allocation_id} is associated/in use. Action: KEEP",
            )
            return {"status": "kept", "allocation_id": allocation_id}

        if DRY_RUN:
            publish_notification(
                "Elastic IP dry-run cleanup",
                f"[DRY RUN] Would release unused Elastic IP {allocation_id}",
            )
            return {"status": "dry_run_would_release", "allocation_id": allocation_id}

        ec2.release_address(AllocationId=allocation_id)
        publish_notification(
            "Elastic IP released",
            f"Allocation {allocation_id} was unassociated and has been released.",
        )
        return {"status": "released", "allocation_id": allocation_id}

    except ClientError as exc:
        publish_notification(
            "Elastic IP governance remediation failed",
            f"Allocation {allocation_id}\nError: {exc}",
        )
        raise
