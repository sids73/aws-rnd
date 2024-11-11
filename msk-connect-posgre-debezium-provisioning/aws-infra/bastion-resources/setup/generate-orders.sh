#!/bin/bash
set -e

SECRET_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ]; then
  echo "Usage: ./generate-orders.sh [SECRET_ARN]"
  echo "  SECRET_ARN optional if .pgpass present, otherwise is AWS ARN for Aurora Admin Creds"
  exit 1
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ENV_FILE="$HOME/.env"

if [ ! -f $ENV_FILE ]; then
  CREDS_FILE="$SCRIPT_DIR/fetch-pgclient-creds.sh"
  if [ ! -f $CREDS_FILE ]; then
    echo "missing $CREDS_FILE"
    exit 1
  fi

  source $CREDS_FILE $SECRET_ARN
else
  source $ENV_FILE
fi

generateOrders() {
  for i in {1..10000}; do
    CUSTOMER_ID=$(shuf --input-range 1-4 --head-count 1)
    TOTAL=$(shuf --input-range 10-1000 --head-count 1)
    SQL="INSERT INTO orders (customer_id, total) VALUES ($CUSTOMER_ID, $TOTAL)"
    echo "Executing: $SQL"
    psql --dbname ecommerce --command "$SQL"
    sleep 10
  done
}

generateOrders
