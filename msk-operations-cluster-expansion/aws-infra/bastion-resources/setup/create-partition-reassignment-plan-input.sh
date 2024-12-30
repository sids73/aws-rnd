#!/bin/bash

CLUSTER_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $CLUSTER_ARN ]; then
  echo "Usage: ./create-partition-reassignment-plan-input.sh CLUSTER_ARN"
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

TOPICS_FILE=topics.txt
./kafka/bin/kafka-topics.sh --bootstrap-server $BS --command-config $CLIENT_PROPERTIES_FILE \
  --list > $TOPICS_FILE

N_TOPICS=$(wc -l < topics.txt)

TOPICS_JSON_FILE=topics-to-reassign.json
echo '{"topics":[' > $TOPICS_JSON_FILE

i=1
while read -r line; do
  # skip management topics (if you name your topics starting with _ then this will need modified)
  if [[ $line != _* ]]; then
    # all but last topic needs a comma
    if [[ $i -ne $N_TOPICS ]]; then
      echo " {\"topic\":\"$line\"}," >> $TOPICS_JSON_FILE
    else
     echo " {\"topic\":\"$line\"}" >> $TOPICS_JSON_FILE
    fi
  fi
  ((i++))
done < $TOPICS_FILE

echo ' ],"version":1}' >> $TOPICS_JSON_FILE

echo "Created reassignment input for $N_TOPICS topics in file $TOPICS_JSON_FILE"
