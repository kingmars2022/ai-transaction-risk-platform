import os
import socket
import time

def wait_for(host, port, name, attempts=60):
    for attempt in range(1, attempts + 1):
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"{name} is ready")
                return
        except OSError:
            print(f"Waiting for {name} ({attempt}/{attempts})...")
            time.sleep(2)

    raise RuntimeError(f"{name} did not become ready")

if __name__ == "__main__":
    wait_for(
        os.getenv("POSTGRES_HOST", "postgres"),
        int(os.getenv("POSTGRES_PORT", "5432")),
        "PostgreSQL",
    )
    wait_for(
        os.getenv("RABBITMQ_HOST", "rabbitmq"),
        int(os.getenv("RABBITMQ_PORT", "5672")),
        "RabbitMQ",
    )
