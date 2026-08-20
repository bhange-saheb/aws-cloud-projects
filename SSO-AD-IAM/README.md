# AWS Managed Microsoft AD + IAM Identity Center

Enterprise Identity & Access Management Project using AWS Managed Microsoft AD, Windows Server, and IAM Identity Center

## Project Overview

This project demonstrates the implementation of an enterprise-style identity and access management solution on AWS using AWS Managed Microsoft AD integrated with AWS IAM Identity Center.

A Windows Server EC2 instance was configured as an administrative workstation, connected to the managed Active Directory domain, and equipped with Remote Server Administration Tools (RSAT) for centralized directory management.

Active Directory users were then integrated with IAM Identity Center, where permission sets were created and assigned to users to provide controlled access to AWS accounts and resources.

### The project demonstrates practical knowledge of:

AWS identity and access management
Microsoft Active Directory
DNS and domain services
Windows Server administration
AWS IAM Identity Center
Role-based access control (RBAC)
Permission sets
Least-privilege access
EC2 networking and security
🎯 Project Objectives

The primary goal was to build a centralized identity solution that allows users to authenticate using Active Directory credentials and access AWS resources through IAM Identity Center.

### Key objectives
Deploy AWS Managed Microsoft AD.
Launch and configure a Windows Server EC2 instance.
Configure DNS for Active Directory domain resolution.
Join the EC2 instance to the managed domain.
Install and configure RSAT for Active Directory administration.
Create and manage users in Active Directory.
Integrate Managed Microsoft AD with IAM Identity Center.
Create IAM Identity Center permission sets.
Assign AWS account access to directory users.
Validate role-based access to AWS resources.
Apply security and least-privilege principles.
🏗️ Architecture
```
                         AWS Cloud
                              │
                              │
                    ┌─────────▼─────────┐
                    │   AWS VPC         │
                    │                   │
                    │  ┌─────────────┐  │
                    │  │ Managed     │  │
                    │  │ Microsoft   │  │
                    │  │ AD          │  │
                    │  │             │  │
                    │  │ Domain      │  │
                    │  │ Controller  │  │
                    │  └──────┬──────┘  │
                    │         │         │
                    │         │ DNS     │
                    │         │         │
                    │  ┌──────▼──────┐  │
                    │  │ Windows     │  │
                    │  │ Server EC2  │  │
                    │  │             │  │
                    │  │ RSAT        │  │
                    │  │ AD Tools    │  │
                    │  └─────────────┘  │
                    │                   │
                    └─────────┬─────────┘
                              │
                              │ Identity
                              ▼
                    ┌────────────────────┐
                    │ IAM Identity       │
                    │ Center             │
                    │                    │
                    │ AD Users / Groups  │
                    │ Permission Sets    │
                    └─────────┬──────────┘
                              │
                              │ Authorization
                              ▼
                    ┌────────────────────┐
                    │    AWS Account     │
                    │                    │
                    │ AWS Resources      │
                    └────────────────────┘

```
### 🛠️ AWS Services & Technologies
Service / Technology	Purpose
AWS Managed Microsoft AD	Managed Active Directory service
Amazon EC2	Windows Server administration workstation
AWS IAM Identity Center	Centralized AWS user access
IAM Permission Sets	Role-based authorization
Amazon VPC	Network isolation
DNS	Active Directory name resolution
Windows Server	Domain administration
RSAT	Active Directory management
Active Directory Users & Computers	User and directory management
## 🚀 Implementation
1. Deploy AWS Managed Microsoft AD

Created an AWS Managed Microsoft AD directory through AWS Directory Service.

Configuration

Example configuration:

Directory Type: AWS Managed Microsoft AD
Domain Name: corp.example.com
NetBIOS Name: CORP
Edition: Standard


The directory was deployed inside the project VPC using appropriate subnets.

After deployment, the directory status was verified as:

Active

Why Managed Microsoft AD?

Using AWS Managed Microsoft AD removes the operational overhead of managing domain controllers while still providing native Microsoft Active Directory functionality.

2. Launch Windows Server EC2

A Windows Server EC2 instance was deployed within the same VPC environment.

The instance was configured to act as an administrative workstation for the Active Directory environment.

Configuration considerations
Windows Server AMI
Appropriate EC2 instance type
Same VPC as Managed Microsoft AD
Appropriate subnet
Security group configuration
RDP access restricted to the administrator's trusted IP
3. Configure DNS

