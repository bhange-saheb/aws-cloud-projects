import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2")

try:
    # 1. Fetch details specifically for this AllocationId
    response = ec2.describe_addresses(AllocationIds=[allocation_id])
    addresses = response.get("Addresses", [])

    if addresses:
        eip = addresses[0]

        # 2. Check if the Elastic IP is associated with an instance or network interface
        association_id = eip.get("AssociationId")
        instance_id = eip.get("InstanceId")

        if not association_id and not instance_id:
            # The EIP is unassociated/unused -> Safe to release
            ec2.release_address(AllocationId=allocation_id)
            print(f"Successfully released unused Elastic IP: {allocation_id}")
        else:
            print(
                f"Elastic IP {allocation_id} is currently in use "
                f"(AssociationId: {association_id}, InstanceId: {instance_id}). Keeping it."
            )

except ClientError as e:
    # 3. Gracefully handle if the EIP was already released/deleted
    if e.response["Error"]["Code"] == "InvalidAllocationID.NotFound":
        print(f"Elastic IP allocation {allocation_id} no longer exists.")
    else:
        # Re-raise unexpected errors (e.g., AccessDenied)
        raise e
