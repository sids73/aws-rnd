#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_apps.spring_gsr_consumer_stack import SpringGsrConsumerStack
from aws_apps.spring_gsr_producer_stack import SpringGsrProducerStack
from aws_infra.bastion_host_stack import BastionHostStack
from aws_infra.fargate_stack import FargateStack
from aws_infra.network_stack import NetworkStack
from aws_infra.iam_msk_stack import MskWithIamAuthStack


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
    , description='A VPC with Public and Private Subnets across 2 Availability Zones and 1 NAT Gateway'
)

bastion_host_stack = BastionHostStack(
    app, 'BastionHostStack', env=env, vpc=network_stack.vpc, description='A Bastion Host to manage and monitor the msk cluster'
)

msk_cluster_name = 'GsrIntegrationExample'
private_iam_msk = MskWithIamAuthStack(app, 'IamMskStack',
    vpc=network_stack.vpc,
    env=env,
    cluster_name=msk_cluster_name,
    description='MSK Cluster with IAM Authentication'
)
fargate_stack = FargateStack(app, 'FargateStack',
    vpc=network_stack.vpc,
    env=env,
    cluster_name='msk-demo',
    description='Fargate Cluster to run the ChatMessage Producer and Consumer application services'
)

registry_name = 'msk-course'
producer_stack = SpringGsrProducerStack(app, 'SpringGsrProducerStack',
    fargate=fargate_stack.cluster,
    env=env,
    msk_cluster_name=msk_cluster_name,
    registry_name=registry_name,
    description='Spring Kafka Producer application to send messages to the Chat Messages Kafka Topic based on the JSON Schema in the Glue Schema Registry'
)
consumer_stack = SpringGsrConsumerStack(app, 'SpringGsrConsumerStack',
    fargate=fargate_stack.cluster,
    env=env,
    msk_cluster_name=msk_cluster_name,
    registry_name=registry_name,
    description='Modified Spring Kafka Consumer application to read and shallow copy messages as raw bytes from the Chat Messages Kafka Topic to a Copy Topic and then read from the copy topic based on the JSON Schema in the Glue Schema Registry'
)
consumer_stack.add_dependency(producer_stack)

app.synth()