Active Directory relies heavily on DNS for domain discovery and authentication.

The Windows EC2 instance was configured to use the DNS servers provided by AWS Managed Microsoft AD.

Windows Network Configuration was opened using:

Win + R
→ ncpa.cpl


The active network adapter was configured with the directory-provided DNS IP addresses.

DNS verification

The configuration was validated using:

ipconfig /all


DNS resolution was tested with:

nslookup corp.example.com


Successful DNS resolution confirmed that the EC2 instance could locate the Active Directory domain.

4. Join Windows EC2 to the AD Domain

After DNS configuration, the Windows Server instance was joined to the Managed Microsoft AD domain.

Example:

Domain:
corp.example.com


The instance was restarted after the domain join.

Validation

After reboot, the server was verified as a domain member and domain credentials could be used for authentication.

5. Install Remote Server Administration Tools (RSAT)

RSAT was installed on the Windows Server instance using Server Manager.

Installed tools included the Active Directory management components required to administer the domain.

The Active Directory management console was then accessed using:

dsa.msc


This provided centralized management of:

Users
Groups
Computers
Organizational Units
Domain objects
6. Create Active Directory Users

Using Active Directory Users and Computers, directory users were created.

Example:

john.doe
alice.smith
bob.admin


Users were configured with appropriate credentials and directory attributes.

For a production environment, users should be organized into appropriate Organizational Units (OUs) and security groups based on organizational roles.

7. Integrate Active Directory with IAM Identity Center

AWS IAM Identity Center was configured to use the AWS Managed Microsoft AD directory as its identity source.

This allows Active Directory identities to be used for centralized AWS access management.

Identity flow
```
Active Directory
       │
       ▼
IAM Identity Center
       │
       ▼
AWS Account
       │
       ▼
Permission Set
       │
       ▼
AWS Resources
```

This provides a centralized authentication and authorization model rather than managing individual IAM users for workforce access.

8. Create IAM Identity Center Permission Sets

Permission sets were created to define the level of access users receive within AWS accounts.

Example permission sets:

ReadOnlyAccess
EC2Admin
S3ReadOnly
AdministratorAccess


For example, a read-only role can be based on the AWS managed policy:

ReadOnlyAccess


In a production environment, custom permission sets should be designed according to business requirements and the principle of least privilege.

9. Assign Users to AWS Accounts

The Active Directory users were assigned to AWS accounts through IAM Identity Center.

Example:

User:
john.doe

AWS Account:
Production

Permission Set:
ReadOnlyAccess


This creates a controlled relationship between the user's corporate identity and their AWS authorization level.

10. Validate Access

The configuration was tested by signing in through the IAM Identity Center user portal.

The user could see the AWS account and assigned permission set.

Example:

AWS Account
    │
    └── ReadOnlyAccess


The user's access was validated against the permissions defined by the assigned permission set.

This confirmed the complete identity flow:
```
AD User
   ↓
IAM Identity Center
   ↓
Permission Set
   ↓
AWS Account
   ↓
AWS Resources
```
🔐 Security Considerations

Security was considered throughout the implementation.

Network Security
RDP access should be restricted to trusted IP addresses.
Avoid exposing port 3389 to the entire internet.
Use private subnets where appropriate.
Apply security groups according to the principle of least privilege.
Identity Security
Use centralized identities rather than creating individual IAM users for workforce access.
Use groups and permission sets to implement RBAC.
Avoid assigning administrator permissions unless required.
Apply least-privilege access.
Disable/remove unnecessary users and permissions.
Credential Security

Never commit the following to GitHub:

AWS Access Keys
AWS Secret Keys
Active Directory Passwords
EC2 Administrator Passwords
Directory Credentials
Private Keys
Sensitive Configuration


Use AWS Secrets Manager, Systems Manager, IAM roles, or other appropriate mechanisms for sensitive information.

🧪 Validation Checklist

The following validations were performed:

 AWS Managed Microsoft AD deployed
 Windows Server EC2 deployed
 DNS configured on Windows Server
 DNS resolution verified
 Windows Server joined to AD domain
 RSAT installed
 Active Directory Users and Computers configured
 AD users created
 IAM Identity Center integrated with directory
 Permission sets created
 Users assigned to AWS accounts
 User access validated
📊 Skills Demonstrated

This project demonstrates hands-on experience with:

