import json
import time
import pika

from app import create_app
from app.extensions import db
from app.ml import predict_risk
from app.models import InferenceJob, Prediction

app = create_app()

def connection_parameters():
    credentials = pika.PlainCredentials(
        app.config["RABBITMQ_USER"],
        app.config["RABBITMQ_PASSWORD"],
    )

    return pika.ConnectionParameters(
        host=app.config["RABBITMQ_HOST"],
        port=app.config["RABBITMQ_PORT"],
        credentials=credentials,
        heartbeat=60,
    )

def process_message(channel, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    job_id = data["job_id"]

    with app.app_context():
        job = db.session.get(InferenceJob, job_id)

        if job is None:
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        try:
            job.status = "processing"
            db.session.commit()

            risk_score = predict_risk(
                job.request_json,
                app.config["MODEL_PATH"],
            )

            prediction = Prediction(
                **job.request_json,
                risk_score=risk_score,
                is_high_risk=risk_score >= app.config["HIGH_RISK_THRESHOLD"],
            )

            db.session.add(prediction)
            db.session.flush()

            job.prediction_id = prediction.id
            job.status = "completed"
            job.error_message = None
            db.session.commit()

            channel.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as exc:
            db.session.rollback()
            job = db.session.get(InferenceJob, job_id)

            if job:
                job.status = "failed"
                job.error_message = str(exc)
                db.session.commit()

            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    queue_name = app.config["RABBITMQ_QUEUE"]

    while True:
        try:
            connection = pika.BlockingConnection(connection_parameters())
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=process_message,
            )

            print(f"Worker listening on queue: {queue_name}")
            channel.start_consuming()

        except KeyboardInterrupt:
            break

        except Exception as exc:
            print(f"RabbitMQ connection failed: {exc}")
            time.sleep(5)

if __name__ == "__main__":
    main()
