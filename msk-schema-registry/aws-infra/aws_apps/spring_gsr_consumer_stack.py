from constructs import Construct
from os import path

from aws_cdk import (
  Aws,
  Stack,
  aws_ecs as ecs,
  aws_iam as iam
)


class SpringGsrConsumerStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            fargate: ecs.Cluster,
            msk_cluster_name: str,
            registry_name='msk-course',
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        task_role = iam.Role(self, 'TaskRole', assumed_by=iam.CompositePrincipal(
            iam.ServicePrincipal(service='ecs-tasks.amazonaws.com'),
            iam.ServicePrincipal(service='ecs.amazonaws.com'),
        ))
        task_role.add_to_policy(iam.PolicyStatement(
            actions=['kafka-cluster:Connect', 'kafka-cluster:AlterCluster', 'kafka-cluster:DescribeCluster'],
            effect=iam.Effect.ALLOW,
            resources=[f'arn:aws:kafka:{Aws.REGION}:{Aws.ACCOUNT_ID}:cluster/{msk_cluster_name}/*']
        ))

        
        task_role.add_to_policy(iam.PolicyStatement(
            actions=['kafka-cluster:*Topic*', 'kafka-cluster:ReadData' , 'kafka-cluster:WriteData'],
            effect=iam.Effect.ALLOW,
            resources=[f'arn:aws:kafka:{Aws.REGION}:{Aws.ACCOUNT_ID}:topic/{msk_cluster_name}/*']
        ))

        task_role.add_to_policy(iam.PolicyStatement(
            actions=['kafka-cluster:AlterGroup', 'kafka-cluster:DescribeGroup'],
            effect=iam.Effect.ALLOW,
            resources=[f'arn:aws:kafka:{Aws.REGION}:{Aws.ACCOUNT_ID}:group/{msk_cluster_name}/*']
        ))
        task_role.add_to_policy(iam.PolicyStatement(
            actions=['glue:GetSchema*'],
            effect=iam.Effect.ALLOW,
            resources=['*']
        ))
        task_role.add_to_policy(iam.PolicyStatement(
            actions=['ssm:GetParameter*'],
            effect=iam.Effect.ALLOW,
            resources=[f'arn:aws:ssm:{Aws.REGION}:{Aws.ACCOUNT_ID}:*']
        ))

        task_def = ecs.FargateTaskDefinition(self, 'TaskDefinition', task_role=task_role)
        task_def.add_container(
            'App',
            logging=ecs.LogDriver.aws_logs(stream_prefix='app'),
            image=ecs.ContainerImage.from_asset(
                directory=path.join(path.dirname(__file__), '..', '..', 'msk-gsr-spring-kafka-consumer')
            ),
            essential=True,
            environment={
                'AWS_REGION': Aws.REGION,
                'KAFKA_TOPICS_COMMON_SETTINGS_REGISTRY_NAME': registry_name,
            },
            port_mappings=[ecs.PortMapping(container_port=8080)],
            health_check=ecs.HealthCheck(
                command=['CMD-SHELL', 'curl -f http://localhost:8080/actuator/health || exit 1']
            )
        )

        ecs.FargateService(
            self,
            'FargateService',
            service_name='msk-gsr-spring-kafka-consumer',
            cluster=fargate,
            task_definition=task_def,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True)
        )