☁️ AWS
Amazon EC2
AWS Managed Microsoft AD
IAM Identity Center
IAM Permission Sets
Amazon VPC
Security Groups
AWS identity management
🪟 Microsoft
Windows Server
Active Directory
Domain Services
DNS
RSAT
Active Directory Users and Computers
Domain joining
🔐 Identity & Security
Identity federation
Role-Based Access Control (RBAC)
Least-privilege access
Centralized authentication
Permission management
Enterprise identity architecture
📸 Screenshots

Screenshots can be added to demonstrate the implementation.

Recommended screenshots:
```

screenshots/
│
├── 01-managed-ad.png
├── 02-ec2-instance.png
├── 03-dns-configuration.png
├── 04-domain-join.png
├── 05-rsat-installation.png
├── 06-active-directory-users.png
├── 07-iam-identity-center.png
├── 08-permission-sets.png
└── 09-user-assignment.png
```

Example:

![AWS Managed Microsoft AD](screenshots/01-managed-ad.png)


Important: Before uploading screenshots, hide account IDs, public IP addresses, usernames, domain credentials, email addresses, and other sensitive information.

📁 Repository Structure
```
aws-managed-ad-iam-identity-center/
│
├── README.md
│
├── screenshots/
│   ├── 01-managed-ad.png
│   ├── 02-ec2-instance.png
│   ├── 03-dns-configuration.png
│   ├── 04-domain-join.png
│   ├── 05-rsat-installation.png
│   ├── 06-active-directory-users.png
│   ├── 07-iam-identity-center.png
│   ├── 08-permission-sets.png
│   └── 09-user-assignment.png
│
└── docs/
    └── architecture.png
```

💡 Real-World Use Case

This architecture can be used as a foundation for organizations that already use Microsoft Active Directory and want to provide employees with centralized access to AWS environments.

Instead of maintaining separate AWS IAM users for every employee, organizations can use their existing directory identities and manage AWS authorization through IAM Identity Center and permission sets.

For example:

                    Corporate Identity
                           │
                           ▼
                    Active Directory
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Developer      Auditor       Admin
             │             │             │
             ▼             ▼             ▼
        Developer       ReadOnly     Administrator
        Permission      Permission   Permission
           Set             Set          Set
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                       AWS Account


This model supports centralized identity management, role-based access, and scalable authorization across AWS environments.

🎓 Key Takeaways

Through this project, I gained practical experience in designing and implementing an AWS-based enterprise identity architecture.

The implementation demonstrates how:

AWS Managed Microsoft AD can provide managed Active Directory services.
Windows Server can be configured as an administrative workstation.
DNS enables Active Directory domain discovery and communication.
RSAT can be used to manage directory resources.
Active Directory users can serve as centralized workforce identities.
IAM Identity Center can provide centralized AWS access.
Permission sets can implement role-based authorization.
Least-privilege principles can be applied to AWS access management.
🚀 Future Improvements

Possible enhancements to this project include:

Implement Active Directory security groups.
Create Organizational Units based on departments.
Implement custom least-privilege permission sets.
Deploy multiple AWS accounts using AWS Organizations.
Implement separate Development, Staging, and Production environments.
Integrate CloudTrail for auditing.
Implement AWS Config for compliance monitoring.
Use AWS Systems Manager instead of public RDP where possible.
Automate infrastructure deployment using Terraform or AWS CloudFormation.
Implement automated user/group provisioning workflows.
👨‍💻 Author

Your Name

Cloud / AWS Enthusiast | Infrastructure | Identity & Access Management

Areas of Interest
AWS
Cloud Infrastructure
Identity & Access Management
Microsoft Active Directory
DevOps
Cloud Security
Infrastructure as Code

⭐ Project Summary

AWS Managed Microsoft AD + IAM Identity Center demonstrates an end-to-end enterprise identity workflow:

```
AWS Managed Microsoft AD
          ↓
     DNS Configuration
          ↓
    Windows EC2 Server
          ↓
       Domain Join
          ↓
         RSAT
          ↓
   Active Directory Users
          ↓
 IAM Identity Center
          ↓
   Permission Sets
          ↓
    AWS Account Access
```

Outcome: A centralized identity and access management architecture that connects Microsoft Active Directory identities with controlled AWS resource access through IAM Identity Center.

*Note screen-shots are not uploaded because services are deleted before README.md was*