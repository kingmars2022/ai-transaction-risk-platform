from datetime import datetime, timezone
import uuid
from .extensions import db

class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    old_balance = db.Column(db.Float, nullable=False)
    new_balance = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(32), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    is_high_risk = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "old_balance": self.old_balance,
            "new_balance": self.new_balance,
            "transaction_type": self.transaction_type,
            "hour": self.hour,
            "risk_score": round(self.risk_score, 6),
            "is_high_risk": self.is_high_risk,
            "created_at": self.created_at.isoformat(),
        }

class InferenceJob(db.Model):
    __tablename__ = "inference_jobs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String(20), nullable=False, default="queued")
    request_json = db.Column(db.JSON, nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey("predictions.id"), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    prediction = db.relationship("Prediction")

    def to_dict(self):
        return {
            "job_id": self.id,
            "status": self.status,
            "prediction": self.prediction.to_dict() if self.prediction else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
