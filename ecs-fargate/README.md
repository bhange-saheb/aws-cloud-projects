# 🐍 Neon Snake Game — AWS ECS Fargate

A simple **containerized Neon Snake Game** deployed on **Amazon ECS using AWS Fargate**.

This project is created as a hands-on practice project to understand how to deploy a Docker container as a serverless container workload using **Amazon ECS Fargate**.

## 🎮 Project Overview

The application is a lightweight browser-based Snake Game served through **Nginx** inside a Docker container.

The Docker image contains:

* HTML — game structure
* CSS — neon game interface
* JavaScript — game logic
* Nginx Alpine — web server

The container listens on **port 80**.

## 🏗️ Architecture

```text
                  Internet
                     │
                     ▼
              ┌─────────────┐
              │     AWS     │
              │ ECS Fargate │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ ECS Service │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   Fargate   │
              │    Task     │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │    Nginx    │
              │ Neon Snake  │
              │    Game     │
              └─────────────┘
```

If an Application Load Balancer is used:

```text
User
 │
 ▼
Application Load Balancer
 │
 ▼
ECS Service
 │
 ▼
Fargate Task
 │
 ▼
Nginx → Snake Game
```

## 🐳 Docker Image

The application is packaged as a Docker image using `nginx:alpine`.

```dockerfile
FROM nginx:alpine

LABEL maintainer="Ankit Bhange"
LABEL description="Ankit's Neon Snake Game"

RUN apk add --no-cache curl net-tools jq

COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 🚀 Run Locally

Build the image:

```bash
docker build -t snake-game .
```

Run the container:

```bash
docker run -d \
  --name neon-snake \
  -p 8080:80 \
  snake-game
```

Open the game:

```text
http://localhost:8080
```

Check the container:

```bash
docker ps
```

View logs:

```bash
docker logs neon-snake
```

Stop the container:

```bash
docker stop neon-snake
```

## 📦 Push Image to Docker Hub

Tag the image:

```bash
docker tag snake-game ankit2507/neon-snake-game:v1
```

Login:

```bash
docker login
```

Push:

```bash
docker push ankit2507/neon-snake-game:v1
```

The same image can then be used as the container image for the ECS task.

## ☁️ AWS ECS Fargate Deployment

The basic deployment process is:

```text
Dockerfile
    │
    ▼
Docker Image
    │
    ▼
Docker Hub / Amazon ECR
    │
    ▼
ECS Task Definition
    │
    ▼
ECS Service
    │
    ▼
AWS Fargate
    │
    ▼
Snake Game
```

### ECS Components

This project uses the following AWS components:

| Component       | Purpose                                     |
| --------------- | ------------------------------------------- |
| ECS Cluster     | Groups ECS resources                        |
| Fargate         | Runs the container without managing servers |
| Task Definition | Defines the container configuration         |
| ECS Service     | Maintains the desired number of tasks       |
| Security Group  | Controls network access                     |
| VPC/Subnets     | Provides networking                         |
| Load Balancer   | Optional public access to the application   |

## ⚙️ Example Task Definition Configuration

The important container configuration is:

```json
{
  "containerDefinitions": [
    {
      "name": "neon-snake-game",
      "image": "ankit2507/neon-snake-game:v1",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

The exact CPU, memory, networking, IAM roles, and other settings depend on your ECS configuration.

## 🔐 Networking

The Fargate task needs network connectivity through an AWS VPC.

Typical configuration:

```text
VPC
 │
 ├── Public/Private Subnet
 │
 ├── Security Group
 │       │
 │       └── TCP 80
 │
 └── Fargate Task
        │
        └── Container :80
```

If using an Application Load Balancer, allow HTTP traffic from the appropriate source to the load balancer and allow the load balancer to reach the ECS task on port `80`.

## 🔍 Troubleshooting

Check ECS services and tasks:

```bash
aws ecs list-services \
  --cluster <cluster-name>
```

List running tasks:

```bash
aws ecs list-tasks \
  --cluster <cluster-name>
```

Describe a task:

```bash
aws ecs describe-tasks \
  --cluster <cluster-name> \
  --tasks <task-id>
```

For application troubleshooting, check the ECS task logs if **CloudWatch Logs** are configured.

## 🧹 Cleanup

When finished practicing, remove the resources you created to avoid unnecessary AWS charges.

Depending on your setup, this may include:

* ECS Service
* ECS Cluster
* Fargate tasks
* Application Load Balancer
* Target Group
* Security Groups
* VPC resources
* ECR repository/images

## 📚 Learning Objectives

This project is designed to practice:

* Docker containerization
* Docker image creation
* Docker Hub / Amazon ECR
* Amazon ECS
* AWS Fargate
* ECS Task Definitions
* ECS Services
* VPC networking
* Security Groups
* Load Balancers
* Container logs
* Basic AWS CLI usage

## 🎯 Project Goal

The goal of this project is **not to build a complex game**, but to use a simple application to understand the process of taking a Docker container and deploying it to **AWS ECS Fargate**.

```text
Build → Push → Deploy → Run → Access
 🐳      📦       ☁️      🚀      🌐
```

## 👨‍💻 Author

**Ankit Bhange**

A simple project created for learning and practicing Docker and AWS ECS Fargate.
