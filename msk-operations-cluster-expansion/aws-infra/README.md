
# Broker Expansion Example

## 1) Deploy Initial Cluster

Deploy the stacks, the initial MSK stack in MskClusterExpansionStack should deploy with 2 brokers.

```
python3 -m venv .venv
source .venv/bin/activate
cdk synth
cdk deploy --all --require-approval=never
```

## 2) Setup Bastion Host and Publish Scaling Data to Cluster 

Publish data to 2 topics, each with 6 partitions spread over the 2 brokers.

A) Log into Bastion Host

Log into the Bastion Host via the SSM Session Manager Connect from AWS Console in Browser.

B) Copy Setup Scripts from S3 Bucket

Switch to the ec2-user and copy the scripts from the S3 bucket created in the Bastion Host stack to the ec2-user home directory. See the Bastion Host stack outputs for the S3 copy command.

```
sudo su - ec2-user
aws s3 cp s3://....
```

C) Install Dependencies

From the Bastion Host shell install JQ, Java, Local Kafka CLI Tools, update the AWS CLI and add IAM Auth Client Properties file.

```
chmod +x setup/*.sh
./setup/install-jq.sh
./setup/install-java.sh
./setup/install-local-kafka.sh
./setup/update-aws-cli.sh
./setup/add-local-iam-auth.sh
```

D) Create Test Topics & Publish Scaling Test Data to MSK

Generate scaling data to create two topics, topicA and topicB, and have data published to it continuously.

```
CLUSTER_ARN=THE_CLUSTER_ARN

TOPIC=topicA
nohup ./generate-scaling-data.sh $CLUSTER_ARN $TOPIC > $TOPIC-nohup.out 2>&1 &

TOPIC=topicB
nohup ./generate-scaling-data.sh $CLUSTER_ARN $TOPIC > $TOPIC-nohup.out 2>&1 &
```

## 3) Expand MSK Cluster from 2 to 4 Brokers

Update the MskClusterExpansionStack to 4 brokers and redeploy.

```
cdk synth
cdk deploy --all --require-approval=never
```

__*** Be sure to check the cluster broker partition count and distribution in CW Metrics Graph ***__

## 4) Reassign Partitions to newly sized Cluster

Log back into the Bastion Host via the SSM Session Manager Connect from AWS Console in Browser and switch to the ec2-user.

A) Collect Topics to Reassign Partitions On

Generate the topics input files (topics.txt and topics-to-reassign.json).

```
./setup/create-partition-reassignment-plan-input.sh $CLUSTER_ARN
```
__*** Inspect topics-to-reassign.json file (check last element of topics array doesn't have comma before closing bracket ***__

B) Generate Reassignment Plan

Generate the reassignment plan file (reassignment-plan.json)

```
./setup/create-partition-reassignment-plan-input.sh $CLUSTER_ARN "1,2,3,4"
```

__*** Update reassignment-plan.json to only include second half of file ***__

C) Execute Reassignment by Applying Reassignment Plan

Apply the topic reassignment plan

```
./setup/apply-partition-reassignment-plan.sh $CLUSTER_ARN 
```


D) Verify the reassignment of partitions

```
./setup/check-partition-reassignment-status.sh $CLUSTER_ARN 
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
