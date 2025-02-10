from aws_cdk import (
    Aws,
    custom_resources as cr,
    Fn,
    RemovalPolicy,
    Stack,
    Token,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_kafkaconnect as mkc,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployer
)

from base64 import b64encode # IMPORTANT: for properties in the worker configuration you actually have to base64 encode them
from constructs import Construct
from os import path


class ConnectorPlugin:
    def __init__(self, bucket: s3.Bucket, plugin: cr.AwsCustomResource):
        self.bucket = bucket
        self.plugin = plugin

# WorkerConfig is a class that encapsulates the worker configuration. It has three attributes: arn, revision, and custom_resource. Revision is the version of the worker configuration.
# IMPORTANT: A worker configuration is immutable, so you can't update it. If you want to update it, you have to create a new one with a new version. 
# The custom_resource attribute is an AWS custom resource that creates the worker configuration.
class WorkerConfig:
    def __init__(
            self,
            arn: str = None, 
            revision: int = None, 
            custom_resource: cr.AwsCustomResource = None
    ):
        self.arn = arn
        self.revision = revision
        self.custom_resource = custom_resource

    def worker_config_arn(self):
        if self.arn:
            return self.arn
        
        return self.custom_resource.get_response_field("workerConfigurationArn")
    
    def worker_config_revision(self):
        if self.revision:
            return self.revision

        return Token.as_number(self.custom_resource.get_response_field("latestRevision.revision"))

    def empty(self):
        return not any([self.arn, self.revision, self.custom_resource])


class MskConnectCdcStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            vpc: ec2.Vpc,
            dbhost: str,
            dbport: int,
            bootstrap_urls: str,
            worker_cfg: WorkerConfig = None,
            **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        # create plugin and place it in a bucket
        debezium_plugin = self.make_debezium_plugin()
        # debezium_plugin.get_response_field("customPluginArn"),
        # debezium_plugin.get_response_field("revision")

        # create connector role
        role = self.make_connector_role()
        debezium_plugin.bucket.grant_read(role)

        # create worker configuration
        if worker_cfg is None or worker_cfg.empty():
            worker_cfg = self.make_worker_config(version=5)

        # create connector
        connector = self.make_connector(
            debezium_plugin, worker_cfg, role, vpc, bootstrap_urls, dbhost, dbport
        )
        connector.node.add_dependency(debezium_plugin.plugin)

    def make_debezium_plugin(self) -> ConnectorPlugin:
        bucket = s3.Bucket(self, 'PluginBucket', removal_policy=RemovalPolicy.DESTROY)

        plugin_path = path.join(
            path.dirname(path.abspath(__file__)), 'resources', 'debezium-connector-postgres.zip'
        )

        plugin_resource = s3_deployer.BucketDeployment(self, 'PluginBucketDeployer',
            sources=[s3_deployer.Source.asset(plugin_path)],
            destination_bucket=bucket,
            extract=False,
            prune=False,
            retain_on_delete=False
        )

        plugin = cr.AwsCustomResource(self, 'DebeziumPlugin',
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                  effect=iam.Effect.ALLOW,
                  actions=["s3:Get*", "s3:List*"],
                  resources=[bucket.bucket_arn, f"{bucket.bucket_arn}/*"]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["kafkaconnect:CreateCustomPlugin"],
                    resources=[f"arn:aws:kafkaconnect:{Aws.REGION}:{Aws.ACCOUNT_ID}:custom-plugin/*"]
                )
            ]),
            on_create=cr.AwsSdkCall(
                service="KafkaConnect",
                action="createCustomPlugin",
                physical_resource_id=cr.PhysicalResourceId.from_response("customPluginArn"),
                parameters={
                    "contentType": "ZIP",
                    "location": {
                        "s3Location": {
                            "bucketArn": bucket.bucket_arn,
                            "fileKey": Fn.select(0, plugin_resource.object_keys)
                        }
                    },
                    "name": "debezium-postgres",
                    "description": "Debezium Connector for PostgreSQL"
                }
            )
        )

        plugin_cleanup = cr.AwsCustomResource(self, 'DebeziumPluginCleanup',
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["kafkaconnect:DeleteCustomPlugin"],
                    resources=[f"arn:aws:kafkaconnect:{Aws.REGION}:{Aws.ACCOUNT_ID}:custom-plugin/*"]
                )
            ]),
            on_delete=cr.AwsSdkCall(
                service="KafkaConnect",
                action="deleteCustomPlugin",
                parameters={
                    "customPluginArn": plugin.get_response_field("customPluginArn")
                }
            )
        )
        plugin_cleanup.node.add_dependency(plugin)

        return ConnectorPlugin(bucket, plugin)

    def make_connector_role(self) -> iam.Role:
        role = iam.Role(self, "DebeziumRole", 
          assumed_by=iam.ServicePrincipal("kafkaconnect.amazonaws.com")
        )
        role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["kafka:Get*", "kafka:Describe*", "kafka:List*", "kafka:Update*", "kafka:Create*",
                     "kafka-cluster:Connect", "kafka-cluster:Alter*", "kafka-cluster:Describe*", "kafka-cluster:Write*", "kafka-cluster:Create*", "kafka-cluster:Read*"],
            resources=[
                f"arn:aws:kafka:{Aws.REGION}:{Aws.ACCOUNT_ID}:*",
                f"arn:aws:kafkaconnect:{Aws.REGION}:{Aws.ACCOUNT_ID}:*"
            ]
        ))
        role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["secretsmanager:GetResourcePolicy", "secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret", "secretsmanager:ListSecretVersionIds"],
            resources=[
                f"arn:aws:secretsmanager:{Aws.REGION}:{Aws.ACCOUNT_ID}:secret:application/debezium_postgre_kafka_sink-JRgqTc"
            ]
        ))
        return role

    # because WorkerConfigurations cannot be deleted then you might want to
    # create subsequent ones with a version suffix
    # A WorkerConfiguration is a set of properties that are used to configure the worker nodes in a Kafka Connect cluster. 
    # It is equivalent to a kafka worker.properties file.
    def make_worker_config(self, version=1) -> WorkerConfig:
        # IMPORTANT!
        # set offset.storage.topic so you can restart and redeploy connectors
        # has to be set at the worker config level not connector config
        props = '\n'.join([
          "offset.storage.topic=ecommerce-cdc",
          "key.converter=org.apache.kafka.connect.json.JsonConverter",
          "value.converter=org.apache.kafka.connect.json.JsonConverter",
          "config.providers=secretsmanager",
          "config.providers.secretsmanager.class=com.amazonaws.kafka.config.providers.SecretsManagerConfigProvider"
         # "config.providers.secretsmanager.param.region=us-east-1"
        ])

        worker_cfg = cr.AwsCustomResource(
            self,
            'DebeziumWorkerConfig',
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["kafkaconnect:CreateWorkerConfiguration"],
                    resources=["*"]
                )
            ]),
            on_create=cr.AwsSdkCall(
                service="KafkaConnect",
                action="createWorkerConfiguration",
                physical_resource_id=cr.PhysicalResourceId.from_response("workerConfigurationArn"),
                parameters={
                    "name": f"ecommerce-cdc-v{version}",
                    "description": "Ecommerce Aurora PostgreSQL Debezium CDC Configuration",
                    "propertiesFileContent": b64encode(props.encode()).decode()
                }
            )
        )
        return WorkerConfig(custom_resource=worker_cfg)

    def make_connector(
            self,
            custom_plugin: ConnectorPlugin,
            worker_cfg: WorkerConfig,
            role: iam.Role,
            vpc: ec2.Vpc,
            bootstrap_urls: str,
            dbhost: str,
            dbport = 5432,
    ) -> mkc.CfnConnector:
        sg = ec2.SecurityGroup(self, "SecurityGroup", vpc=vpc)

        log_group = logs.LogGroup(self, 'ConnectorLogs',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.THREE_DAYS
        )

        connector = mkc.CfnConnector(self, 'DebeziumConnector',
            connector_name="ecommerce-cdc",
            capacity=mkc.CfnConnector.CapacityProperty(
                provisioned_capacity={ "mcuCount": 2, "workerCount": 1 }
            ),
            connector_configuration={
              "tasks.max": "1",# number of tasks
              "connector.class": "io.debezium.connector.postgresql.PostgresConnector", # connector class 
              "plugin.name": "pgoutput", # plugin name
              "slot.name": "debezium", # logical replication slot
              "name": "ecommerce-cdc", # name of the connector
              "database.dbname": "ecommerce",
              "database.hostname": "${secretsmanager:application/debezium_postgre_kafka_sink:host}", # reference to the secret in secrets manager containing the hostname
              "database.port": "${secretsmanager:application/debezium_postgre_kafka_sink:port}",
              "topic.prefix": "ecommerce-cdc", # prefix for the topics
              "schema.include.list": "public", # comma-separated list of schemas to include
              "table.include.list": "public.customers,public.orders", # comma-separated list of tables to include
              "database.user": "${secretsmanager:application/debezium_postgre_kafka_sink:username}",  # database user
              "database.password": "${secretsmanager:application/debezium_postgre_kafka_sink:password}", # reference to the secret in secrets manager containing the password
            },
            connector_description="Debezium Aurora Postgres for Ecommerce Change Data Capture",
            kafka_cluster=mkc.CfnConnector.KafkaClusterProperty(
                apache_kafka_cluster=mkc.CfnConnector.ApacheKafkaClusterProperty(
                    bootstrap_servers=bootstrap_urls,
                    vpc={
                        "securityGroups": [sg.security_group_id],
                        "subnets": [sn.subnet_id for sn in vpc.private_subnets]
                    }
                )
            ),
            kafka_connect_version="3.7.x",
            service_execution_role_arn=role.role_arn,
            plugins=[mkc.CfnConnector.PluginProperty(
                custom_plugin={
                    "customPluginArn": custom_plugin.plugin.get_response_field("customPluginArn"),
                    "revision": Token.as_number(custom_plugin.plugin.get_response_field("revision"))
                }
            )],
            kafka_cluster_client_authentication={
                "authenticationType": "IAM"
            },
            kafka_cluster_encryption_in_transit={
                "encryptionType": "TLS"
            },
            log_delivery=mkc.CfnConnector.LogDeliveryProperty(
                worker_log_delivery=mkc.CfnConnector.WorkerLogDeliveryProperty(
                    cloud_watch_logs=mkc.CfnConnector.CloudWatchLogsLogDeliveryProperty(
                        enabled=True,
                        log_group=log_group.log_group_name
                    )
                )
            ),
            worker_configuration=mkc.CfnConnector.WorkerConfigurationProperty(
                worker_configuration_arn=worker_cfg.worker_config_arn(),
                revision=worker_cfg.worker_config_revision()
            )
        )
        return connector
