# services/dashboard_connector/blurb.py
import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "log-stream")

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

print(f"[*] Listening on RabbitMQ queue: {RABBITMQ_QUEUE}")

def callback(ch, method, properties, body):
    service_id = properties.headers.get("service_id", "unknown")
    log_line = body.decode()
    print(f"[{service_id}] {log_line}")

channel.basic_consume(
    queue=RABBITMQ_QUEUE,
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()
