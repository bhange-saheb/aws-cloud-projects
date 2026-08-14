response = ec2.describe_volumes(
    VolumeIds=[volume_id]
)

volume = response["Volumes"][0]

if volume["State"] == "available":

    ec2.delete_volume(
        VolumeId=volume_id
    )

elif volume["State"] == "in-use":

    print("Volume is attached. Keeping it.")