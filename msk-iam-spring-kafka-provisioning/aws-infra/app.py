#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_infra.bastion_host_stack import BastionHostStack
from aws_infra.fargate_stack import FargateStack
from aws_infra.iam_msk_stack import MskWithIamAuthStack
from aws_infra.network_stack import NetworkStack
from aws_apps.spring_iam_auth_stack import SpringIamAuthStack


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

private_iam_msk = MskWithIamAuthStack(app, 'IamMskStack', vpc=network_stack.vpc, env=env)

fargate_stack = FargateStack(app, 'FargateStack', vpc=network_stack.vpc, env=env, cluster_name='msk-demo')

SpringIamAuthStack(app, "SpringIamAuthStack", fargate=fargate_stack.cluster, env=env, msk_cluster_name='IamExample')

app.synth()
