#!/bin/bash

CLUSTER_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $CLUSTER_ARN ]; then
  echo "Usage: ./check-partition-reassignment-status.sh CLUSTER_ARN"
  echo "  CLUSTER_ARN is AWS ARN for MSK Cluster with Iam Auth enabled"
  exit 1
fi

CLIENT_PROPERTIES_FILE=iam-auth-client.properties
if [ ! -f "$CLIENT_PROPERTIES_FILE" ]; then
  echo "Missing client properties file. Can be created via add-local-iam-auth.sh."
  exit 1
fi

BS=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query "BootstrapBrokerStringSaslIam" --output text)

echo "Boostrap Brokers URL: $BS"

./kafka/bin/kafka-reassign-partitions.sh --verify --bootstrap-server $BS \
  --reassignment-json-file reassignment-plan.json \
  --command-config $CLIENT_PROPERTIES_FILE