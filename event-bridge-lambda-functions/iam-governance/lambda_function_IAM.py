import boto3
import json
import os

iam = boto3.client("iam")

BOUNDARY_POLICY_ARN = os.environ["BOUNDARY_POLICY_ARN"]


def lambda_handler(event, context):

    print(json.dumps(event))

    detail = event.get("detail", {})

    request_parameters = detail.get("requestParameters", {})

    username = request_parameters.get("userName")

    if not username:
        print("Username not found")
        return

    print(f"New IAM user detected: {username}")

    iam.put_user_permissions_boundary(
        UserName=username, PermissionsBoundary=BOUNDARY_POLICY_ARN
    )

    print(f"Permissions boundary attached to {username}")
