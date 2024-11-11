from aws_cdk import (
    Duration,
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds
)
from constructs import Construct


class AuroraPgStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        cluster = rds.DatabaseCluster(
            self,
            'AuroraPostgres',
            cluster_identifier='aurorapg',
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_14_8
            ),
            parameters={
                'rds.logical_replication': '1'
            },
            writer=rds.ClusterInstance.provisioned('writer',
                publicly_accessible=False,
                instance_type=ec2.InstanceType.of(
                    instance_class=ec2.InstanceClass.T3, instance_size=ec2.InstanceSize.MEDIUM
                )
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            storage_encrypted=True
        )

        cluster.add_rotation_single_user(automatically_after=Duration.days(30))

        cluster.connections.allow_from(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(cluster.cluster_endpoint.port)
        )

        CfnOutput(self, 'ClusterEndpointHostname', value=cluster.cluster_endpoint.hostname)
        CfnOutput(self, 'ClusterEndpointPort', value=f"{cluster.cluster_endpoint.port}")
        CfnOutput(self, 'ClusterSecret', value=cluster.secret.secret_arn)
