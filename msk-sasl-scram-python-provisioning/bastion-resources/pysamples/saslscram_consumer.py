
import argparse

from confluent_kafka import Consumer


def consume_greetings(username, password, bootstrap_servers, topic, poll_time=1.0):
  config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': username,
    'sasl.password': password,
    'group.id': 'bastion-host',
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

      print(f'Consumed greeting "{msg.value()}"')

  finally:
    consumer.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--username', required=True)
  parser.add_argument('--password', required=True)
  parser.add_argument('--bootstrap-servers', required=True)
  parser.add_argument('--topic', required=True)

  args = parser.parse_args()

  consume_greetings(args.username, args.password, args.bootstrap_servers, args.topic)
