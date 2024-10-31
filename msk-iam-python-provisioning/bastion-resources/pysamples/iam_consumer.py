
import argparse
import os

from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
from confluent_kafka import Consumer


AWS_REGION=os.environ['AWS_REGION']

def oauth_cb(oauth_config):
    return MSKAuthTokenProvider.generate_auth_token(AWS_REGION)


def consume_chats(bootstrap_servers, topic, poll_time=1.0):
  config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'OAUTHBEARER',
    'oauth_cb': oauth_cb,
    'group.id': 'bastion-host-iam',
    'auto.offset.reset': 'earliest'
  }
  consumer = Consumer(config)
  consumer.subscribe([topic])

  try:

    while True:
      msg = consumer.poll(timeout=poll_time)
      if not msg:
        continue
      elif msg.error():
        raise RuntimeError(msg.error())

      print(f'Consumed chat "{msg.value()}"')

  finally:
    consumer.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--bootstrap-servers', required=True)
  parser.add_argument('--topic', required=True)

  args = parser.parse_args()

  consume_chats(args.bootstrap_servers, args.topic)
