#!/bin/bash

SECRET_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $SECRET_ARN ]; then
  echo "Usage: ./add-local-sasl-scram-auth.sh SECRET_ARN"
  echo "  SECRET_ARN is AWS ARN for SASL/SCRAM credentials"
  exit 1
fi

SECRET=$(aws secretsmanager get-secret-value --secret-id $SECRET_ARN --query 'SecretString' --output text)

# if missing jq run: sudo yum install jq -y
USERNAME=$(echo $SECRET | jq -r '.username')
PASSWORD=$(echo $SECRET | jq -r '.password')

CLIENT_PROPERTIES_FILE=sasl-scram-auth-client.properties

echo "security.protocol=SASL_SSL" > $CLIENT_PROPERTIES_FILE
echo "sasl.mechanism=SCRAM-SHA-512" >> $CLIENT_PROPERTIES_FILE
echo "sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username=\"$USERNAME\" password='$PASSWORD';" >> $CLIENT_PROPERTIES_FILE
