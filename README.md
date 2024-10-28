# aws-rnd
**Project 1: ECS Python API with CDK**

This project demonstrates how to deploy a simple Python-based "hello API" to AWS using CDK. The Python API is containerized and deployed in an ECS Fargate Cluster within a VPC that includes:
- 2 public subnets
- 2 private subnets
- An application load balancer
- A NAT gateway with egress only

**Project 2: MSK Bastion Host Monitor**

This project demonstrates how to deploy a VPC with:
- 2 public subnets
- 2 private subnets
- 1 NAT gateway
- 1 Bastion host

The Bastion host serves as a "jump box" to monitor and interact with MSK in future projects. Additionally, this project includes shell scripts to:
- Install Java 11
- Install JQ
- Install local Kafka
- Upgrade the AWS CLI

**Important:** Future MSK projects will use the same CDK stacks. After deploying and using this project, destroy it to avoid conflicts with future projects.

**Project 3: MSK IAM Provisioning**

This project demonstrates how to deploy a VPC with:
- 2 public subnets
- 2 private subnets
- 1 NAT gateway
- 1 Bastion host

The Bastion host serves as a "jump box" to monitor and interact with MSK. Additionally, it installs an MSK cluster in 2 AZs with IAM authentication enabled and other properties as documented in the MSK stack CDK code. This project also includes shell scripts to:
- Install Java 11
- Install JQ
- Install local Kafka
- Upgrade the AWS CLI
- Inject an IAM role on the client
- Set up a test topic on the MSK cluster
