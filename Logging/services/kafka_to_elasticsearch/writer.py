from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from elasticsearch import Elasticsearch
import json
import time

# Hardcoded configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "container-logs"
ES_HOST = "https://f2310bb5ff5c4f2a899249e884ff660d.eastus2.azure.elastic-cloud.com"
ES_INDEX = "container-logs"
ES_API_KEY = "ZkNDRXA1WUIxcU5Mc192UExtakY6eVRvck9nZjNwb0VPZG1qTzdXcFBiUQ=="

# Wait for Kafka to be available
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

# Connect to Elasticsearch
es = Elasticsearch(
    ES_HOST,
    api_key=ES_API_KEY,
    headers={"Content-Type": "application/json"}
)

print(f"[*] Writing logs from Kafka:{KAFKA_TOPIC} to Elasticsearch:{ES_INDEX}")

for msg in consumer:
    log_entry = msg.value
    es.index(index=ES_INDEX, document=log_entry)