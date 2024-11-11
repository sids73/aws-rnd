from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct


class NetworkStack(Stack):

    vpc: ec2.Vpc
    default_sg: ec2.SecurityGroup

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(
            self,
            "VPC",
            ip_addresses=ec2.IpAddresses.cidr('10.0.0.0/16'),
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=2,
            nat_gateways=1
        )

        self.default_sg = ec2.SecurityGroup(
            self,
            "DefaultSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True
        )
        self.default_sg.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            ec2.Port.all_traffic(),
            description='Trust intra vpc traffic'
        )
