#!/bin/bash


if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $1 ]; then
  echo "Usage: ./create-ecommerce-cdc-topics.sh CLUSTER_ARN [CLIENT_PROPERTIES_FILE]"
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

CLUSTER_ARN=$1

BS=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query "BootstrapBrokerStringSaslIam" --output text)

echo "Boostrap Brokers URL: $BS"

./kafka/bin/kafka-topics.sh --bootstrap-server $BS --command-config iam-auth-client.properties \
  --create --topic ecommerce-cdc.public.customers

./kafka/bin/kafka-topics.sh --bootstrap-server $BS --command-config iam-auth-client.properties \
  --create --topic ecommerce-cdc.public.orders
