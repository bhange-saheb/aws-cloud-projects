# Amazon S3 Access Points — Developer Access Isolation

## Overview

Amazon S3 Access Points provide a dedicated endpoint and policy for accessing objects in an S3 bucket.

They are especially useful when **multiple applications, teams, or developers need different levels of access to the same S3 bucket**.

Instead of putting a large and complicated policy directly on the bucket, we can create separate Access Points and give each Access Point its own permissions.

For example:

```text
                    S3 Bucket
                       |
          +------------+------------+
          |                         |
      dev1ap                      dev2ap
          |                         |
       dev1                         dev2
          |                         |
      dev1/*                     dev2/*
```

In this example:

* `dev1` accesses the bucket through `dev1ap`
* `dev2` accesses the bucket through `dev2ap`
* `dev1` is restricted to the `dev1/` prefix
* `dev2` is restricted to the `dev2/` prefix

---

# When Should We Use S3 Access Points?

S3 Access Points are useful when:

* Multiple teams access the same S3 bucket
* Different applications need different permissions
* You want to isolate prefixes such as `dev1/`, `dev2/`, `application1/`, etc.
* You want separate network controls for different users/applications
* A bucket policy is becoming difficult to manage
* You want a dedicated endpoint for a particular application or team
* You want to restrict access through a VPC Access Point

AWS describes Access Points as named network endpoints attached to S3 buckets that can have distinct permissions and network controls.

---

# Why Use Access Points?

Without Access Points, you might end up with a bucket policy containing many users and prefixes:

```text
S3 Bucket
 |
 +-- dev1 -> dev1/*
 |
 +-- dev2 -> dev2/*
 |
 +-- application1 -> application1/*
 |
 +-- application2 -> application2/*
 |
 +-- analytics -> analytics/*
```

As the number of applications and teams grows, this can become difficult to maintain.

With Access Points:

```text
S3 Bucket
 |
 +-- dev1ap -> dev1/*
 |
 +-- dev2ap -> dev2/*
 |
 +-- analytics-ap -> analytics/*
 |
 +-- application-ap -> application/*
```

Each Access Point can have its own policy and network configuration.

---

# Lab Architecture

For this lab I created two IAM users:

```text
IAM User: dev1
IAM User: dev2
```

I then created two S3 Access Points:

```text
Access Point: dev1ap
Access Point: dev2ap
```

The intended access model is:

```text
dev1
 |
 +--> dev1ap
        |
        +--> dev1/*


dev2
 |
 +--> dev2ap
        |
        +--> dev2/*
```

The underlying S3 bucket is shared.

Example bucket structure:

```text
my-company-bucket/
|
+-- dev1/
|   |
|   +-- Goku.jpg
|   +-- ankit.txt
|
+-- dev2/
    |
    +-- test.txt
    +-- application.log
```

---

# Prerequisites

You need:

* AWS account
* S3 bucket
* IAM users
* AWS CLI
* Access to create S3 Access Points
* Appropriate permissions to configure IAM and S3

Example:

```text
AWS Account ID:
6AAA804AA64296394

Region:
us-east-1
```

For documentation and scripts, I have replaced the account ID with a variable:

```bash
ACCOUNT_ID="YOUR_ACCOUNT_ID"
REGION="us-east-1"
BUCKET="YOUR_BUCKET_NAME"
```

---

# Step 1 — Create the IAM Users

Create two IAM users:

```text
dev1
dev2
```

Example AWS CLI:

```bash
aws iam create-user --user-name dev1
aws iam create-user --user-name dev2
```

For this lab, the users were initially created without an IAM identity policy.

The important concept is that an IAM user does not automatically get permission to access S3 simply because the user exists.

Permissions must come from an appropriate policy.

---

# Step 2 — Create the Access Points

Create one Access Point for each developer.

```text
dev1ap
dev2ap
```

Example:

```bash
aws s3control create-access-point \
  --account-id "$ACCOUNT_ID" \
  --name dev1ap \
  --bucket "$BUCKET"
```

And:

```bash
aws s3control create-access-point \
  --account-id "$ACCOUNT_ID" \
  --name dev2ap \
  --bucket "$BUCKET"
```

