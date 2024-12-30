#!/bin/bash

if [ ! -d kafka ]; then
  echo "Missing local kafka install directory"
  echo "Should run this from same directory that has kafka install directory"
  exit 1
fi

curl -L "https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.9/aws-msk-iam-auth-1.1.9-all.jar" -o "aws-msk-iam-auth-1.1.9-all.jar"

mv aws-msk-iam-auth-1.1.9-all.jar kafka/libs/aws-msk-iam-auth-1.1.9-all.jar

CLIENT_PROPERTIES_FILE=iam-auth-client.properties

echo "security.protocol=SASL_SSL" > $CLIENT_PROPERTIES_FILE
echo "sasl.mechanism=AWS_MSK_IAM" >> $CLIENT_PROPERTIES_FILE

# add the awsDebugCreds=true to local CLI config for troubleshooting IAM Auth but don't ever
# run with this turned on for a client in a prod env as there will be performance issues
echo "sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required awsDebugCreds=true;" >> $CLIENT_PROPERTIES_FILE
echo "sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler" >> $CLIENT_PROPERTIES_FILE

# set cli tools log level to debug (required to benefit from awsDebugCreds=true)
# sed -i -e 's/WARN/DEBUG/g' kafka/config/tools-log4j.properties
