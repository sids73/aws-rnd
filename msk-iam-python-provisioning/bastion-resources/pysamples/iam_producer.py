
import argparse
import json
import os
import socket
import time

from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
from confluent_kafka import Producer
from faker import Faker


faker = Faker()


def random_chat():
    return {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "country": faker.country(),
        "statement": faker.paragraph(nb_sentences=2)
    }


AWS_REGION=os.environ['AWS_REGION']

def oauth_cb(oauth_config):
    return MSKAuthTokenProvider.generate_auth_token(AWS_REGION)


def publish_chats(bootstrap_servers, topic, iterations=1, sleep=1):
  config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'OAUTHBEARER',
    'oauth_cb': oauth_cb,
    'client.id': socket.gethostname()
  }
  producer = Producer(config)

  for _ in range(iterations):
    chat = random_chat()
    print(f'Publishing chat "{chat}"')

    producer.produce(topic, value=json.dumps(chat))

    time.sleep(sleep)

  producer.flush()



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--bootstrap-servers', required=True)
  parser.add_argument('--topic', required=True)
  parser.add_argument('--iterations', type=int, default=1, required=False)

  args = parser.parse_args()

  publish_chats(args.bootstrap_servers, args.topic, iterations=args.iterations)
