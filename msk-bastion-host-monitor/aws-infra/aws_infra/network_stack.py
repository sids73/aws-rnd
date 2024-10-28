from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct

class NetworkStack(Stack):

    vpc: ec2.Vpc
    default_sg: ec2.SecurityGroup

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        self.vpc = ec2.Vpc(
            self, "MyMSKVpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=2, # provides 2 public subnets and 2 private subnets
            nat_gateways=1 
        )
        self.default_sg = ec2.SecurityGroup(
            self, "DefaultSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True
        )
        self.default_sg.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block), 
            ec2.Port.all_traffic(),
            description="Trust intra vpc traffic"
        )