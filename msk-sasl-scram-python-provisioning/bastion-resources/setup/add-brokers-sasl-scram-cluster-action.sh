#!/bin/bash

CLUSTER_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $CLUSTER_ARN ]; then
  echo "Usage: ./add-brokers-sasl-scram-topic-replication.sh CLUSTER_ARN"
  echo "  CLUSTER_ARN is AWS ARN for MSK"
  exit 1
fi

if [ ! -d kafka ]; then
  echo "Missing local kafka install directory"
  echo "Should run this from same directory that has kafka install directory"
  exit 1
fi

ZK=$(aws kafka describe-cluster --cluster-arn $CLUSTER_ARN --query 'ClusterInfo.ZookeeperConnectString' --output text)

BS=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query BootstrapBrokerStringSaslScram --output text)

BROKER_CN=$(echo $BS | cut -d ":" -f 1 | cut -c 4-1000)

./kafka/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=$ZK --add \
    --allow-principal "User:CN=*$BROKER_CN" \
    --operation ClusterAction \
    --cluster
