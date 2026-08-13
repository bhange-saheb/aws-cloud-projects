# Amazon S3 Static Website Hosting — Portfolio Website

## Overview

Amazon S3 can host a **static website** directly from an S3 bucket.

A static website consists of files such as:

* HTML
* CSS
* JavaScript
* Images
* Fonts
* Other static assets

For this project, we used Amazon S3 to host a **personal portfolio website**.

The basic architecture is:

```text
                         Internet
                            |
                            v
                     S3 Website Endpoint
                            |
                            v
                    S3 Static Website
                            |
                            v
                    Portfolio Bucket
                            |
          +-----------------+-----------------+
          |                 |                 |
        index.html        css/             images/
                           |
                        style.css
```

---

# When Should We Use S3 Static Website Hosting?

S3 static website hosting is useful when you have a website that does not require a traditional backend server.

Good examples include:

* Personal portfolio
* Resume website
* Documentation website
* Landing page
* Product information website
* Company informational website
* Static blog
* HTML/CSS/JavaScript projects
* Frontend applications that can be deployed as static files

For example:

```text
Portfolio Website
       |
       v
   S3 Bucket
       |
       +-- index.html
       +-- style.css
       +-- script.js
       +-- images/
```

There is no EC2 server required to serve these static files.

---

# Why Use Amazon S3 for a Portfolio?

A portfolio website is a good use case for S3 because it generally contains static content.

Instead of running:

```text
Internet
   |
   v
EC2
   |
   v
Web Server
   |
   v
Portfolio
```

we can use:

```text
Internet
   |
   v
Amazon S3
   |
   v
Portfolio
```

Advantages include:

* No server to maintain
* No operating system patching
* Highly scalable object storage
* Simple deployment
* Pay only for the resources used
* Easy integration with CloudFront
* Easy integration with Route 53
* Good fit for static websites

---

# Project Architecture

The portfolio website uses:

```text
                    User Browser
                         |
                         v
                  S3 Website Endpoint
                         |
                         v
                 Portfolio S3 Bucket
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
    index.html        css/            images/
                         |
                         v
                     style.css
```

Example:

```text
portfolio-bucket/
|
+-- index.html
|
+-- css/
|   |
|   +-- style.css
|
+-- js/
|   |
|   +-- script.js
|
+-- images/
    |
    +-- profile.jpg
    +-- project1.png
    +-- project2.png
```

---

# Prerequisites

You need:

* AWS account
* S3 bucket
* AWS Management Console or AWS CLI
* Static website files

Example files:

```text
index.html
style.css
script.js
images/
```

---

# Step 1 — Create an S3 Bucket

Create an S3 bucket for the portfolio.

Example:

```text
portfolio-mywebsite
```

The bucket name must be globally unique.

Example AWS CLI:

```bash
aws s3 mb s3://portfolio-mywebsite --region us-east-1
```

You can verify it:

```bash
aws s3 ls
```

---

# Step 2 — Prepare the Portfolio

Example project structure:

```text
portfolio/
|
+-- index.html
+-- about.html
+-- projects.html
+-- contact.html
|
+-- css/
|   |
|   +-- style.css
|
+-- js/
|   |
|   +-- script.js
|
+-- images/
    |
    +-- profile.jpg
    +-- project1.png
```

The most important file is:

```text
index.html
```

This will be the default homepage.

---

# Step 3 — Enable Static Website Hosting

Open:

```text
AWS Console
    |
    v
S3
    |
    v
Portfolio Bucket
    |
    v
Properties
    |
    v
Static website hosting
```

Enable:

```text
Static website hosting: Enabled
```

Set:

```text
Index document:
index.html
```

If your website has a custom error page, you can configure:

```text
Error document:
error.html
```

For example:

```text
index.html
error.html
```

---

# Step 4 — Upload Portfolio Files

Using the AWS CLI:

```bash
aws s3 cp ./portfolio/ s3://portfolio-mywebsite/ --recursive
```

Verify:

```bash
aws s3 ls s3://portfolio-mywebsite/
```

You should see something similar to:

```text
2026-08-13  index.html
2026-08-13  about.html
2026-08-13  projects.html
2026-08-13  contact.html
```

And folders:

```text
css/
js/
images/
```

