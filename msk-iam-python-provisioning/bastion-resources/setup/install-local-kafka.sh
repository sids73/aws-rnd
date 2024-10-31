#!/bin/bash
set -e # exit on error

curl "https://archive.apache.org/dist/kafka/2.8.1/kafka_2.13-2.8.1.tgz" -o "kafka.tgz"

tar -xvzf kafka.tgz

mv kafka_2.13-2.8.1 kafka
