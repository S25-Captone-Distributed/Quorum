from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
import json
import os
import time

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "container-logs")
ES_HOST = os.getenv("ES_HOST")
ES_API_KEY = os.getenv("ES_API_KEY")
ES_INDEX = os.getenv("ES_INDEX", "container-logs")

# Wait for Kafka to be ready
while True:
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="es-writer"
        )
        break
    except NoBrokersAvailable:
        print("[!] Kafka not available, retrying in 3s...")
        time.sleep(3)

# Connect to Elastic Cloud using API key
es = Elasticsearch(
    ES_HOST,
    api_key=ES_API_KEY
)

print(f"[*] Writing logs from Kafka:{KAFKA_TOPIC} to Elasticsearch:{ES_INDEX}")

for msg in consumer:
    log_entry = msg.value
    es.index(index=ES_INDEX, document=log_entry)