An S3 Access Point is associated with one S3 general-purpose bucket.

---

# Step 3 — Access Point ARN

For `dev1ap`, the Access Point ARN looks like:

```text
arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap
```

For object operations, the Access Point ARN includes `/object/`.

For example:

```text
arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/object/dev1/*
```

This distinction is important.

## Access Point resource

```text
arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap
```

## Object resource

```text
arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/object/dev1/*
```

AWS documents this `/object/` form for object operations through Access Points.

---

# Step 4 — Configure the dev1 Access Point Policy

The goal is:

```text
dev1 -> dev1ap -> dev1/*
```

Example Access Point policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Dev1FullAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:user/dev1"
      },
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap",
        "arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/object/dev1/*"
      ]
    }
  ]
}
```

### Important

I used:

```json
"Action": "s3:*"
```

instead of:

```json
"Action": "*"
```

because `s3:*` means all S3 actions rather than all AWS service actions.

However, not every S3 API operation is supported through Access Points, so `s3:*` does not mean every possible AWS operation. AWS maintains a list of supported S3 operations.

---

# Step 5 — Configure the dev2 Access Point Policy

For `dev2`, create a similar policy but change the user, Access Point, and prefix.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Dev2FullAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:user/dev2"
      },
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev2ap",
        "arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev2ap/object/dev2/*"
      ]
    }
  ]
}
```

The resulting design is:

```text
dev1
 |
 +--> dev1ap
       |
       +--> dev1/*


dev2
 |
 +--> dev2ap
       |
       +--> dev2/*
```

---

# Step 6 — Important: Underlying Bucket Policy

This was the important issue I have discovered while troubleshooting the `403 Forbidden` error.

An Access Point policy does not automatically override the underlying S3 bucket policy.

For general-purpose S3 buckets, AWS states that permissions granted through an Access Point are effective only when the underlying bucket also permits the access. You can either:

1. Add equivalent permissions to the bucket policy, or
2. Delegate bucket access control to the Access Points.

AWS recommends delegating access control to Access Points for use cases where access is intended to be controlled through Access Points.

---

# Step 7 — Delegate Bucket Access Control to Access Points

A bucket policy can delegate access control to Access Points owned by the bucket owner's account.

Example:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "*",
      "Resource": [
        "arn:aws:s3:::YOUR_BUCKET_NAME",
        "arn:aws:s3:::YOUR_BUCKET_NAME/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:DataAccessPointAccount": "ACCOUNT_ID"
        }
      }
    }
  ]
}
```

This means the bucket delegates access control to Access Points owned by the specified account.

The actual user restrictions are then handled by the Access Point policies.

AWS provides this delegation model as a recommended approach when bucket access is intended to be controlled through Access Points.

---

# Step 8 — IAM User Policies

For this lab, I wanted to understand whether the users could operate without identity-based S3 policies.

The intended design is:

```text
dev1
 |
 | No S3 identity policy
 v
dev1ap
 |
 | Access Point policy
 v
S3 bucket
```

and:

```text
dev2
 |
 | No S3 identity policy
 v
dev2ap
 |
 | Access Point policy
 v
S3 bucket
```

The important requirement is that the resource-based Access Point and bucket authorization must be correctly configured.

If you instead attach an IAM identity policy, remember that S3 authorization is evaluated across the relevant policies. A broad identity policy can make the user's access wider than the intended Access Point restriction.

---

# Step 9 — Configure AWS CLI Credentials

Configure credentials for `dev1`:

```bash
aws configure --profile dev1
```

Then configure `dev2`:

```bash
aws configure --profile dev2
```

Verify the identity:

```bash
aws sts get-caller-identity --profile dev1
```

Expected result should identify:

```text
arn:aws:iam::ACCOUNT_ID:user/dev1
```

For dev2:

```bash
aws sts get-caller-identity --profile dev2
```

---

# Step 10 — Upload Through dev1 Access Point

Suppose we have:

```text
ankit.txt
```

Upload it to the `dev1/` prefix:

```bash
aws s3 cp ankit.txt \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/ankit.txt \
--profile dev1
```

The object should appear in the underlying bucket as:

```text
dev1/ankit.txt
```

The request is going through:

```text
dev1
  |
  v
