from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
)
from constructs import Construct


class FargateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, cluster_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.cluster = ecs.Cluster(self, 'FargateCluster', vpc=vpc, cluster_name=cluster_name)

        CfnOutput(self, 'FargateClusterName', value=self.cluster.cluster_name)
