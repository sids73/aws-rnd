#!/bin/bash
set -e

SECRET_ARN=$1
if [ "$1" == "-h" ] || [ "$1" = "--help" ]; then
  echo "Usage: ./create-ecommerce-db.sh [SECRET_ARN]"
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

psql --command "CREATE ROLE debezium LOGIN PASSWORD 'D3bezium'"
psql --command "CREATE ROLE developer LOGIN PASSWORD 'Develop3r'"
psql --command "GRANT developer TO postgres"
psql --command "CREATE DATABASE ecommerce OWNER developer"
psql --command "GRANT rds_replication TO debezium"
psql --command "GRANT rds_superuser TO debezium"
psql --command "GRANT ALL PRIVILEGES ON DATABASE ecommerce TO debezium"
psql --command "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO debezium"
# psql --command "SELECT * FROM pg_create_logical_replication_slot('debezium', 'pgoutput')"
# psql --command "SELECT slot_name, plugin, slot_type FROM pg_replication_slots"

# DDL=$(cat <<-EOF
#   CREATE TABLE IF NOT EXISTS customers (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     created TIMESTAMP DEFAULT now()
#   );
#   CREATE TABLE IF NOT EXISTS orders (
#     id SERIAL PRIMARY KEY,
#     customer_id INTEGER NOT NULL,
#     total INTEGER NOT NULL,
#     created TIMESTAMP DEFAULT now(),
#     CONSTRAINT customer_fk FOREIGN KEY (customer_id) 
#       REFERENCES customers(id)
#   );
# EOF
# )
# psql --dbname ecommerce --command "$DDL"

psql --dbname ecommerce --file "$SCRIPT_DIR/create-ecommerce-db.sql"

psql
