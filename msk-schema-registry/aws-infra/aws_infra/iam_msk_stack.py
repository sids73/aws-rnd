
from aws_cdk import (
    CfnOutput,
    custom_resources as cr,
    RemovalPolicy,
    Stack,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_msk as msk,
    aws_ssm as ssm
)
from constructs import Construct


class MskWithIamAuthStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, cluster_name='IamExample', brokers=2, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        security_group = ec2.SecurityGroup(
            self,
            'MskSecurityGroup',
            allow_all_outbound=True,
            description='MSK Security Group',
            vpc=vpc
        )
        security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(2181), description='ZooKeeper Connectivity within VPC'
        )
        security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(9098), description='MSK IAM Auth within VPC'
        )
    
        config = msk.CfnConfiguration(
            self,
            'MskConfig',
            name='KafkaConfigOverride',
            server_properties='\n'.join([
                'auto.create.topics.enable=false',
                'unclean.leader.election.enable=false'
            ])
        )

        log_group = logs.LogGroup(
            self, 'MskLogGroup', retention=logs.RetentionDays.THREE_DAYS, removal_policy=RemovalPolicy.DESTROY
        )

        kafka = msk.CfnCluster(
            self,
            'MskCluster',
            cluster_name=cluster_name,
            broker_node_group_info=msk.CfnCluster.BrokerNodeGroupInfoProperty(
                client_subnets=list(map(lambda sn: sn.subnet_id, vpc.public_subnets)),
                instance_type='kafka.t3.small',
                security_groups=[security_group.security_group_id],
                storage_info=msk.CfnCluster.StorageInfoProperty(
                    ebs_storage_info=msk.CfnCluster.EBSStorageInfoProperty(volume_size=10), # 10 GB storage
                )
            ),
            number_of_broker_nodes=brokers,
            kafka_version='2.8.1',
            encryption_info=msk.CfnCluster.EncryptionInfoProperty(
                encryption_in_transit=msk.CfnCluster.EncryptionInTransitProperty(
                    client_broker='TLS',
                    in_cluster=True
                )
            ),
            client_authentication=msk.CfnCluster.ClientAuthenticationProperty(
                sasl=msk.CfnCluster.SaslProperty(iam=msk.CfnCluster.IamProperty(enabled=True))
            ),
            configuration_info=msk.CfnCluster.ConfigurationInfoProperty(
                arn=config.attr_arn,
                revision=config.attr_latest_revision_revision
            ),
            logging_info=msk.CfnCluster.LoggingInfoProperty(
                broker_logs=msk.CfnCluster.BrokerLogsProperty(cloud_watch_logs=msk.CfnCluster.CloudWatchLogsProperty(
                    enabled=True, log_group=log_group.log_group_name
                ))
            )
        )

        urls_resource = cr.AwsCustomResource(
            self,
            'BootstrapUrls',
            on_create=cr.AwsSdkCall(
                service='kafka',
                action='GetBootstrapBrokers',
                parameters={
                'ClusterArn': kafka.attr_arn
                },
                physical_resource_id=cr.PhysicalResourceId.of(f'{cluster_name.lower()}-bootstrap-urls')
            ),
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
              resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
        ))
        ssm.StringParameter(
            self,
            'BootstrapUrlsConfig',
            parameter_name='/config/application/spring.kafka.bootstrap-servers',
            string_value=urls_resource.get_response_field('BootstrapBrokerStringSaslIam')
        )

        CfnOutput(self, 'MskArn', value=kafka.attr_arn)
        CfnOutput(self, 'BootstrapServers', value=urls_resource.get_response_field('BootstrapBrokerStringSaslIam'))
