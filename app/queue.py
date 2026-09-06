import json
import pika
from flask import current_app

def publish_job(job_id):
    credentials = pika.PlainCredentials(
        current_app.config["RABBITMQ_USER"],
        current_app.config["RABBITMQ_PASSWORD"],
    )

    parameters = pika.ConnectionParameters(
        host=current_app.config["RABBITMQ_HOST"],
        port=current_app.config["RABBITMQ_PORT"],
        credentials=credentials,
        heartbeat=60,
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    queue_name = current_app.config["RABBITMQ_QUEUE"]

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps({"job_id": job_id}).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )

    connection.close()
