#!/bin/bash

# BEFORE RUNNING: edit the reassignment-plan.json file to only include
# the after plan section (bottom half)

CLUSTER_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $CLUSTER_ARN ]; then
  echo "Usage: ./apply-partition-reassignment-plan.sh CLUSTER_ARN BROKER_IDS"
  echo "  CLUSTER_ARN is AWS ARN for MSK Cluster with Iam Auth enabled"
  exit 1
fi

CLIENT_PROPERTIES_FILE=iam-auth-client.properties
if [ ! -f "$CLIENT_PROPERTIES_FILE" ]; then
  echo "Missing client properties file. Can be created via add-local-iam-auth.sh."
  exit 1
fi

PLAN_FILE=reassignment-plan.json
if [ ! -f "$PLAN_FILE" ]; then
  echo "Missing partition reassignment plan file. Can be created via create-partition-reassignment-plan.sh."
  exit 1
fi

BS=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query "BootstrapBrokerStringSaslIam" --output text)

echo "Boostrap Brokers URL: $BS"

./kafka/bin/kafka-reassign-partitions.sh --execute --bootstrap-server $BS \
  --reassignment-json-file $PLAN_FILE \
  --command-config $CLIENT_PROPERTIES_FILE