from pathlib import Path
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    Stack,
    CfnOutput
)
from constructs import Construct

class CdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Create a VPC
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2, # provides 2 public subnets and 2 private subnets
            nat_gateways=1
        )

        # Create an ECS cluster
        cluster = ecs.Cluster(
            self, "MyFargate-Cluster",
            vpc=vpc
        )

        src_path = Path(__file__).parents[2].joinpath("hello-api")

        if not src_path.exists():
            raise ValueError(f"Path {src_path} does not exist")
        else:
            print(f"Path {src_path} exists")
            service = ecs_patterns.ApplicationLoadBalancedFargateService(
                self, "My-Hello-API-Fargate-Service",
                cluster=cluster,
                cpu=256,
                memory_limit_mib=512,
                task_image_options=
                    ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                        image=ecs.ContainerImage.from_asset(str(src_path)),
                        container_name="hello-api-app-container",
                        container_port=8000
                    ),
                    task_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),   
            )
            service.target_group.configure_health_check(
                path="/hello/health"
            )
            CfnOutput(
                self, "hello-endpoint",
                value=f"http://{service.load_balancer.load_balancer_dns_name}/hello/siddhesh"
            )   