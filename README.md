# aws-rnd
**Project 1 : ecs-python-api-with-cdk**
This project is a demonstrator project that shows how to deploy a simple python based "hello api" to AWS using CDK
The python api is containerized and deployed in an ECS Fargate Cluster in a VPC with 2 public and 2 private subnets
with an application load balancer and NAT gateway with egress only
**Project 2 : msk-bastion-host-monitor**
This project is a demonstrator project that shows how to deploy a VPC with 2 public and 2 private subnets with 1 NAT
gateway and 1 Bastion host. This Bastion host can be used as a "jump box" to monitor and interact with MSK in future
projects. This project also has resources (shell scripts) to install Java 11, JQ, local Kafka and upgrade the AWS CLI
Important : future MSK projects will have the same CDK stacks. Once done with deploying this project and playing with it
destroy it to not have conflicts with the same CDK stacks in future projects!
**Project 3 : msk-iam-provisioning**
This project is a demonstrator project that shows how to deploy a VPC with 2 public and 2 private subnets with 1 NAT
gateway and 1 Bastion host. This Bastion host can be used as a "jump box" to monitor and interact with MSK. It also installs
a MSK cluster in 2 AZs with IAM authentication enabled and other properties as documented in the MSK stack CDK code
This project also has resources (shell scripts) to install Java 11, JQ, local Kafka and upgrade the AWS CLI like the scripts
in Project 2 and also includes scripts to inject an IAM role on the client and setup a test topic on the MSK cluster
