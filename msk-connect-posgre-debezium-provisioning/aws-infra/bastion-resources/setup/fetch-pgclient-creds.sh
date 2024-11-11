#!/bin/bash

SECRET_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ] || [ -z $SECRET_ARN ]; then
  echo "Usage: source fetch-pgclient-creds.sh SECRET_ARN"
  echo "  SECRET_ARN is AWS ARN for Aurora Admin Creds"
  exit 1
fi

SECRET=$(aws secretsmanager get-secret-value --secret-id $SECRET_ARN --query 'SecretString' --output text)

# if missing jq run: sudo yum install jq -y
export PGUSER=$(echo $SECRET | jq -r '.username')
export PGPASSWORD=$(echo $SECRET | jq -r '.password')
export PGHOST=$(echo $SECRET | jq -r '.host')
export PGPORT=$(echo $SECRET | jq -r '.port')

ENV_FILE="$HOME/.env"
echo "export PGUSER=$PGUSER" > $ENV_FILE
echo "export PGPASSWORD=$PGPASSWORD" >> $ENV_FILE
echo "export PGHOST=$PGHOST" >> $ENV_FILE
echo "export PGPORT=$PGPORT" >> $ENV_FILE
chmod 600 $ENV_FILE

echo "Auth creds loaded into environment variables."
echo "Connect by running $ psql"
