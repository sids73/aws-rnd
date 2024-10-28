import os
from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_iam as iam
)
from constructs import Construct

class BastionHostStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc ,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        bastion = ec2.BastionHostLinux(
            self, "BastionHost",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T2, ec2.InstanceSize.MICRO
            ),
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )
        bastion.role.add_to_principal_policy(
            iam.PolicyStatement(
                actions=["kafka:*", "kafka-cluster:*", "secretsmanager:GetSecretValue", "kms:Decrypt"],
                effect=iam.Effect.ALLOW,
                resources=["*"]
            )
        )
        
        bucket = s3.Bucket(self, "BastionHostBucket")
        bucket.grant_read_write(bastion.role) # Granting read/write access to the bastion host

        src_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'bastion-resources'
        )


        s3deploy.BucketDeployment(
            self, "MskResourcesDeployment",
            sources=[s3deploy.Source.asset(src_dir)],
            destination_bucket=bucket
        )

        CfnOutput(self, "BucketName", value=bucket.bucket_name)
        CfnOutput(self, "CopyMSKResources", value=f"aws s3 cp --recursive s3://{bucket.bucket_name} .", description="Run this command as ec2-user to copy MSK resources to the bastion host")