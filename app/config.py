import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://risk:risk@localhost:5432/riskdb",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "risk_jobs")
    MODEL_PATH = os.getenv("MODEL_PATH", "model/risk_model.joblib")
    HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "0.65"))
