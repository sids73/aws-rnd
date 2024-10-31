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
- Install JQ (Don't need this for this project)
- Install local Kafka
- Upgrade the AWS CLI (make sure you run **$source ~/.bash_profile** after running this script)
**Tip : Once you get on the Bastion host shell and assume the ec2-user role (sudo su ec2-user) make sure that you also execute 'cd' to land in the ec2-users home directory. Then copy the resource files from the s3 bucket.**

**Important:** Future MSK projects will use the same CDK stacks. After deploying and using this project, destroy it to avoid conflicts with future projects.

**Project 3: MSK IAM Provisioning with canned Confluent Kafka producer and consumer scripts**

This project demonstrates how to deploy a VPC with:
- 2 public subnets
- 2 private subnets
- 1 NAT gateway
- 1 Bastion host

The Bastion host serves as a "jump box" to monitor and interact with MSK. Additionally the CDK code installs an MSK cluster in 2 AZs with IAM authentication enabled and other properties as documented in the MSK stack CDK code. This project also includes shell scripts to:
- Install Java 11
- Install JQ (Don't need this for this project)
- Install local Kafka
- Upgrade the AWS CLI (make sure you run **$source ~/.bash_profile** after running this script)
- Inject an IAM role on the client
- Set up a test topic on the MSK cluster
**Tip : Once you get on the Bastion host shell and assume the ec2-user role (sudo su ec2-user) make sure that you also execute 'cd' to land in the ec2-users home directory. Then copy the resource files from the s3 bucket.**

**Project 4: MSK IAM Provisioning with custom Python producer and consumer**

This project demonstrates how to deploy a VPC with:
- 2 public subnets
- 2 private subnets
- 1 NAT gateway
- 1 Bastion host with the necessary python scripts for producer and consumer

The Bastion host serves as a "jump box" to monitor and interact with MSK. Additionally the CDK code installs an MSK cluster in 2 AZs with IAM authentication enabled and other properties as documented in the MSK stack CDK code. This project also includes shell scripts to:
- Install Java 11
- Install JQ (Don't need this for this project)
- Install local Kafka
- Upgrade the AWS CLI (make sure you run **$source ~/.bash_profile** after running this script)
- Inject an IAM role on the client
- Set up a test topic on the MSK cluster (chat.messages is the topic of interest in this example)
**Tip : Once you get on the Bastion host shell and assume the ec2-user role (sudo su ec2-user) make sure that you also execute 'cd' to land in the ec2-users home directory. Then copy the resource files from the s3 bucket.**