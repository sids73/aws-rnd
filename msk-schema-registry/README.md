# AWS MSK Schema Registry using AWS CDK

This project involves setting up and managing a schema registry for Amazon Managed Streaming for Apache Kafka (MSK). The schema registry helps in managing and enforcing schemas for data streams, ensuring data compatibility and quality.
This project consists of 
a. A 2 AZ VPC with a Private Subnet and a Public Subnet equipped with a NAT Internet Gateway
b. A IAM authentication based MSK Stack
c. A Bastion Host to monitor and debug the MSK setup and interaction
d. A Fargate Cluster used to host the Kafka Producer and Consumer Services
e. A Kafka producer service which produces a "ChatMessage" with a JSON schema registered in the AWS Glue Schema Registry. Messages are serialized using the AWS GlueSchemaRegistryKafkaSerializer and produced on the chat-messages topic
f. A special Kafka consumer service which 'transports' the GlueSchemaRegistryKafkaSerialized original message from the producer to a chat-messages-copy topic. The copy or cloning is "Shallow", which means that the original message is not deserialized and reserialized to the
   'copy' topic. The listener on the chat-messages topic uses the ByteArraySerializer to reproduce the exact bytes of the serialized message to the "copy" topic. No schema look up or validation happens during the copy. There is another listener in this consumer which then
    reads the "copy" topic and deserializes the message using the GlueSchemaRegistryKafkaDeSerializer to interpret the message using the JSON Schema from the Glue Schema registry. This implementation was done to prove out a "Shallow" transport operation between kafka topics

## Features

- Schema versioning and compatibility checks
- Integration with AWS MSK
- RESTful API for schema management
- Support for Avro, JSON, and Protobuf schemas
- Shallow and least expensive replication between Source and Destination Kafka topics (could be same account, cross account, cross cloud, cross data centers)

## Getting Started

To get started with the project, follow the setup instructions provided in the repository.

## Requirements

- AWS account
- AWS MSK cluster
- AWS CLI configured

## Usage

Detailed usage instructions and examples can be found in the documentation.

## Contributing

Contributions are welcome. Please contact me if you have any questions.

## License

This project is licensed under the MIT License.