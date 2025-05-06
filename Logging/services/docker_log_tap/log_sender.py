# services/docker_log_tap/log_sender.py

import json, os, time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = os.environ["KAFKA_BROKER"]
KAFKA_TOPIC = os.environ["KAFKA_TOPIC"]

producer = None
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("✅ Connected to Kafka.")
        break
    except NoBrokersAvailable:
        print("⏳ Kafka not ready yet, retrying...")
        time.sleep(3)

if not producer:
    raise RuntimeError("❌ Kafka not available after 10 retries")

# dummy infinite log loop
i = 0
while True:
    log = {"log": f"🔥 generated test log {i}", "source": "docker_log_tap"}
    producer.send(KAFKA_TOPIC, log)
    print(f"📤 Sent: {log}")
    time.sleep(5)
    i += 1