dev1ap
  |
  v
S3 bucket
  |
  v
dev1/ankit.txt
```

---

# Step 11 — Download Through dev1 Access Point

Suppose the bucket contains:

```text
dev1/Goku.jpg
```

Download it:

```bash
aws s3 cp \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/Goku.jpg \
goku123.jpg \
--profile dev1
```

The downloaded file will be:

```text
goku123.jpg
```

---

# Step 12 — Why I Got 403 HeadObject

During testing I received:

```text
fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
```

The command was similar to:

```bash
aws s3 cp \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/Goku.jpg \
goku123.jpg
```

The important part of the error was:

```text
HeadObject
```

When the AWS CLI performs an S3 copy/download, it can first perform metadata operations such as `HeadObject`.

Therefore, having an Access Point policy alone does not guarantee success.

The underlying bucket must also permit the request, or bucket access must be delegated to the Access Point.

This was the key lesson from the troubleshooting process.

---

# Step 13 — Test HeadObject Directly

We can test the object directly:

```bash
aws s3api head-object \
  --bucket arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap \
  --key dev1/Goku.jpg \
  --profile dev1
```

If authorization is correct, AWS returns object metadata.

If authorization is incorrect, you may receive:

```text
403 Forbidden
```

This is useful for separating an S3 authorization problem from an AWS CLI copy problem.

---

# Step 14 — Test dev1 Access

Upload:

```bash
aws s3 cp ankit.txt \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/ankit.txt \
--profile dev1
```

Download:

```bash
aws s3 cp \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/Goku.jpg \
goku123.jpg \
--profile dev1
```

List objects:

```bash
aws s3 ls \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/ \
--profile dev1
```

Delete an object:

```bash
aws s3 rm \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/ankit.txt \
--profile dev1
```

---

# Step 15 — Test dev2 Access

The same operations should be performed through `dev2ap`.

For example:

```bash
aws s3 cp test.txt \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev2ap/dev2/test.txt \
--profile dev2
```

Download:

```bash
aws s3 cp \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev2ap/dev2/test.txt \
test-download.txt \
--profile dev2
```

---

# Step 16 — Test Isolation

This is the most important test.

## dev1 should access dev1/

```text
dev1 -> dev1ap -> dev1/*
```

Expected:

```text
SUCCESS
```

## dev1 should not access dev2/

For example:

```bash
aws s3 ls \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev2/ \
--profile dev1
```

Expected:

```text
Access denied
```

Similarly:

```text
dev2 -> dev2/*
```

but not:

```text
dev2 -> dev1/*
```

---

# Final Architecture

```text
                         S3 BUCKET
                    my-company-bucket
                           |
              +------------+------------+
              |                         |
              |                         |
           dev1ap                     dev2ap
              |                         |
       Access Point Policy       Access Point Policy
              |                         |
            dev1                      dev2
              |                         |
              v                         v
           dev1/*                    dev2/*
              |                         |
              v                         v
       +-------------+           +-------------+
       | Goku.jpg    |           | test.txt    |
       | ankit.txt   |           | app.log     |
       +-------------+           +-------------+
```

---

# Access Point vs Bucket Policy

## Bucket Policy

A bucket policy controls access to the S3 bucket.

Example resource:

```text
arn:aws:s3:::YOUR_BUCKET_NAME
```

or:

```text
arn:aws:s3:::YOUR_BUCKET_NAME/*
```

## Access Point Policy

An Access Point policy controls who can use a particular Access Point and what they can do through it.

Object resource example:

```text
arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/object/dev1/*
```

This allows us to create different access controls for different teams or applications.

---

# Access Point ARN vs Bucket ARN

This is an important concept.

### Bucket ARN

```text
arn:aws:s3:::my-company-bucket
```

### Access Point ARN

```text
arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap
```

### Access Point Object ARN

```text
arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/object/dev1/*
```

Do not mix these ARN formats in policies.

AWS specifically distinguishes bucket-level and object-level resources when configuring Access Point policies.

---

# Security Recommendations

## 1. Follow least privilege

Instead of:

```json
"Action": "s3:*"
```

production environments should normally use only the actions that are required.

For example:

```json
"Action": [
  "s3:GetObject",
  "s3:PutObject"
]
```

---

## 2. Restrict users to their own prefixes

For example:

```text
dev1 -> dev1/*
dev2 -> dev2/*
```

Do not accidentally give:

```text
dev1 -> *
```

if developers should be isolated.

---

## 3. Consider VPC Access Points

Access Points can use a network origin of:

```text
Internet
```

or:

```text
VPC
```

A VPC-restricted Access Point can be useful when applications should access S3 only from a particular VPC.

---

## 4. Keep Block Public Access enabled

S3 Access Points have their own Block Public Access settings. AWS recommends keeping these enabled unless there is a specific reason to change them.

---

## 5. Use IAM roles for applications where possible

For real production workloads, prefer IAM roles over long-lived IAM user access keys for applications running on AWS.

IAM users can still be useful for labs, demonstrations, or specific human-user scenarios.

---

# Troubleshooting Checklist

If you receive:

```text
403 Forbidden
```

check the following.

### 1. Verify the AWS identity

```bash
aws sts get-caller-identity --profile dev1
```

### 2. Check the Access Point policy

Verify:

```text
Principal
Action
Resource
```

### 3. Check the underlying bucket policy

Remember:

```text
Access Point Policy
        +
Bucket authorization
        =
Successful request
```

unless bucket access control has been appropriately delegated to the Access Points.

### 4. Check the object prefix

For dev1:

```text
dev1/*
```

For dev2:

```text
dev2/*
```

### 5. Check Block Public Access

Access Point, bucket, and account-level Block Public Access settings can affect requests.

### 6. Check explicit Deny statements

An explicit:

```json
"Effect": "Deny"
```

can prevent an otherwise allowed request.

### 7. Test HeadObject

```bash
aws s3api head-object \
  --bucket arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap \
  --key dev1/Goku.jpg \
  --profile dev1
```

---

# Key Takeaways

The main concepts learned in this lab are:

1. **S3 Access Points provide separate endpoints and policies for accessing a shared bucket.**

2. **Multiple Access Points can be attached to the same bucket.**

3. **Each Access Point can provide different permissions.**

4. **Access Point policies can restrict users to specific prefixes.**

5. **For object operations, Access Point object resources use:**

```text
accesspoint/<access-point-name>/object/<prefix>/*
```

6. **The underlying bucket authorization must also allow the request, or bucket access should be delegated appropriately to the Access Points.**

7. **An IAM user does not automatically get S3 permissions simply because the user exists.**

8. **`s3:*` means all S3 actions, while `*` is broader and can represent actions across AWS services.**

9. **A `403 HeadObject` error during `aws s3 cp` is often an authorization issue involving the Access Point, bucket, IAM principal, or an explicit deny.**

10. **Access Points are particularly useful for managing access to shared S3 datasets at scale.**

---

# Useful Commands

## Check current identity

```bash
aws sts get-caller-identity --profile dev1
```

## List through Access Point

```bash
aws s3 ls \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/ \
--profile dev1
```

## Upload

```bash
aws s3 cp ankit.txt \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/ankit.txt \
--profile dev1
```

## Download

```bash
aws s3 cp \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/Goku.jpg \
goku123.jpg \
--profile dev1
```

## Delete

```bash
aws s3 rm \
s3://arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap/dev1/ankit.txt \
--profile dev1
```

## HeadObject

```bash
aws s3api head-object \
--bucket arn:aws:s3:us-east-1:ACCOUNT_ID:accesspoint/dev1ap \
--key dev1/Goku.jpg \
--profile dev1
```

---

# References

* AWS S3 Access Point policies:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-points-policies.html

* AWS S3 Access Points:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-points.html

* AWS S3 Access Point creation:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-access-points.html

* AWS S3 bucket policies:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html
