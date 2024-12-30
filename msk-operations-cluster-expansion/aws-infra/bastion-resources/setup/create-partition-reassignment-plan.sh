#!/bin/bash

CLUSTER_ARN=$1
BROKER_IDS=$2
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $CLUSTER_ARN ] || [ -z $BROKER_IDS ]; then
  echo "Usage: ./create-partition-reassignment-plan.sh CLUSTER_ARN BROKER_IDS"
  echo "  CLUSTER_ARN is AWS ARN for MSK Cluster with Iam Auth enabled"
  echo "  BROKER_IDS is command separated list of broker IDS to balance topic partitions across"
  exit 1
fi

CLIENT_PROPERTIES_FILE=iam-auth-client.properties

if [ ! -f "$CLIENT_PROPERTIES_FILE" ]; then
  echo "Missing client properties file. Can be created via add-local-iam-auth.sh."
  exit 1
fi

TOPICS_FILE=topics-to-reassign.json
if [ ! -f "$TOPICS_FILE" ]; then
  echo "Missing topics file. Can be created via create-partition-reassignment-plan-input.sh."
  exit 1
fi

BS=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query "BootstrapBrokerStringSaslIam" --output text)

echo "Boostrap Brokers URL: $BS"

PLAN_FILE=reassignment-plan.json
./kafka/bin/kafka-reassign-partitions.sh --generate --bootstrap-server $BS \
  --topics-to-move-json-file $TOPICS_FILE --broker-list $BROKER_IDS \
  --command-config $CLIENT_PROPERTIES_FILE > $PLAN_FILE