---

# Step 5 — Configure Access

This is one of the most important parts of S3 static website hosting.

A website must be readable by visitors.

Historically, S3 static website endpoints have commonly been configured with public-read access, which requires allowing public access to the website objects.

However, AWS strongly recommends keeping **S3 Block Public Access enabled whenever possible** and using CloudFront with Origin Access Control for a secure production architecture.

For a learning/demo static website using the S3 website endpoint directly, public object access may be required.

---

# Step 6 — Bucket Policy for Public Website Access

For a simple educational/demo setup, a bucket policy can allow public read access to objects.

Example:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadForWebsite",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::portfolio-mywebsite/*"
    }
  ]
}
```

This allows visitors to perform:

```text
s3:GetObject
```

on objects in the portfolio bucket.

It does **not** give visitors permission to:

```text
PutObject
DeleteObject
ListBucket
```

Only object retrieval is allowed.

---

# Important Security Warning

A public bucket policy means that anyone who knows the URL can potentially retrieve objects covered by the policy.

Therefore:

**Never store sensitive information in a public website bucket.**

Do not upload:

```text
passwords
API keys
AWS credentials
.env files
private documents
database credentials
SSH keys
secret configuration files
```

A portfolio bucket should contain only content intended for public viewing.

---

# Step 7 — Check Block Public Access

If your bucket policy gives:

```text
Principal: *
```

but S3 Block Public Access is preventing public access, the website will not work through the public S3 website endpoint.

Check:

```text
S3
 |
 +-- Bucket
      |
      +-- Permissions
            |
            +-- Block public access
```

For a learning lab, you may encounter a setting that prevents the public bucket policy from taking effect.

For production, instead of disabling Block Public Access, use:

```text
CloudFront
    |
    v
S3 private bucket
```

with Origin Access Control.

---

# Step 8 — Find the Website Endpoint

After enabling static website hosting, S3 provides a website endpoint.

It looks similar to:

```text
http://BUCKET_NAME.s3-website-REGION.amazonaws.com
```

For example:

```text
http://portfolio-mywebsite.s3-website-us-east-1.amazonaws.com
```

The exact endpoint is shown in:

```text
S3
 |
 +-- Bucket
      |
      +-- Properties
            |
            +-- Static website hosting
                  |
                  +-- Bucket website endpoint
