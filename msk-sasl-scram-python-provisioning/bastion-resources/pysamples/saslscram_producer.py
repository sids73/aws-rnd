
import argparse
import random
import socket
import time

from confluent_kafka import Producer


def random_greeting():
  return random.choice([
    "Hello", # English
    "Bonjour", # French
    "Hola", # Spanish
    "Zdravstvute", # Russian
    "Ciao", # Italian
    "Nǐ Hǎo", # Chinese
    "Konnichiwa", # Japanese
    "Hallo", # German
    "Oi", # Portuguese
    "Anyoung", # Korean
    "Ahlan", # Arabic
    "Namaste", # Hindi
    "Shalom", # Hebrew
    "Goedendag" # Dutch
  ])


def publish_greetings(username, password, bootstrap_servers, topic, count=1, sleep=1):
  config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': username,
    'sasl.password': password,
    'client.id': socket.gethostname()
  }
  producer = Producer(config)

  for _ in range(count):
    greeting = random_greeting()
    print(f'Publishing greeting "{greeting}"')

    producer.produce(topic, value=greeting)

    time.sleep(sleep)

  producer.flush()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--username', required=True)
  parser.add_argument('--password', required=True)
  parser.add_argument('--bootstrap-servers', required=True)
  parser.add_argument('--topic', required=True)

  args = parser.parse_args()

  publish_greetings(args.username, args.password, args.bootstrap_servers, args.topic)
