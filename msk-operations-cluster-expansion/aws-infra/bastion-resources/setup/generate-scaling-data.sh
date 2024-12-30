#!/bin/bash

# for broker count scaling run in background
# TOPIC=topicA
# nohup ./generate-scaling-data.sh $CLUSTER_ARN $TOPIC > $TOPIC-nohup.out 2>&1 &
# TOPIC=topicB
# nohup ./generate-scaling-data.sh $CLUSTER_ARN $TOPIC > $TOPIC-nohup.out 2>&1 &

CLUSTER_ARN=$1
TOPIC=$2
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $CLUSTER_ARN ] || [ -z $TOPIC ]; then
  echo "Usage: ./generate-scaling-data.sh CLUSTER_ARN TOPIC"
  echo "  CLUSTER_ARN is AWS ARN for MSK Cluster with Iam Auth enabled"
  echo "  TOPIC topic to publish data to"
  exit 1
fi

CLIENT_PROPERTIES_FILE=iam-auth-client.properties
if [ ! -f "$CLIENT_PROPERTIES_FILE" ]; then
  echo "Missing client properties file. Can be created via add-local-iam-auth.sh."
  exit 1
fi

BS=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query "BootstrapBrokerStringSaslIam" --output text)

echo "Boostrap Brokers URL: $BS"

./kafka/bin/kafka-topics.sh --bootstrap-server $BS \
  --command-config iam-auth-client.properties \
  --create --topic $TOPIC --partitions 6 --replication-factor 2

generateMessages() {
  for i in {1..10000}; do

    # --throughput 1000 (1000 msg/sec)
    ./kafka/bin/kafka-producer-perf-test.sh --topic $TOPIC \
      --num-records 1000 --record-size 100 --throughput 100 \
      --producer.config iam-auth-client.properties \
      --producer-props bootstrap.servers=$BS acks=all

    sleep 10
  done
}

# To generate data execute the following around 20 times.

generateMessages