```

Open the endpoint in a browser.

If everything is configured correctly, your portfolio should load.

---

# Step 9 — Test the Website

Open:

```text
http://YOUR_BUCKET_WEBSITE_ENDPOINT
```

Expected result:

```text
+---------------------------------------+
|                                       |
|           My Portfolio                |
|                                       |
|       About Me                         |
|       Projects                         |
|       Skills                           |
|       Contact                          |
|                                       |
+---------------------------------------+
```

---

# Step 10 — Verify Files

Check the bucket:

```bash
aws s3 ls s3://portfolio-mywebsite/ --recursive
```

Example:

```text
index.html
about.html
projects.html
contact.html
css/style.css
js/script.js
images/profile.jpg
images/project1.png
```

---

# Step 11 — Update the Portfolio

After making changes locally:

```bash
aws s3 cp ./portfolio/ \
s3://portfolio-mywebsite/ \
--recursive
```

Or use:

```bash
aws s3 sync ./portfolio/ s3://portfolio-mywebsite/
```

`sync` is generally more convenient because it synchronizes changed files.

Example:

```bash
aws s3 sync ./portfolio/ s3://portfolio-mywebsite/
```

---

# Step 12 — Delete Files

To remove a specific file:

```bash
aws s3 rm s3://portfolio-mywebsite/about.html
```

To remove a directory/prefix:

```bash
aws s3 rm s3://portfolio-mywebsite/images/ --recursive
```

Be careful with delete commands.

---

# Useful AWS CLI Commands

## List buckets

```bash
aws s3 ls
```

## List website files

```bash
aws s3 ls s3://portfolio-mywebsite/
```

## List everything

```bash
aws s3 ls s3://portfolio-mywebsite/ --recursive
```

## Upload one file

```bash
aws s3 cp index.html s3://portfolio-mywebsite/
```

## Upload complete website

```bash
aws s3 cp ./portfolio/ s3://portfolio-mywebsite/ --recursive
```

## Synchronize website

```bash
aws s3 sync ./portfolio/ s3://portfolio-mywebsite/
```

## Delete a file

```bash
aws s3 rm s3://portfolio-mywebsite/about.html
```

## Delete everything

```bash
aws s3 rm s3://portfolio-mywebsite/ --recursive
```

---

# Troubleshooting

## Problem 1 — 403 Access Denied

If the website returns:

```text
403 Forbidden
```

check:

1. Static website hosting is enabled
2. `index.html` exists
3. Bucket policy allows `s3:GetObject`
4. Block Public Access settings
5. Object ownership settings
6. The requested object actually exists

---

# Problem 2 — 404 Not Found

Check that:

```text
index.html
```

exists in the bucket root.

Run:

```bash
aws s3 ls s3://portfolio-mywebsite/
```

You should see:

```text
index.html
```

If your file is:

```text
website/index.html
```

instead of:

```text
index.html
```

the configured index document may not be found.

---

# Problem 3 — CSS Is Not Loading

Suppose:

```text
index.html
css/style.css
```

Make sure the HTML references the correct path:

```html
<link rel="stylesheet" href="css/style.css">
```

Check that the file exists:

```bash
aws s3 ls s3://portfolio-mywebsite/css/
```

---

# Problem 4 — Images Are Not Loading

Check:

```text
images/profile.jpg
```

and the HTML:

```html
<img src="images/profile.jpg">
```

Linux/S3 paths are case-sensitive.

For example:

```text
profile.jpg
```

is different from:

```text
Profile.jpg
```

---

# Problem 5 — Website Works Locally but Not on S3

A website might work with:

```bash
python3 -m http.server
```

but fail on S3.

Check:

* Relative paths
* File names
* Case sensitivity
* JavaScript API endpoints
* CORS requirements
* Absolute vs relative URLs
* Browser console errors

S3 static hosting provides static content; it does not execute server-side application code.

---

# Static Website vs Dynamic Website

## Static Website

```text
HTML
CSS
JavaScript
Images
```

Can be hosted directly from S3.

Example:

```text
Portfolio
Documentation
Landing Page
Resume
```

## Dynamic Website

A dynamic application may require:

```text
Frontend
    |
    v
Backend/API
    |
    v
Database
```

S3 alone cannot run backend code such as:

```text
PHP
Python
Node.js server
Java
Ruby
```

S3 stores and serves objects; it is not a general-purpose application server.

---

# Recommended Production Architecture

For a learning project, direct S3 static website hosting is useful.

For a production portfolio, a better architecture is:

```text
                         Internet
                            |
                            v
                       Route 53
                            |
                            v
                       CloudFront
                            |
                    Origin Access Control
                            |
                            v
                    Private S3 Bucket
                            |
                            v
                     Portfolio Files
```

Benefits include:

* HTTPS
* CDN caching
* Better performance
* Custom domain
* Better security
* Private S3 bucket
* No need to expose the S3 bucket publicly

AWS recommends using CloudFront with Origin Access Control when you want CloudFront to securely access a private S3 bucket. ([docs.aws.amazon.com](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html?utm_source=chatgpt.com))

---

# Custom Domain

Instead of:

```text
http://bucket-name.s3-website-region.amazonaws.com
```

you can use a custom domain:

```text
https://www.example.com
```

Typical architecture:

```text
User
 |
 v
Route 53
 |
 v
CloudFront
 |
 v
S3
```

You can use:

```text
example.com
www.example.com
```

for your portfolio.

---

# HTTPS

The S3 website endpoint itself is an HTTP website endpoint.

For a production portfolio, use:

```text
HTTPS
```

through CloudFront.

Architecture:

```text
Browser
   |
   | HTTPS
   v
CloudFront
   |
   | Secure origin access
   v
