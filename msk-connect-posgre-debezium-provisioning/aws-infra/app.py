#!/usr/bin/env python3
"""
This script sets up and provisions AWS infrastructure using AWS CDK.

Stacks:
- NetworkStack: Sets up the network infrastructure.
- BastionHostStack: Sets up a bastion host within the VPC created by NetworkStack.
- AuroraPgStack: Sets up an Aurora PostgreSQL database within the VPC.
- MskWithIamAuthStack: Sets up an MSK cluster with IAM authentication within the VPC.

Environment variables:
- CDK_DEFAULT_ACCOUNT: AWS account ID.
- CDK_DEFAULT_REGION: AWS region.

Note:
- Uncomment the relevant lines to specify the AWS account and region explicitly.
- Replace placeholders for BOOTSTRAP_SERVERS, DB_HOST, and DB_PORT with actual values.
"""
import os

import aws_cdk as cdk
from aws_infra.bastion_host_stack import BastionHostStack
from aws_infra.network_stack import NetworkStack
from aws_infra.aurorapg_stack import AuroraPgStack
from aws_infra.iam_msk_stack import MskWithIamAuthStack
from aws_infra.msk_connect_cdc_stack import MskConnectCdcStack, WorkerConfig


app = cdk.App()

env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

network_stack = NetworkStack(app, "NetworkStack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    env=env

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

bastion_host_stack = BastionHostStack(
    app, 'BastionHostStack', env=env, vpc=network_stack.vpc
)

aurorapg_stack = AuroraPgStack(app, 'AuroraPgStack', env=env, vpc=network_stack.vpc)

private_iam_msk = MskWithIamAuthStack(app, 'IamMskStack', vpc=network_stack.vpc, env=env)

# aws kafka get-bootstrap-brokers --cluster-arn THE-CLUSTER-ARN
BOOTSTRAP_SERVERS="b-2.iamexample.zp7n5z.c21.kafka.us-east-1.amazonaws.com:9098,b-1.iamexample.zp7n5z.c21.kafka.us-east-1.amazonaws.com:9098"

# aws rds describe-db-clusters --query 'DBClusters[].Endpoint'
DB_HOST="aurorapg.cluster-cbckagegtyxu.us-east-1.rds.amazonaws.com"

# aws rds describe-db-clusters --query 'DBClusters[].Port'
DB_PORT="5432"

cdc_stack = MskConnectCdcStack(app, 'MskConnectCdcStack',
    bootstrap_urls=BOOTSTRAP_SERVERS,
    dbhost=DB_HOST,
    dbport=int(DB_PORT),
    vpc=network_stack.vpc,
    env=env,
    worker_cfg= WorkerConfig(arn="arn:aws:kafkaconnect:us-east-1:173881142689:worker-configuration/ecommerce-cdc-v3/2854f2d0-f3a0-4cbb-8b15-e66427bddedc-2",
                           revision=1)
 )

app.synth()
