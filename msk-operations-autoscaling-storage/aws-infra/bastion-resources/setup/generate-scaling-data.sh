#!/bin/bash

CLUSTER_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $CLUSTER_ARN ]; then
  echo "Usage: ./generate-scaling-data.sh CLUSTER_ARN [CLIENT_PROPERTIES_FILE]"
  echo "  CLUSTER_ARN is AWS ARN for MSK Cluster with Iam Auth enabled"
  echo "  CLIENT_PROPERTIES_FILE optional path to a client propeties file, default is iam-auth-client.properties"
  exit 1
fi

CLIENT_PROPERTIES_FILE=iam-auth-client.properties
if [ ! -z $2 ]; then 
  CLIENT_PROPERTIES_FILE=$2
fi

if [ ! -f "$CLIENT_PROPERTIES_FILE" ]; then
  echo "Missing client properties file. Can be created via add-local-iam-auth.sh."
  exit 1
fi

BS=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query "BootstrapBrokerStringSaslIam" --output text)

echo "Boostrap Brokers URL: $BS"

TOPIC=scaling.messages

./kafka/bin/kafka-topics.sh --bootstrap-server $BS \
  --command-config iam-auth-client.properties \
  --create --topic $TOPIC --partitions 6 --replication-factor 2

generateMessages() {
  for i in {1..10000}; do

    # --throughput 1000 (1000 msg/sec)
    ./kafka/bin/kafka-producer-perf-test.sh --topic $TOPIC \
      --num-records 10000 --record-size 1000 --throughput 1000 \
      --producer.config iam-auth-client.properties \
      --producer-props bootstrap.servers=$BS acks=all

    sleep 10
  done
}

# To generate data execute the following around 20 times.

generateMessages