S3
```

This provides a much better production setup than exposing the S3 website endpoint directly.

---

# S3 Website Hosting vs CloudFront + S3

| Feature                   | S3 Website Endpoint                      | CloudFront + S3 |
| ------------------------- | ---------------------------------------- | --------------- |
| Static hosting            | Yes                                      | Yes             |
| HTTPS                     | Not directly through S3 website endpoint | Yes             |
| CDN                       | No                                       | Yes             |
| Custom domain             | Limited setup                            | Yes             |
| Private S3 bucket         | No                                       | Yes             |
| Global performance        | Basic                                    | Excellent       |
| Production recommendation | Basic/demo                               | Recommended     |
| Cost                      | Low                                      | Low to moderate |

---

# Security Best Practices

For a production portfolio:

* Keep S3 Block Public Access enabled
* Keep the S3 bucket private
* Use CloudFront
* Use Origin Access Control
* Use HTTPS
* Use Route 53 for DNS
* Use AWS Certificate Manager for TLS certificates
* Never store secrets in the bucket
* Enable logging where appropriate
* Consider versioning
* Use least-privilege IAM permissions

Recommended architecture:

```text
                    Internet
                       |
                       v
                  Route 53
                       |
                       v
                  CloudFront
                       |
                       v
               Origin Access Control
                       |
                       v
                 Private S3 Bucket
                       |
          +------------+------------+
          |            |            |
       index.html    css/        images/
```

---

# Optional — Enable Versioning

Versioning can protect against accidental overwrites or deletions.

Enable:

```bash
aws s3api put-bucket-versioning \
  --bucket portfolio-mywebsite \
  --versioning-configuration Status=Enabled
```

Check:

```bash
aws s3api get-bucket-versioning \
  --bucket portfolio-mywebsite
```

Expected:

```json
{
    "Status": "Enabled"
}
```

---

# Optional — Enable Encryption

S3 provides server-side encryption for objects.

For example, you can use SSE-S3:

```text
SSE-S3
```

or AWS KMS:

```text
SSE-KMS
```

For a public portfolio, encryption is still useful as a general storage security practice, although it does not make public objects private.

---

# Deployment Workflow

The complete workflow looks like:

```text
Developer
    |
    v
Local Portfolio
    |
    +-- index.html
    +-- CSS
    +-- JavaScript
    +-- Images
    |
    v
AWS CLI
    |
    v
S3 Bucket
    |
    v
Static Website
    |
    v
Visitors
```

A simple deployment command:

```bash
aws s3 sync ./portfolio/ s3://portfolio-mywebsite/
```

---

# What We Learned

This project demonstrates several important AWS concepts:

1. **S3 can host static websites.**

2. **A static website does not require an EC2 server.**

3. **`index.html` is commonly configured as the default index document.**

4. **S3 objects can be uploaded using the AWS CLI.**

5. **`aws s3 sync` is useful for deploying website changes.**

6. **Bucket policies can control access to S3 objects.**

7. **S3 Block Public Access can prevent unintended public exposure.**

8. **S3 website endpoints are useful for learning and simple static sites.**

9. **CloudFront is recommended for a production website requiring HTTPS, CDN delivery, and a private S3 origin.**

10. **Sensitive information should never be stored in a publicly accessible website bucket.**

---

# Final Architecture

## Learning / Basic Setup

```text
                 Internet
                    |
                    v
             S3 Website Endpoint
                    |
                    v
             Public S3 Bucket
                    |
                    v
              Portfolio Files
```

## Production Setup

```text
                     Internet
                        |
                        v
                    Route 53
                        |
                        v
                   CloudFront
                        |
                        v
              Origin Access Control
                        |
                        v
                 Private S3 Bucket
                        |
                        v
                Portfolio Website
```

---

# Conclusion

Amazon S3 Static Website Hosting is a simple and effective way to learn how AWS serves static content.

For a personal portfolio, it provides an easy starting point:

```text
Create Bucket
     ↓
Upload Portfolio
     ↓
Enable Static Website Hosting
     ↓
Configure Access
     ↓
Open Website Endpoint
```

As the project becomes more production-oriented, the architecture can be upgraded to:

```text
Route 53
    ↓
CloudFront
    ↓
Origin Access Control
    ↓
Private S3 Bucket
```

This provides a more secure and scalable architecture while keeping S3 as the storage layer for the portfolio.

---

# Useful AWS Documentation

* S3 static website hosting:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html

* S3 bucket policies:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html

* S3 Block Public Access:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html

* CloudFront with S3:
  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.SimpleDistribution.html

* CloudFront Origin Access Control:
  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html
