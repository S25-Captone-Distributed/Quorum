from kafka import KafkaConsumer
import pika
import json
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "container-logs")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "log-stream")

# Set up Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='bridge-consumer'
)

# Set up RabbitMQ Publisher
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

print(f"[*] Bridging logs from Kafka:{KAFKA_TOPIC} to RabbitMQ:{RABBITMQ_QUEUE}")

for msg in consumer:
    data = msg.value
    service_id = data.get("service_id", "unknown")
    log_line = data.get("log", "")
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=log_line,
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={"service_id": service_id}
        )
    )