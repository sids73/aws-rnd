# Spring with MSK and IAM Auth

### Running Locally

Once an MSK cluster supporting IAM authentication is deployed with publicly exposed brokers add the IAM user credentials of a user [with sufficient permissions to connect to an MSK cluster](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html) to a .env file in the project's root directory. 

```shell
AWS_REGION=DESIRED-REGION
AWS_ACCESS_KEY_ID=DESIRED-ACCESS-KEY-ID
AWS_SECRET_ACCESS_KEY=DESIRED-ACCESS-KEY
SPRING_KAFKA_BOOTSTRAP_SERVERS=MSK-BOOTSTRAP-URLS
```

Build the application container image.

```shell
docker build --tag msk-iam-spring-kafka . 
```

Run the image as a container then watch the logs to ensure that 

```shell
docker run --name msk-iam-spring-kafka --env-file .env msk-iam-spring-kafka
```
